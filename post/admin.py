from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Post, Like, Comment, CommentReply

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('user', 'text', 'created_at', 'updated_at', 'likes_count')
    readonly_fields = ('created_at', 'updated_at', 'likes_count')

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'caption_preview', 'media_preview', 'feeling', 'created_at', 'updated_at', 'likes_count', 'comments_count')
    list_filter = ('feeling', 'created_at')
    search_fields = ('user__username', 'caption')
    date_hierarchy = 'created_at'
    inlines = [CommentInline]

    def caption_preview(self, obj):
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
    caption_preview.short_description = 'Caption'

    def media_preview(self, obj):
        if obj.media:
            file_extension = obj.media.name.split('.')[-1].lower()
            if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.media.url)
            elif file_extension in ['mp4', 'avi', 'mov']:
                return format_html('<video width="50" height="50" controls><source src="{}" type="video/mp4"></video>', obj.media.url)
            elif file_extension in ['mp3', 'wav']:
                return format_html('<audio controls><source src="{}" type="audio/mpeg"></audio>', obj.media.url)
        return "No media"
    media_preview.short_description = 'Media'

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = 'Comments'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post_link', 'text_preview', 'created_at', 'likes_count', 'replies_count')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'text', 'post__caption')
    date_hierarchy = 'created_at'

    def post_link(self, obj):
        url = reverse('admin:post_post_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, f'Post {obj.post.id}')
    post_link.short_description = 'Post'

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

    def replies_count(self, obj):
        return obj.replies.count()
    replies_count.short_description = 'Replies'

@admin.register(CommentReply)
class CommentReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment_link', 'text_preview', 'created_at', 'likes_count')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'text', 'comment__text')
    date_hierarchy = 'created_at'

    def comment_link(self, obj):
        url = reverse('admin:post_comment_change', args=[obj.comment.id])
        return format_html('<a href="{}">{}</a>', url, f'Comment {obj.comment.id}')
    comment_link.short_description = 'Comment'

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'content_object_link', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'

    def content_type(self, obj):
        if obj.post:
            return 'Post'
        elif obj.comment:
            return 'Comment'
        elif obj.comment_reply:
            return 'Comment Reply'
    content_type.short_description = 'Content Type'

    def content_object_link(self, obj):
        if obj.post:
            url = reverse('admin:post_post_change', args=[obj.post.id])
            return format_html('<a href="{}">{}</a>', url, f'Post {obj.post.id}')
        elif obj.comment:
            url = reverse('admin:post_comment_change', args=[obj.comment.id])
            return format_html('<a href="{}">{}</a>', url, f'Comment {obj.comment.id}')
        elif obj.comment_reply:
            url = reverse('admin:post_commentreply_change', args=[obj.comment_reply.id])
            return format_html('<a href="{}">{}</a>', url, f'Comment Reply {obj.comment_reply.id}')
    content_object_link.short_description = 'Content Object'