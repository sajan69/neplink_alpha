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
    messages_info = room.messages.all()
    active_call = room.call_logs.filter(status='ongoing').first()
    
    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages_info,
        'active_call': active_call
    })

@csrf_exempt
@login_required
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        room_id = request.POST.get('room_id')
        room = ChatRoom.objects.get(id=room_id)
        
        message = Message.objects.create(
            sender=request.user,
            room=room,
            content=f"Shared file: {file.name}",
            is_file=True,
            file=file
        )
        
        return JsonResponse({'file_url': message.file.url})
    return JsonResponse({'error': 'Invalid request'}, status=400)