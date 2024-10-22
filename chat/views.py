from datetime import datetime, timezone
import json
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
    for room in user_rooms:
        room.unread_count = room.unread_messages_count(request.user)
    
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
    # room Participants excluding the logged in user
    room_participants = room.participants.exclude(id=request.user.id)
    room.mark_messages_as_read(request.user)
    
    if not room.participants.filter(id=request.user.id).exists():
        messages.error(request, "You don't have access to this chat room.")
        return redirect('chat:chat_list')
    active_call = room.call_logs.filter(status='ongoing').first()
    
    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages_info,
        'ongoing_call': active_call,
        'rooms': rooms,
        'room_participants': room_participants
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

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, CallLog
from agora_token_builder import RtcTokenBuilder
import random
import time
import json
from decouple import config
# ... (keep your existing imports and views)

@login_required
@require_POST
def initiate_call(request):
    data = json.loads(request.body)
    room_id = data.get('room_id')
    call_type = data.get('call_type')
    
    room = ChatRoom.objects.get(id=room_id)
    
    # Check if there's an ongoing call in the room
    ongoing_call = CallLog.objects.filter(room=room, status='ongoing').first()
    if ongoing_call:
        return JsonResponse({'status': 'Call already ongoing', 'call_log_id': ongoing_call.id})
    
    # Create a new call log
    call_log = CallLog.objects.create(
        room=room,
        caller=request.user,
        call_type=call_type,
        agora_channel=f"room_{room_id}"
    )
    call_log.participants.add(request.user)
    
    # Update the room's active call
    room.active_call = call_log
    room.save()
    
    return JsonResponse({'status': 'Call initiated', 'call_log_id': call_log.id, 'call_type': call_type})

@login_required
@require_POST
def end_call(request):
    data = json.loads(request.body)
    call_log_id = data.get('call_log_id')
    
    call_log = CallLog.objects.get(id=call_log_id)
    call_log.end_call()
    
    return JsonResponse({'status': 'Call ended'})

@login_required
def get_agora_token(request):
    app_id = config('AGORA_APP_ID')
    app_certificate = config('AGORA_APP_CERTIFICATE')
    channel = request.GET.get('channel')
    uid = random.randint(1, 230)
    expiration_time_in_seconds = 3600
    current_timestamp = int(time.time())
    privilegeExpiredTs = current_timestamp + expiration_time_in_seconds
    role = 1  # 1 for host, 2 for guest

    token = RtcTokenBuilder.buildTokenWithUid(app_id, app_certificate, channel, uid, role, privilegeExpiredTs)

    return JsonResponse({'token': token, 'uid': uid, 'app_id': app_id})