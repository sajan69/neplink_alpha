from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ChatRoom, Message, CallLog
from .serializers import ChatRoomSerializer, MessageSerializer, CallLogSerializer
from accounts.models import User
from friends.models import Friendship
from django.shortcuts import get_object_or_404
from agora_token_builder import RtcTokenBuilder
import random
import time
from decouple import config
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_group_chat']
    search_fields = ['name']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)

    @swagger_auto_schema(
        operation_description="Create or open a private chat",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'friend_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID of the friend to chat with'),
            },
            required=['friend_id']
        ),
        responses={201: ChatRoomSerializer()}
    )
    @action(detail=False, methods=['post'])
    def create_or_open_private_chat(self, request):
        friend_id = request.data.get('friend_id')
        friend = get_object_or_404(User, id=friend_id)
        if not Friendship.objects.filter(user=request.user, friend=friend).exists():
            return Response({'error': 'You can only chat with your friends.'}, status=status.HTTP_400_BAD_REQUEST)

        room = ChatRoom.objects.filter(participants=request.user).filter(participants=friend).filter(is_group_chat=False).first()
        if not room:
            room_name = f"{request.user.username} - {friend.username}"
            room = ChatRoom.objects.create(is_group_chat=False, name=room_name)
            room.participants.add(request.user, friend)
        
        serializer = self.get_serializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Create a group chat",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the group chat'),
                'participant_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='List of user IDs to add to the group chat'),
            },
            required=['name', 'participant_ids']
        ),
        responses={201: ChatRoomSerializer()}
    )
    @action(detail=False, methods=['post'])
    def create_group_chat(self, request):
        name = request.data.get('name')
        participant_ids = request.data.get('participant_ids', [])
        
        if name and participant_ids:
            room = ChatRoom.objects.create(name=name, is_group_chat=True)
            room.participants.add(request.user)
            
            for participant_id in participant_ids:
                friend = get_object_or_404(User, id=participant_id)
                if Friendship.objects.filter(user=request.user, friend=friend).exists():
                    room.participants.add(friend)
            
            serializer = self.get_serializer(room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': 'Please provide a name and participant IDs.'}, status=status.HTTP_400_BAD_REQUEST)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp']

    def get_queryset(self):
        return Message.objects.filter(room__participants=self.request.user)

    def perform_create(self, serializer):
        room = serializer.validated_data['room']
        if not room.participants.filter(id=self.request.user.id).exists():
            raise permissions.PermissionDenied("You don't have access to this chat room.")
        serializer.save(sender=self.request.user)

class CallLogViewSet(viewsets.ModelViewSet):
    queryset = CallLog.objects.all()
    serializer_class = CallLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'call_type']
    ordering_fields = ['start_time']

    def get_queryset(self):
        return CallLog.objects.filter(room__participants=self.request.user)

    @swagger_auto_schema(
        operation_description="Initiate a call",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'room_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the chat room'),
                'call_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of call (audio/video)'),
            },
            required=['room_id', 'call_type']
        ),
        responses={201: CallLogSerializer()}
    )
    @action(detail=False, methods=['post'])
    def initiate_call(self, request):
        room_id = request.data.get('room_id')
        call_type = request.data.get('call_type')
        
        room = get_object_or_404(ChatRoom, id=room_id)
        if not room.participants.filter(id=request.user.id).exists():
            return Response({'error': "You don't have access to this chat room."}, status=status.HTTP_403_FORBIDDEN)
        
        ongoing_call = CallLog.objects.filter(room=room, status='ongoing').first()
        if ongoing_call:
            return Response({'error': 'Call already ongoing', 'call_log_id': ongoing_call.id}, status=status.HTTP_400_BAD_REQUEST)
        
        call_log = CallLog.objects.create(
            room=room,
            caller=request.user,
            call_type=call_type,
            agora_channel=f"room_{room_id}"
        )
        call_log.participants.add(request.user)
        
        room.active_call = call_log
        room.save()
        
        serializer = self.get_serializer(call_log)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="End a call",
        responses={200: CallLogSerializer()}
    )
    @action(detail=True, methods=['post'])
    def end_call(self, request, pk=None):
        call_log = self.get_object()
        call_log.end_call()
        serializer = self.get_serializer(call_log)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Get Agora token",
        manual_parameters=[
            openapi.Parameter('channel', openapi.IN_QUERY, description="Agora channel name", type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: openapi.Response(
            description="Agora token and related information",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                    'uid': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'app_id': openapi.Schema(type=openapi.TYPE_STRING),
                },
            )
        )}
    )
    @action(detail=False, methods=['get'])
    def get_agora_token(self, request):
        app_id = config('AGORA_APP_ID')
        app_certificate = config('AGORA_APP_CERTIFICATE')
        channel = request.query_params.get('channel')
        uid = random.randint(1, 230)
        expiration_time_in_seconds = 3600
        current_timestamp = int(time.time())
        privilegeExpiredTs = current_timestamp + expiration_time_in_seconds
        role = 1  # 1 for host, 2 for guest

        token = RtcTokenBuilder.buildTokenWithUid(app_id, app_certificate, channel, uid, role, privilegeExpiredTs)

        return Response({'token': token, 'uid': uid, 'app_id': app_id})