from rest_framework import serializers
from .models import Post, PostMedia, Comment, CommentReply, Like, SelectedFriend, UserTagSettings
from accounts.serializers import UserSerializer

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'file_type', 'created_at']
        read_only_fields = ['id', 'created_at']

class CommentReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CommentReply
        fields = ['id', 'user', 'comment', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = CommentReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'text', 'created_at', 'updated_at', 'replies']
        read_only_fields = ['id', 'created_at', 'updated_at']

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'comment', 'comment_reply', 'created_at']
        read_only_fields = ['id', 'created_at']

class SelectedFriendSerializer(serializers.ModelSerializer):
    friend = UserSerializer(read_only=True)

    class Meta:
        model = SelectedFriend
        fields = ['id', 'post', 'friend']
        read_only_fields = ['id']

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    media = PostMediaSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    selected_friends = SelectedFriendSerializer(many=True, read_only=True)
    tagged_users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'caption', 'created_at', 'updated_at', 'feeling', 'is_hidden', 'visibility', 'shared_post', 'is_shared', 'tagged_users', 'media', 'comments', 'likes', 'selected_friends']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserTagSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTagSettings
        fields = ['id', 'user', 'allow_tagging', 'show_tagged_posts']
        read_only_fields = ['id']