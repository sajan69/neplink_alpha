from django.urls import path
from accounts.views import UserRegisterView, UserLoginView, PasswordResetView, OTPVerificationView, UserPasswordChangeView,HomeView,logout_view,PasswordResetConfirmView

app_name = 'accounts'
urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('otp-verify/', OTPVerificationView.as_view(), name='otp_verify'),
    path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('', HomeView.as_view(), name='home'),
    path('logout/', logout_view, name='logout'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
