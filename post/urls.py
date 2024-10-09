from django.urls import path
from .views import PostManagementView, PostDetailView

app_name = 'post'
urlpatterns = [
    path('post-management/', PostManagementView.as_view(), name='post_management'),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
]

