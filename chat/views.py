from datetime import timezone
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Q
from .models import CallLog, ChatRoom, Message
from accounts.models import User
from friends.models import Friendship

@login_required
def chat_list(request):
    user_rooms = ChatRoom.objects.filter(participants=request.user)
    
    return render(request, 'chat/chat_list.html', {'rooms': user_rooms})

@login_required
def create_or_open_private_chat(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    if not Friendship.objects.filter(user=request.user, friend=friend).exists():
        messages.error(request, "You can only chat with your friends.")
        return redirect('friends:friend_list')

    room = ChatRoom.objects.filter(
        participants=request.user
    ).filter(
        participants=friend
    ).filter(
        is_group_chat=False
    ).first()

    if not room:
        room_name = f"{request.user.username} - {friend.username}"
        room = ChatRoom.objects.create(is_group_chat=False, name=room_name)
        room.participants.add(request.user, friend)

    return redirect('chat:chat_room', room_id=room.id)

@login_required
def create_group_chat(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        participant_ids = request.POST.getlist('participants')
        
        if name and participant_ids:
            room = ChatRoom.objects.create(name=name, is_group_chat=True)
            room.participants.add(request.user)
            
            for participant_id in participant_ids:
                friend = get_object_or_404(User, id=participant_id)
                if Friendship.objects.filter(user=request.user, friend=friend).exists():
                    room.participants.add(friend)
            
            messages.success(request, f'Group chat "{name}" created successfully.')
            return redirect('chat:chat_room', room_id=room.id)
        else:
            messages.error(request, 'Please provide a name and select participants.')

    friends = Friendship.objects.filter(user=request.user).values_list('friend', flat=True)
    friends = User.objects.filter(id__in=friends)

    print(friends)
    return render(request, 'chat/create_group_chat.html', {'friends': friends})

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    rooms = ChatRoom.objects.filter(participants=request.user)
    messages_info = room.messages.all()
    
    if not room.participants.filter(id=request.user.id).exists():
        messages.error(request, "You don't have access to this chat room.")
        return redirect('chat:chat_list')
    print(messages_info)
    active_call = room.call_logs.filter(status='ongoing').first()
    
    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages_info,
        'active_call': active_call,
        'rooms': rooms
    })

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        user_id = request.POST.get('user_id')
        uploaded_file = request.FILES['file']

        user = User.objects.get(id=user_id)
        room = ChatRoom.objects.get(id=room_id)
        
        message = Message.objects.create(
            sender=user,
            room=room,
            content=f"Shared file: {uploaded_file.name}",
            is_file=True,
            file=uploaded_file  # File will be stored correctly
        )
        print(f'File uploaded: {message.file.url}')
        return JsonResponse({'file_url': message.file.url})

from agora_token_builder.RtcTokenBuilder import Role_Publisher
from agora_token_builder import RtcTokenBuilder
from django.conf import settings
import time

@csrf_exempt
@login_required
def generate_agora_token(request, room_id):
    # Retrieve the chat room and check if the user is a participant
    room = get_object_or_404(ChatRoom, id=room_id)
    if not room.is_participant(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)

    # Generate the channel name and token expiration
    channel_name = f"channel_{room.id}_{int(time.time())}"
    expiration_time_in_seconds = 3600  # Token valid for 1 hour
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration_time_in_seconds

    # Generate Agora token using RtcTokenBuilder
    token = RtcTokenBuilder.buildTokenWithUid(
        settings.AGORA_APP_ID, 
        settings.AGORA_APP_CERTIFICATE, 
        channel_name, 
        request.user.id, 
        Role_Publisher,  # Use the correct role here
        privilege_expired_ts
    )

    # Create a new call log entry
    call_log = CallLog.objects.create(
        room=room,
        caller=request.user,
        agora_channel=channel_name
    )
    room.active_call = call_log
    room.save()

    # Return the generated token and other information as a JSON response
    return JsonResponse({
        'token': token,
        'app_id': settings.AGORA_APP_ID,
        'channel_name': channel_name,
        'call_log_id': call_log.id
    })

@csrf_exempt
@login_required
def end_call(request, call_log_id):
    call_log = get_object_or_404(CallLog, id=call_log_id)
    if call_log.caller != request.user and call_log.receiver != request.user:
        return JsonResponse({'error': 'Access denied'}, status=403)

    call_log.end_call()
    return JsonResponse({'status': 'success'})