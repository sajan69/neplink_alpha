from django.shortcuts import render

# Create your views here.
from django.views import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from post.models import Post, Comment, CommentReply, Like
from django.urls import reverse
from accounts.services import NotificationService
from django.db.models import Count
import json

from django.shortcuts import redirect
from django.contrib import messages

class PostManagementView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        post_id = request.POST.get('post_id')

        if not action or not post_id:
            messages.error(request, 'Invalid request')
            return redirect('accounts:home')

        try:
            post_id = int(post_id)
            post = get_object_or_404(Post, id=post_id)
        except ValueError:
            messages.error(request, 'Invalid post ID')
            return redirect('accounts:home')

        actions = {
            
            'like_post': self.like_post,
            'like_comment': self.like_comment,
            'add_comment': self.add_comment,
            'delete_comment': self.delete_comment,
            'delete_post': self.delete_post,
            'edit_post': self.edit_post,
            'edit_comment': self.edit_comment,
            'share_post': self.share_post,
            'edit_reply': self.edit_reply,
            'delete_reply': self.delete_reply,
            'add_reply': self.add_reply,
            'like_reply': self.like_reply,
        }

        if action in actions:
            return actions[action](request, post)
        
        messages.error(request, 'Invalid action')
        return redirect('accounts:home')

    

    def like_post(self, request, post):
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            messages.success(request, 'Post unliked successfully')
        else:
            messages.success(request, 'Post liked successfully')
            if post.user != request.user:
                NotificationService.send_notification_to_userids(
                    f"{request.user.username} liked your post",
                    f"{request.user.username} liked your post: {post.caption[:50]}...",
                    [post.user.id],
                    reverse('post:post_detail', args=[post.id])
                )
        return redirect('accounts:home')

    def like_comment(self, request, post):
        comment_id = request.POST.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)
        like, created = Like.objects.get_or_create(user=request.user, comment=comment)
        if not created:
            like.delete()
            messages.success(request, 'Comment unliked successfully')
        else:
            messages.success(request, 'Comment liked successfully')
            if comment.user != request.user:
                NotificationService.send_notification_to_userids(
                    f"{request.user.username} liked your comment",
                    f"{request.user.username} liked your comment: {comment.text[:50]}...",
                    [comment.user.id],
                    reverse('post:post_detail', args=[post.id])
                )
        return redirect('accounts:home')

    def add_comment(self, request, post):
        text = request.POST.get('text')
        if text:
            comment = Comment.objects.create(user=request.user, post=post, text=text)
            messages.success(request, 'Comment added successfully')
            if post.user != request.user:
                NotificationService.send_notification_to_userids(
                    f"{request.user.username} commented on your post",
                    f"{request.user.username} commented: {text[:50]}...",
                    [post.user.id],
                    reverse('post:post_detail', args=[post.id])
                )
        else:
            messages.error(request, 'Comment text is required')
        return redirect('accounts:home')

    def delete_comment(self, request, post):
        comment_id = request.POST.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        comment.delete()
        messages.success(request, 'Comment deleted successfully')
        return redirect('accounts:home')

    def delete_post(self, request, post):
        if request.user != post.user:
            messages.error(request, 'You do not have permission to delete this post')
        else:
            post.delete()
            messages.success(request, 'Post deleted successfully')
        return redirect('accounts:home')
    def edit_post(self, request, post):
        if request.user != post.user:
            messages.error(request, 'You do not have permission to edit this post')
            return redirect('accounts:home')

        post.caption = request.POST.get('caption', post.caption)
        post.feeling = request.POST.get('feeling', post.feeling)
        if 'media' in request.FILES:
            post.media = request.FILES['media']
        post.save()
        messages.success(request, 'Post updated successfully')
        return redirect('accounts:home')

    def edit_comment(self, request, post):
        comment_id = request.POST.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        comment.text = request.POST.get('text', comment.text)
        comment.save()
        messages.success(request, 'Comment updated successfully')
        return redirect('accounts:home')

    def share_post(self, request, post):
        share_caption = request.POST.get('share_caption', '')
        shared_post = Post.objects.create(
            user=request.user,
            caption=share_caption,
            post=post
        )
        messages.success(request, 'Post shared successfully')
        return redirect('accounts:home')

    def like_reply(self, request, post):
        reply_id = request.POST.get('reply_id')
        reply = get_object_or_404(CommentReply, id=reply_id)
        like, created = Like.objects.get_or_create(user=request.user, comment_reply=reply)
        if not created:
            like.delete()
            messages.success(request, 'Reply unliked successfully')
        else:
            messages.success(request, 'Reply liked successfully')
            if reply.user != request.user:
                NotificationService.send_notification_to_userids(
                    f"{request.user.username} liked your reply",
                    f"{request.user.username} liked your reply: {reply.text[:50]}...",
                    [reply.user.id],
                    reverse('post:post_detail', args=[post.id])
                )
        return redirect('accounts:home')

    def add_reply(self, request, post):
        comment_id = request.POST.get('comment_id')
        text = request.POST.get('text')
        comment = get_object_or_404(Comment, id=comment_id)
        if text:
            reply = CommentReply.objects.create(user=request.user, comment=comment, text=text)
            messages.success(request, 'Reply added successfully')
            if comment.user != request.user:
                NotificationService.send_notification_to_userids(
                    f"{request.user.username} replied to your comment",
                    f"{request.user.username} replied: {text[:50]}...",
                    [comment.user.id],
                    reverse('post:post_detail', args=[post.id])
                )
        else:
            messages.error(request, 'Reply text is required')
        return redirect('accounts:home')

    def edit_reply(self, request, post):
        reply_id = request.POST.get('reply_id')
        reply = get_object_or_404(CommentReply, id=reply_id, user=request.user)
        reply.text = request.POST.get('text', reply.text)
        reply.save()
        messages.success(request, 'Reply updated successfully')
        return redirect('accounts:home')

    def delete_reply(self, request, post):
        reply_id = request.POST.get('reply_id')
        reply = get_object_or_404(CommentReply, id=reply_id, user=request.user)
        reply.delete()
        messages.success(request, 'Reply deleted successfully')
        return redirect('accounts:home')
    

class PostDetailView(LoginRequiredMixin, View):
    template_name = 'accounts/post_detail.html'

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        context = {
            'post': post,
            'is_owner': post.user == request.user
        }
        return render(request, self.template_name, context)
