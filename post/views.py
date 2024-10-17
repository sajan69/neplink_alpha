from django.shortcuts import render

# Create your views here.
from django.views import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from accounts.models import User
from friends.models import Friendship
from post.models import Post, Comment, CommentReply, Like, PostMedia, SelectedFriend, UserTagSettings
from django.urls import reverse
from accounts.services import NotificationService
from django.db.models import Count
import json
from django.contrib.auth import get_user_model

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
            'hide_unhide_post': self.hide_unhide_post,
            'tag_friends': self.tag_friends,
            'remove_tag': self.remove_tag,
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
        post.caption = request.POST.get('caption', post.caption)
        post.feeling = request.POST.get('feeling', post.feeling)
        post.visibility = request.POST.get('visibility', post.visibility)

         # Handle SelectedFriend objects
        SelectedFriend.objects.filter(post=post).delete()  # Remove all existing selections
        if post.visibility == 'selected':
            selected_friend_ids = request.POST.getlist('selected_friends')
            User = get_user_model()
            for friend_id in selected_friend_ids:
                friend = User.objects.get(id=friend_id)
                SelectedFriend.objects.create(post=post, friend=friend)


        # Handle file deletions
        deleted_media = request.POST.getlist('deleted_media')
        PostMedia.objects.filter(id__in=deleted_media).delete()

        # Handle new file uploads
        files = request.FILES.getlist('files')
        for file in files:
            file_type = self.get_file_type(file.name)
            PostMedia.objects.create(post=post, file=file, file_type=file_type)

        post.save()
        messages.success(request, 'Post updated successfully')
        return redirect('accounts:home')
    
    def get_file_type(self, filename):
        extension = filename.split('.')[-1].lower()
        if extension in ['jpg', 'jpeg', 'png', 'gif']:
            return 'image'
        elif extension in ['mp4', 'avi', 'mov']:
            return 'video'
        elif extension in ['mp3', 'wav']:
            return 'audio'
        else:
            return 'unknown'

    def edit_comment(self, request, post):
        comment_id = request.POST.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        comment.text = request.POST.get('text', comment.text)
        comment.save()
        messages.success(request, 'Comment updated successfully')
        return redirect('accounts:home')

    def share_post(self, request, post):
        share_caption = request.POST.get('share_caption', '')
        visibility = request.POST.get('visibility', 'everyone')
        feeling = request.POST.get('feeling', '')

        shared_post = Post.objects.create(
            user=request.user,
            caption=share_caption,
            shared_post=post,
            is_shared=True,
            visibility=visibility,
            feeling=feeling
        )

        if visibility == 'selected':
            selected_friend_ids = request.POST.getlist('selected_friends')
            User = get_user_model()
            for friend_id in selected_friend_ids:
                friend = User.objects.get(id=friend_id)
                SelectedFriend.objects.create(post=shared_post, friend=friend)

        messages.success(request, 'Post shared successfully')
        if post.user != request.user:
            NotificationService.send_notification_to_userids(
                f"{request.user.username} shared your post",
                f"{request.user.username} shared your post: {post.caption[:50]}...",
                [post.user.id],
                reverse('post:post_detail', args=[shared_post.id])
            )
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
    
    def hide_unhide_post(self, request, post):
        post.is_hidden = not post.is_hidden
        post.save()
        action = "hidden" if post.is_hidden else "unhidden"
        messages.success(request, f'Post {action} successfully')
        return redirect('accounts:home')
    
    def tag_friends(self, request, post):
        tagged_user_ids = request.POST.getlist('tagged_friends')
        for user_id in tagged_user_ids:
            user = get_object_or_404(User, id=user_id)
            tag_settings, created = UserTagSettings.objects.get_or_create(user=user)
            if tag_settings.allow_tagging:
                post.tagged_users.add(user)
                NotificationService.send_notification_to_userids(
                    f"{request.user.username} tagged you in a post",
                    f"{request.user.username} tagged you in a post: {post.caption[:50]}...",
                    [user.id],
                    reverse('post:post_detail', args=[post.id])
                )
        messages.success(request, 'Friends tagged successfully')
        return redirect('accounts:home')

    def remove_tag(self, request, post):
        user = request.user
        post.tagged_users.remove(user)
        messages.success(request, 'You have been removed from the tagged post')
        return redirect('accounts:home')
    

class PostDetailView(LoginRequiredMixin, View):
    template_name = 'post/post_detail.html'

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        friends = Friendship.objects.filter(user=request.user).select_related('friend')
        context = {
            'post': post,
            'is_owner': post.user == request.user,
            'friends': friends
        }
        return render(request, self.template_name, context)
    

class HiddenPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'post/hidden_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        """Return all hidden posts for the current user."""
        return Post.objects.filter(user=self.request.user, is_hidden=True).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['friends'] = Friendship.objects.filter(user=self.request.user).select_related('friend')
        return context


