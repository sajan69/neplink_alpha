from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import FriendRequest, Friendship
from .serializers import FriendRequestSerializer, FriendshipSerializer
from accounts.models import User
from accounts.services import NotificationService
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class FriendViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['friend__username', 'friend__email']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Friendship.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Get friend list",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search friends by username or email", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order results by created_at", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Send friend request",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'to_user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID to send friend request to'),
            },
            required=['to_user_id']
        )
    )
    @action(detail=False, methods=['post'])
    def send_friend_request(self, request):
        to_user_id = request.data.get('to_user_id')
        to_user = User.objects.get(id=to_user_id)
        friend_request, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
        if created:
            NotificationService.send_notification_to_userids('Friend Request', f'{request.user.username} sent you a friend request.', [to_user.id], '/friends/requests/')
            return Response({'message': 'Friend request sent'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Friend request already sent'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Accept friend request",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'request_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Friend request ID to accept'),
            },
            required=['request_id']
        )
    )
    @action(detail=False, methods=['post'])
    def accept_friend_request(self, request):
        request_id = request.data.get('request_id')
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        Friendship.objects.create(user=request.user, friend=friend_request.from_user)
        Friendship.objects.create(user=friend_request.from_user, friend=request.user)
        friend_request.delete()
        return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Reject friend request",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'request_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Friend request ID to reject'),
            },
            required=['request_id']
        )
    )
    @action(detail=False, methods=['post'])
    def reject_friend_request(self, request):
        request_id = request.data.get('request_id')
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        friend_request.delete()
        return Response({'message': 'Friend request rejected'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Remove friend",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'friend_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID of friend to remove'),
            },
            required=['friend_id']
        )
    )
    @action(detail=False, methods=['post'])
    def remove_friend(self, request):
        friend_id = request.data.get('friend_id')
        Friendship.objects.filter(user=request.user, friend_id=friend_id).delete()
        Friendship.objects.filter(user_id=friend_id, friend=request.user).delete()
        return Response({'message': 'Friend removed'}, status=status.HTTP_200_OK)

class FriendRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user)

    @swagger_auto_schema(
        operation_description="Get friend requests",
        manual_parameters=[
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order results by created_at", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)