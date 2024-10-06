from django.urls import path
from . import views

app_name = 'friends'

urlpatterns = [
    path('', views.friend_list, name='friend_list'),
    path('search/', views.user_search, name='user_search'),
    path('request/send/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('request/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('request/reject/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('remove/<int:friend_id>/', views.remove_friend, name='remove_friend'),
    path('requests/', views.friend_requests, name='friend_requests'),
    path('search-friends/', views.search_friends, name='friend_search'),
    path('request/cancel/<int:request_id>/', views.cancel_friend_request, name='cancel_friend_request'),

]