from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PostViewSet, CommentViewSet, CommentReplyViewSet, UserTagSettingsViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'comment-replies', CommentReplyViewSet)
router.register(r'user-tag-settings', UserTagSettingsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]