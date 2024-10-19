from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Comment, CommentReply, Like, PostMedia, SelectedFriend, UserTagSettings
from .serializers import PostSerializer, CommentSerializer, CommentReplySerializer, LikeSerializer, PostMediaSerializer, SelectedFriendSerializer, UserTagSettingsSerializer
from accounts.services import NotificationService
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['visibility', 'is_hidden', 'is_shared']
    search_fields = ['caption', 'user__username']
    ordering_fields = ['created_at', 'updated_at']

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        files = self.request.FILES.getlist('files')
        for file in files:
            file_type = self.get_file_type(file.name)
            PostMedia.objects.create(post=post, file=file, file_type=file_type)

    @swagger_auto_schema(
        operation_description="Like or unlike a post",
        responses={200: openapi.Response("Post liked/unliked successfully")}
    )
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            return Response({'message': 'Post unliked'}, status=status.HTTP_200_OK)
        if post.user != request.user:
            NotificationService.send_notification_to_userids(
                f"{request.user.username} liked your post",
                f"{request.user.username} liked your post: {post.caption[:50]}...",
                [post.user.id],
                f'/post/{post.id}/'
            )
        return Response({'message': 'Post liked'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Add a comment to a post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, description='Comment text'),
            },
            required=['text']
        ),
        responses={201: CommentSerializer()}
    )
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(user=request.user, post=post)
            if post.user != request.user:
                NotificationService.send_notification_to_userids(
                    f"{request.user.username} commented on your post",
                    f"{request.user.username} commented: {comment.text[:50]}...",
                    [post.user.id],
                    f'/post/{post.id}/'
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Share a post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'caption': openapi.Schema(type=openapi.TYPE_STRING, description='Caption for the shared post'),
            },
            required=['caption']
        ),
        responses={201: PostSerializer()}
    )
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        original_post = self.get_object()
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            shared_post = serializer.save(user=request.user, shared_post=original_post, is_shared=True)
            if original_post.user != request.user:
                NotificationService.send_notification_to_userids(
                    f"{request.user.username} shared your post",
                    f"{request.user.username} shared your post: {original_post.caption[:50]}...",
                    [original_post.user.id],
                    f'/post/{shared_post.id}/'
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_file_type(self, filename):
        # Implement logic to determine file type based on filename or extension
        pass

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']

    @swagger_auto_schema(
        operation_description="Like or unlike a comment",
        responses={200: openapi.Response("Comment liked/unliked successfully")}
    )
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        comment = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, comment=comment)
        if not created:
            like.delete()
            return Response({'message': 'Comment unliked'}, status=status.HTTP_200_OK)
        if comment.user != request.user:
            NotificationService.send_notification_to_userids(
                f"{request.user.username} liked your comment",
                f"{request.user.username} liked your comment: {comment.text[:50]}...",
                [comment.user.id],
                f'/post/{comment.post.id}/'
            )
        return Response({'message': 'Comment liked'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Add a reply to a comment",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, description='Reply text'),
            },
            required=['text']
        ),
        responses={201: CommentReplySerializer()}
    )
    @action(detail=True, methods=['post'])
    def add_reply(self, request, pk=None):
        comment = self.get_object()
        serializer = CommentReplySerializer(data=request.data)
        if serializer.is_valid():
            reply = serializer.save(user=request.user, comment=comment)
            if comment.user != request.user:
                NotificationService.send_notification_to_userids(
                    f"{request.user.username} replied to your comment",
                    f"{request.user.username} replied: {reply.text[:50]}...",
                    [comment.user.id],
                    f'/post/{comment.post.id}/'
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentReplyViewSet(viewsets.ModelViewSet):
    queryset = CommentReply.objects.all()
    serializer_class = CommentReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']

    @swagger_auto_schema(
        operation_description="Like or unlike a comment reply",
        responses={200: openapi.Response("Reply liked/unliked successfully")}
    )
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        reply = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, comment_reply=reply)
        if not created:
            like.delete()
            return Response({'message': 'Reply unliked'}, status=status.HTTP_200_OK)
        if reply.user != request.user:
            NotificationService.send_notification_to_userids(
                f"{request.user.username} liked your reply",
                f"{request.user.username} liked your reply: {reply.text[:50]}...",
                [reply.user.id],
                f'/post/{reply.comment.post.id}/'
            )
        return Response({'message': 'Reply liked'}, status=status.HTTP_201_CREATED)

class UserTagSettingsViewSet(viewsets.ModelViewSet):
    queryset = UserTagSettings.objects.all()
    serializer_class = UserTagSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserTagSettings.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)