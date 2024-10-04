from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:room_id>/', views.chat_room, name='chat_room'),
    path('private/<int:friend_id>/', views.create_or_open_private_chat, name='create_or_open_private_chat'),
    path('group/create/', views.create_group_chat, name='create_group_chat'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('generate_agora_token/<int:room_id>/', views.generate_agora_token, name='generate_agora_token'),
    path('end_call/<int:call_log_id>/', views.end_call, name='end_call'),

]