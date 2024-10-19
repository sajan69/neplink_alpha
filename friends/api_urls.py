from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import FriendViewSet, FriendRequestViewSet

router = DefaultRouter()
router.register(r'friends', FriendViewSet, basename='friend')
router.register(r'friend-requests', FriendRequestViewSet, basename='friend-request')

urlpatterns = [
    path('', include(router.urls)),
]