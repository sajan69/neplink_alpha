from django.views.generic import View, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail

from chat.models import ChatRoom
from friends.models import FriendRequest, Friendship
from .models import User
from django.contrib import messages

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
        login(request, user)
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
            login(request, user)
            return redirect('accounts:home')
        return render(request, self.template_name, {'error': 'Invalid credentials'})

class PasswordResetView(View):
    template_name = 'accounts/password_reset.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        otp = "123456"  # Replace with actual OTP generation logic
        send_mail(
            'Password Reset OTP',
            f'Your OTP is {otp}',
            'from@example.com',
            [email],
        )
        request.session['email'] = email
        return redirect('accounts:otp_verify')

class OTPVerificationView(View):
    template_name = 'accounts/otp_verify.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        otp = request.POST.get('otp')
        if otp == "123456":  # Check OTP
            return redirect('accounts:password_reset_confirm')
        return render(request, self.template_name, {'error': 'Invalid OTP'})
    


class PasswordResetConfirmView(View):
    template_name = 'accounts/password_reset_confirm.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            return render(request, self.template_name, {'error': 'Passwords do not match'})
        
        email = request.session.get('email')
        user = User.objects.get(email=email)
        user.set_password(password1)
        user.save()
        return redirect('accounts:login')

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
    

   

@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    template_name = 'accounts/home.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
         # Get all users except the current user and their friends and friend requests received and sent
        context['unknown_users'] = User.objects.exclude(id=self.request.user.id).exclude(friends__user=self.request.user).exclude(friend_requests_received__from_user=self.request.user).exclude(friend_requests_sent__to_user=self.request.user)

        # Get all friend requests received by the current user
        context['friend_requests'] = FriendRequest.objects.filter(to_user=self.request.user)
        print(context['friend_requests'])

        return context

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

@method_decorator(login_required, name='dispatch')
class ProfileView(DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'user'

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

        # Add mutual friends to the context
        context['mutual_friends'] = mutual_friends

        return context



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
