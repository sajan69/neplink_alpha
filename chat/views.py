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
    
    if not room.participants.filter(id=request.user.id).exists():
        messages.error(request, "You don't have access to this chat room.")
        return redirect('chat:chat_list')
    print(messages_info)
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

from agora_token_builder.RtcTokenBuilder import Role_Publisher
from agora_token_builder import RtcTokenBuilder
from django.conf import settings
import time
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .agora import APP_ID, generate_agora_token
from django.views.decorators.http import require_POST

@csrf_exempt

@login_required
def initiate_call(request):
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        call_type = data.get('call_type')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not room_id or not call_type:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        room = ChatRoom.objects.get(id=room_id)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'error': 'Chat Room not found'}, status=404)

    # Check if there's an ongoing call
    ongoing_call = room.call_logs.filter(status='ongoing').first()
    if ongoing_call:
        return JsonResponse({
            'status': 'Call already ongoing',
            'call_log_id': ongoing_call.id,
            'agora_channel': ongoing_call.agora_channel,
            'call_type': ongoing_call.call_type
        })

    # Create a new call log
    agora_channel = f'room_{room_id}_{int(datetime.now(timezone.utc).timestamp())}'
    call_log = CallLog.objects.create(
        room=room,
        caller=request.user,
        agora_channel=agora_channel,
        call_type=call_type,
    )
    call_log.participants.add(request.user)

    return JsonResponse({
        'status': 'Call initiated',
        'call_log_id': call_log.id,
        'agora_channel': call_log.agora_channel,
        'call_type': call_type
    })

@csrf_exempt

@login_required
def end_call(request):
    try:
        data = json.loads(request.body)
        call_log_id = data.get('call_log_id')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not call_log_id:
        return JsonResponse({'error': 'Missing call_log_id'}, status=400)

    try:
        call_log = CallLog.objects.get(id=call_log_id)
    except CallLog.DoesNotExist:
        return JsonResponse({'error': 'Invalid Call Log'}, status=400)

    if call_log.status == 'ended':
        return JsonResponse({'error': 'Call already ended'}, status=400)

    # Mark the call log as ended
    call_log.end_call()

    return JsonResponse({'status': 'Call ended'})

@csrf_exempt
@require_POST
@login_required
def join_call(request):
    try:
        data = json.loads(request.body)
        call_log_id = data.get('call_log_id')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not call_log_id:
        return JsonResponse({'error': 'Missing call_log_id'}, status=400)

    try:
        call_log = CallLog.objects.get(id=call_log_id)
    except CallLog.DoesNotExist:
        return JsonResponse({'error': 'Invalid Call Log'}, status=400)

    if call_log.status != 'ongoing':
        return JsonResponse({'error': 'Call is not ongoing'}, status=400)

    # Add the user to the call participants
    call_log.participants.add(request.user)

    return JsonResponse({
        'status': 'Joined call',
        'agora_channel': call_log.agora_channel,
        'call_type': call_log.call_type
    })

@login_required
def get_agora_token(request):
    """
    API endpoint to get Agora token for a specific call channel and user.
    """
    channel_name = request.GET.get('channel')
    uid = request.GET.get('uid')

    if not channel_name or not uid:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    token = generate_agora_token(channel_name, uid, Role_Publisher)
    return JsonResponse({'token': token, 'channel_name': channel_name, 'app_id': APP_ID})