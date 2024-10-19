from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import UserRegistrationView, UserLoginView, UserViewSet, NotificationViewSet, PasswordResetAPIView, OTPVerificationAPIView, PasswordResetConfirmAPIView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='api_register'),
    path('login/', UserLoginView.as_view(), name='api_login'),
    path('password-reset/', PasswordResetAPIView.as_view(), name='api_password_reset'),
    path('password-reset/otp-verify/', OTPVerificationAPIView.as_view(), name='api_otp_verify'),
    path('password-reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='api_password_reset_confirm'),
]