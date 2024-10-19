from django.urls import path
from accounts.views import (
    
    ProfileEditView,
    ProfileView,
    UserRegisterView,
    UserLoginView,
    PasswordResetView,
    OTPVerificationView,
    UserPasswordChangeView,
    HomeView,
    logout_view,
    PasswordResetConfirmView,
    LandingPageView,
    RegisterDeviceView,
    LogoutDeviceView,
    notifications_view,
    mark_all_notifications_read,
    mark_notification_read,
    UserSettingsView,
)
 
app_name = 'accounts'
urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/otp-verify/', OTPVerificationView.as_view(), name='otp_verify'),
    path('password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    path('', HomeView.as_view(), name='home'),
    path('logout/', logout_view, name='logout'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
     path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/edit/', ProfileEditView.as_view(), name='edit_profile'),
    path('landing-page/', LandingPageView.as_view(), name='landing_page'),
    path('register-device/', RegisterDeviceView.as_view(), name='register_device'),
    path('logout-device/', LogoutDeviceView.as_view(), name='logout_device'),
    path('notifications/', notifications_view, name='notifications'),
    path('notifications/mark-all-read/', mark_all_notifications_read, name='mark_all_read'),
    path('notifications/mark-read/<int:notification_id>/', mark_notification_read, name='mark_read'),
    path('settings/', UserSettingsView.as_view(), name='user_settings'),

    ]


