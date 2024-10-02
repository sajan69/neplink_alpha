from datetime import timezone
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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
        room = ChatRoom.objects.create(is_group_chat=False)
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
    if not room.participants.filter(id=request.user.id).exists():
        messages.error(request, "You don't have access to this chat room.")
        return redirect('chat:chat_list')

    messagess = room.messages.all()
    
    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messagess
    })

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_receiver(receiver_id, caller_id, room_id):
    channel_layer = get_channel_layer()

    # Notify the receiver of the incoming call
    async_to_sync(channel_layer.group_send)(
        f'incoming_calls_{receiver_id}',
        {
            'type': 'notify_incoming_call',
            'caller': caller_id,
            'room_id': room_id,
        }
    )


@login_required
def call_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if the user is in the room participants
    if request.user not in room.participants.all():
        return redirect('chat:chat_list')
    
    return render(request, 'chat/call_room.html', {'room': room})

@login_required
def start_call(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    caller = request.user

    # Here, you might need to get the receiver from the frontend or from the room participants
    receiver_id = request.GET.get('receiver_id')
    receiver = get_object_or_404(User, id=receiver_id)

    call_log = CallLog.objects.create(room=room, caller=caller, receiver=receiver)
    
    return JsonResponse({'status': 'success', 'call_log_id': call_log.id})

@login_required
def end_call(request, call_log_id):
    call_log = get_object_or_404(CallLog, id=call_log_id)
    call_log.end_time = timezone.now()
    call_log.status = 'ended'
    call_log.save()

    # Optionally, you can add more logic for cleaning up after a call ends
    # For example, you can delete the call log if the call was too short
    # or if the call was not answered

    return JsonResponse({'status': 'success'})