from django.views.generic import View, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from .models import User

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

def logout_view(request):
    logout(request)
    return redirect('accounts:login')