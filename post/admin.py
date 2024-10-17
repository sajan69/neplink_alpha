from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Post, PostMedia, SelectedFriend, UserTagSettings, Like, Comment, CommentReply

class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1
    fields = ('file', 'file_type', 'preview')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.file_type == 'image':
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.file.url)
        elif obj.file_type == 'video':
            return format_html('<video width="100" height="100" controls><source src="{}" type="video/mp4"></video>', obj.file.url)
        elif obj.file_type == 'audio':
            return format_html('<audio controls><source src="{}" type="audio/mpeg"></audio>', obj.file.url)
        return "No preview available"

class SelectedFriendInline(admin.TabularInline):
    model = SelectedFriend
    extra = 1
    autocomplete_fields = ['friend']

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('user', 'text', 'created_at', 'likes_count')
    readonly_fields = ('created_at', 'likes_count')

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'caption_preview', 'feeling', 'visibility', 'is_shared', 'created_at', 'likes_count', 'comments_count', 'tagged_users_count')
    list_filter = ('feeling', 'visibility', 'is_shared', 'created_at')
    search_fields = ('user__username', 'caption', 'tagged_users__username')
    autocomplete_fields = ['user', 'shared_post', 'tagged_users']
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'comments_count', 'shares_count')
    fieldsets = (
        ('Post Information', {
            'fields': ('user', 'caption', 'feeling', 'visibility', 'is_hidden')
        }),
        ('Sharing', {
            'fields': ('is_shared', 'shared_post')
        }),
        ('Tagging', {
            'fields': ('tagged_users',)
        }),
        ('Statistics', {
            'fields': ('created_at', 'updated_at', 'likes_count', 'comments_count', 'shares_count')
        }),
    )
    inlines = [PostMediaInline, SelectedFriendInline, CommentInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _likes_count=Count('likes', distinct=True),
            _comments_count=Count('comments', distinct=True),
            _tagged_users_count=Count('tagged_users', distinct=True)
        )
        return queryset

    def caption_preview(self, obj):
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
    caption_preview.short_description = 'Caption'

    def likes_count(self, obj):
        return obj._likes_count
    likes_count.short_description = 'Likes'
    likes_count.admin_order_field = '_likes_count'

    def comments_count(self, obj):
        return obj._comments_count
    comments_count.short_description = 'Comments'
    comments_count.admin_order_field = '_comments_count'

    def shares_count(self, obj):
        return obj.shares.count()
    shares_count.short_description = 'Shares'

    def tagged_users_count(self, obj):
        return obj._tagged_users_count
    tagged_users_count.short_description = 'Tagged Users'
    tagged_users_count.admin_order_field = '_tagged_users_count'

@admin.register(UserTagSettings)
class UserTagSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'allow_tagging', 'show_tagged_posts')
    list_filter = ('allow_tagging', 'show_tagged_posts')
    search_fields = ('user__username',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'content_object', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    autocomplete_fields = ['user', 'post', 'comment', 'comment_reply']

    def content_type(self, obj):
        if obj.post:
            return 'Post'
        elif obj.comment:
            return 'Comment'
        elif obj.comment_reply:
            return 'Comment Reply'
    content_type.short_description = 'Content Type'

    def content_object(self, obj):
        if obj.post:
            return f'Post {obj.post.id}'
        elif obj.comment:
            return f'Comment {obj.comment.id}'
        elif obj.comment_reply:
            return f'Comment Reply {obj.comment_reply.id}'
    content_object.short_description = 'Content Object'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'text_preview', 'created_at', 'likes_count', 'replies_count')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'text', 'post__caption')
    autocomplete_fields = ['user', 'post']
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'replies_count')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _likes_count=Count('likes', distinct=True),
            _replies_count=Count('replies', distinct=True)
        )
        return queryset

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'

    def likes_count(self, obj):
        return obj._likes_count
    likes_count.short_description = 'Likes'
    likes_count.admin_order_field = '_likes_count'

    def replies_count(self, obj):
        return obj._replies_count
    replies_count.short_description = 'Replies'
    replies_count.admin_order_field = '_replies_count'

@admin.register(CommentReply)
class CommentReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'text_preview', 'created_at', 'likes_count')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'text', 'comment__text')
    autocomplete_fields = ['user', 'comment']
    readonly_fields = ('created_at', 'updated_at', 'likes_count')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_likes_count=Count('likes', distinct=True))
        return queryset

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'

    def likes_count(self, obj):
        return obj._likes_count
    likes_count.short_description = 'Likes'
    likes_count.admin_order_field = '_likes_count'

