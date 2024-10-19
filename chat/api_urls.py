from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ChatRoomViewSet, MessageViewSet, CallLogViewSet

router = DefaultRouter()
router.register(r'chat-rooms', ChatRoomViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'call-logs', CallLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]