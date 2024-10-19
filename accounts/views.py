from django.http import JsonResponse
from django.views.generic import View, TemplateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

from accounts.services import NotificationService
from chat.models import ChatRoom
from friends.models import FriendRequest, Friendship
from post.models import CommentReply, PostMedia, SelectedFriend, UserTagSettings
from .models import Notification, User, OTP
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

class UserRegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        contact = request.POST.get('contact')
        
        user = User.objects.create_user(username=username, email=email, password=password, contact=contact)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('accounts:login')

class UserLoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('accounts:home')
        return render(request, self.template_name, messages.error(request, 'Invalid credentials')) 
class PasswordResetView(View):
    template_name = 'accounts/password_reset.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No user found with this email address.")
            return render(request, self.template_name)

        otp = OTP.generate_otp(user)
        send_mail(
            'Password Reset OTP',
            f'Your OTP is {otp.code}',
            'from@example.com',
            [email],
        )
        request.session['reset_email'] = email
        return redirect('accounts:otp_verify')

class OTPVerificationView(View):
    template_name = 'accounts/otp_verify.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        otp = request.POST.get('otp')
        email = request.session.get('reset_email')
        if not email:
            messages.error(request, "Session expired. Please start the password reset process again.")
            return redirect('accounts:password_reset')

        try:
            user = User.objects.get(email=email)
            otp_instance = OTP.objects.filter(user=user, code=otp).latest('created_at')
            if otp_instance.is_valid():
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                return redirect('accounts:password_reset_confirm', uidb64=uid, token=token)
            else:
                messages.error(request, "Invalid or expired OTP.")
        except (User.DoesNotExist, OTP.DoesNotExist):
            messages.error(request, "Invalid OTP.")

        return render(request, self.template_name)

class PasswordResetConfirmView(View):
    template_name = 'accounts/password_reset_confirm.html'

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            return render(request, self.template_name)
        else:
            messages.error(request, "The password reset link is invalid or has expired.")
            return redirect('accounts:password_reset')

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 != password2:
                messages.error(request, "Passwords do not match.")
                return render(request, self.template_name)
            
            user.set_password(password1)
            user.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect('accounts:login')
        else:
            messages.error(request, "The password reset link is invalid or has expired.")
            return redirect('accounts:password_reset')

class UserPasswordChangeView(View):
    template_name = 'accounts/password_change.html'

    @method_decorator(login_required)
    def get(self, request):
        return render(request, self.template_name)

    @method_decorator(login_required)
    def post(self, request):
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not request.user.check_password(old_password):
            return render(request, self.template_name, {'error': 'Incorrect old password'})
        
        if new_password1 != new_password2:
            return render(request, self.template_name, {'error': 'New passwords do not match'})
        
        request.user.set_password(new_password1)
        request.user.save()
        return redirect('accounts:login')
    

import json
from django.http import JsonResponse
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from post.models import Post, Comment, CommentReply, Like, PostMedia
from django.db import transaction
from django.db.models import Q
from django.db import models
from django.template.loader import render_to_string
class HomeView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'accounts/home.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        """Return all non-hidden posts ordered by creation date (newest first)."""
        user = self.request.user
        friends = Friendship.objects.filter(user=user).values_list('friend', flat=True)
        
        return Post.objects.filter(
            models.Q(visibility='everyone') |
            (models.Q(visibility='friends') & (models.Q(user__in=friends) | models.Q(user=user))) |
            (models.Q(visibility='private') & models.Q(user=user)) |
            (models.Q(visibility='selected') & (models.Q(selected_friends__friend=user) | models.Q(user=user)))
        ).distinct().order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add additional context data for the template."""
        context = super().get_context_data(**kwargs)
        context['unknown_users'] = User.objects.exclude(id=self.request.user.id).exclude(friends__user=self.request.user).exclude(friend_requests_received__from_user=self.request.user).exclude(friend_requests_sent__to_user=self.request.user)
        context['suggested_users'] = User.objects.filter(friends__user__friends__user=self.request.user).exclude(id=self.request.user.id).exclude(friends__user=self.request.user).exclude(friend_requests_received__from_user=self.request.user).exclude(friend_requests_sent__to_user=self.request.user).distinct()
        context['friend_requests'] = FriendRequest.objects.filter(to_user=self.request.user)
        context['friends'] = Friendship.objects.filter(user=self.request.user).select_related('friend')

        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            posts_html = render_to_string('post/post_list.html', {'posts': context['posts']}, request=self.request)
            return JsonResponse({
                'html': posts_html,
                'has_next': context['page_obj'].has_next(),
            })
        return super().render_to_response(context, **response_kwargs)
    
    def post(self, request, *args, **kwargs):
        caption = request.POST.get('caption')
        feeling = request.POST.get('feeling')
        visibility = request.POST.get('visibility')
        files = request.FILES.getlist('files')
        selected_friends = request.POST.getlist('selected_friends')
        tagged_friends = request.POST.getlist('tagged_friends')

        if not caption and not files:
            messages.error(request, 'Please provide a caption or upload media files.')
            return redirect('accounts:home')

        try:
            with transaction.atomic():
                post = Post.objects.create(
                    user=request.user,
                    caption=caption,
                    feeling=feeling,
                    visibility=visibility
                )

                for file in files:
                    file_type = self.get_file_type(file.name)
                    PostMedia.objects.create(
                        post=post,
                        file=file,
                        file_type=file_type
                    )

                if visibility == 'selected':
                    for friend_id in selected_friends:
                        SelectedFriend.objects.create(post=post, friend_id=friend_id)

                if tagged_friends:
                    for friend_id in tagged_friends:
                        friend = get_object_or_404(User, id=friend_id)
                        if friend.tag_settings.allow_tagging:
                            post.tagged_users.add(friend)
                            NotificationService.send_notification_to_userids(
                                f"{request.user.username} tagged you in a post",
                                f"{request.user.username} tagged you in a post: {post.caption[:50]}...",
                                [friend.id],
                                reverse('post:post_detail', args=[post.id])
                            )

            messages.success(request, 'Post created successfully!')
        except Exception as e:
            messages.error(request, f'An error occurred while creating the post: {str(e)}')

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
    
class LandingPageView(TemplateView):
    template_name = 'accounts/landing_page.html'
    


def logout_view(request):
    logout(request)
    return redirect('accounts:login')

from django.views.generic import DetailView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy



from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q, Prefetch

from django.db.models import Q
from push_notifications.models import GCMDevice

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'user'
    paginate_by = 10
    

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viewed_user = self.get_object()
        current_user = self.request.user

        # Check if the profile being viewed belongs to the current user
        context['is_own_profile'] = (current_user == viewed_user)

        # Fetch all friendships for both the viewed user and the current user
        viewed_user_friends = Friendship.objects.filter(Q(user=viewed_user) | Q(friend=viewed_user)).select_related('friend')
        current_user_friends = Friendship.objects.filter(Q(user=current_user) | Q(friend=current_user)).select_related('friend')

        # Efficiently store friends of both users in sets
        viewed_user_friends_set = set(friendship.user if friendship.friend == viewed_user else friendship.friend for friendship in viewed_user_friends)
        current_user_friends_set = set(friendship.user if friendship.friend == current_user else friendship.friend for friendship in current_user_friends)

        # Calculate mutual friends
        mutual_friends = viewed_user_friends_set.intersection(current_user_friends_set)



        # Fetch friend requests
        friend_requests_sent = FriendRequest.objects.filter(from_user=current_user)
        friend_requests_received = FriendRequest.objects.filter(to_user=current_user)

        # Process friendships for the viewed user
        friends = set()
        is_friend = False
        for friendship in viewed_user_friends:
            friend = friendship.friend if friendship.user == viewed_user else friendship.user
            friends.add(friend)
            if friend == current_user:
                is_friend = True

        context['friends'] = friends
        context['is_friend'] = is_friend

        # Process friend requests
        context['friend_requests_sent'] = [{'user': req.to_user, 'id': req.id} for req in friend_requests_sent]
        context['friend_requests_received'] = [req.from_user for req in friend_requests_received]

        # Determine appropriate action
        if is_friend:
            context['action'] = 'chat'
        elif viewed_user in [req['user'] for req in context['friend_requests_sent']]:
            request_id = [req['id'] for req in context['friend_requests_sent'] if req['user'] == viewed_user][0]
            context['action'] = 'request_sent'
            context['request_id'] = request_id
        elif viewed_user in context['friend_requests_received']:
            request_id = friend_requests_received.get(from_user=viewed_user).id
            context['action'] = 'request_received'
            context['request_id'] = request_id
        elif not context['is_own_profile']:
            context['action'] = 'add_friend'

         # Fetch and paginate posts
        posts = Post.objects.filter(user=viewed_user).order_by('-created_at')
        posts_paginator = Paginator(posts, self.paginate_by)
        posts_page = posts_paginator.get_page(self.request.GET.get('posts_page', 1))
        context['posts'] = posts_page

        # Fetch and paginate tagged posts
        tag_settings, created = UserTagSettings.objects.get_or_create(user=viewed_user)
        if tag_settings.show_tagged_posts:
            tagged_posts = viewed_user.tagged_posts.all().order_by('-created_at')
            tagged_posts_paginator = Paginator(tagged_posts, self.paginate_by)
            tagged_posts_page = tagged_posts_paginator.get_page(self.request.GET.get('tagged_posts_page', 1))
            context['tagged_posts'] = tagged_posts_page

        # Add mutual friends to the context
        context['mutual_friends'] = mutual_friends

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            posts_page = context['posts']
            tagged_posts_page = context.get('tagged_posts')

            if self.request.GET.get('posts_page'):
                html = render_to_string('post/post_list.html', {'posts': posts_page}, request=self.request)
                return JsonResponse({
                    'html': html,
                    'has_next': posts_page.has_next(),
                })
            elif self.request.GET.get('tagged_posts_page'):
                html = render_to_string('post/post_list.html', {'posts': tagged_posts_page}, request=self.request)
                return JsonResponse({
                    'html': html,
                    'has_next': tagged_posts_page.has_next(),
                })

        return super().render_to_response(context, **response_kwargs)

# Edit profile view - Allows editing only if the user is viewing their own profile
@method_decorator(login_required, name='dispatch')
class ProfileEditView(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'bio', 'contact', 'profile_pic', 'cover_photo']
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        if self.request.user.username != self.kwargs['username']:
            return redirect('accounts:profile', username=self.kwargs['username'])
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'username': self.request.user.username})
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
class RegisterDeviceView(APIView):
    def post(self, request, *args, **kwargs):
        registration_id = request.data.get("registration_id")
        user_id = request.data.get("user_id")

        if not registration_id:
            return Response({"error": "Missing registration_id"}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the device with the registration_id exists
        device = GCMDevice.objects.filter(registration_id=registration_id).first()

        if device:
            # If device exists and user is provided, assign the device to the user
            if user:
                device.user = user
            device.active = True
            device.save()
            created = False
        else:
            # If device does not exist, create a new device
            device = GCMDevice.objects.create(registration_id=registration_id, user=user, active=True)
            created = True

        return Response({"success": True, "created": created}, status=status.HTTP_201_CREATED)

    

class LogoutDeviceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        registration_id = request.data.get("registration_id")

        if not registration_id:
            return Response({"error": "Missing registration_id"}, status=status.HTTP_400_BAD_REQUEST)

        device = GCMDevice.objects.filter(registration_id=registration_id, user=request.user).first()
        if device:
            device.active = False
            device.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)
    
class UserSettingsView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/user_settings.html'
    fields = ['first_name', 'last_name', 'email', 'bio', 'profile_pic', 'cover_photo']
    success_url = reverse_lazy('accounts:user_settings')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_settings, created = UserTagSettings.objects.get_or_create(user=self.request.user)
        context['tag_settings'] = tag_settings
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_private = self.request.POST.get('is_private') == 'on'
        user.show_email = self.request.POST.get('show_email') == 'on'
        user.show_full_name = self.request.POST.get('show_full_name') == 'on'
        user.save()

        tag_settings, created = UserTagSettings.objects.get_or_create(user=user)
        tag_settings.allow_tagging = self.request.POST.get('allow_tagging') == 'on'
        tag_settings.show_tagged_posts = self.request.POST.get('show_tagged_posts') == 'on'
        tag_settings.save()

        messages.success(self.request, 'Your settings have been updated successfully.')
        return super().form_valid(form)

def notifications_view(request):
    user = request.user
    page_number = request.GET.get('page', 1)
    notifications = NotificationService.get_user_notifications(user.id)
    unread_count = NotificationService.get_unread_notification_count(user.id)
    
    paginator = Paginator(notifications, 12)  # Show 12 notifications per page
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': unread_count
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If it's an AJAX request, return JSON data
        notification_data = [{
            'id': n.id,
            'title': n.title,
            'body': n.body,
            'timestamp': n.timestamp.isoformat(),
            'read': n.read,
            'link': n.link
        } for n in page_obj]
        return JsonResponse({
            'notifications': notification_data,
            'has_next': page_obj.has_next(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None
        })
    
    return render(request, 'accounts/notifications.html', context)


@require_POST
def mark_notification_read(request, notification_id):
    user_id = request.user.id  # Assuming the user is authenticated
    NotificationService.mark_notification_as_read(user_id, notification_id)
    return JsonResponse({'success': True})

@require_POST
def mark_all_notifications_read(request):
    user_id = request.user.id  # Assuming the user is authenticated
    NotificationService.mark_all_notifications_as_read(user_id)
    return JsonResponse({'success': True})



