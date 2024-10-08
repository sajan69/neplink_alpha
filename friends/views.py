from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from accounts.services import NotificationService
from .models import FriendRequest, Friendship
from accounts.models import User

@login_required
def friend_list(request):
    friendships = Friendship.objects.filter(user=request.user)
    friends = [friendship.friend for friendship in friendships]
    return render(request, 'friends/friend_list.html', {'friends': friends})
@login_required
def search_friends(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            query = request.GET.get('query', '')
            
            if query:
                # Get the current user's friendships
                friendships = Friendship.objects.filter(user=request.user)
                
                # Get the IDs of friends to filter them later
                friend_ids = friendships.values_list('friend__id', flat=True)
                
                # Now, search among the friends based on the query (username, first name, last name)
                friends = User.objects.filter(
                    Q(id__in=friend_ids) & (Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
                )
                
                results = []
                for friend in friends:
                    results.append({
                        'id': friend.id,
                        'username': friend.username,
                        'profile_pic_url': friend.profile_pic.url if friend.profile_pic else '/static/img/default_profile_pic.png'
                    })
                
                return JsonResponse({'friends': results})
            else:
                return JsonResponse({'friends': []})
        
    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
def user_search(request):
    query = request.GET.get('query')
    users = []
    friend_status = {}
    sent_requests = []
    received_requests = []

    if query:
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
        for user in users:
            if Friendship.objects.filter(user=request.user, friend=user).exists():
                friend_status[user.id] = 'friend'
            elif FriendRequest.objects.filter(from_user=request.user, to_user=user).exists():
                friend_status[user.id] = 'request_sent'
                sent_requests = FriendRequest.objects.filter(from_user=request.user)
            elif FriendRequest.objects.filter(from_user=user, to_user=request.user).exists():
                friend_status[user.id] = 'request_received'
                received_requests = FriendRequest.objects.filter(to_user=request.user)
            else:
                friend_status[user.id] = 'not_friend'

    print(sent_requests) 

    return render(request, 'friends/user_search.html', {'users': users, 'friend_status': friend_status, 'received_requests': received_requests, 'sent_requests': sent_requests})

@login_required
def send_friend_request(request, username):
    to_user = get_object_or_404(User, username=username)
    if to_user == request.user:
        messages.error(request, "You can't send a friend request to yourself.")
        return redirect('friends:user_search')
    
    friend_request, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    if created:
        messages.success(request, f'Friend request sent to {to_user.username}.')
        NotificationService.send_notification_to_userids('Friend Request', f'{request.user.username} sent you a friend request.', [to_user.id], '/friends/requests/')
    else:
        messages.info(request, f'Friend request to {to_user.username} already sent.')
    return redirect('friends:user_search')

@login_required
def cancel_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, from_user=request.user)
    friend_request.delete()
    messages.success(request, f'Friend request to {friend_request.to_user.username} cancelled.')
    return redirect('friends:friend_requests')

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    Friendship.objects.create(user=request.user, friend=friend_request.from_user)
    Friendship.objects.create(user=friend_request.from_user, friend=request.user)
    friend_request.delete()
    messages.success(request, f'You are now friends with {friend_request.from_user.username}.')
    return redirect('friends:friend_requests')

@login_required
def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.delete()
    messages.success(request, f'Friend request from {friend_request.from_user.username} rejected.')
    return redirect('friends:friend_requests')

@login_required
def remove_friend(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    Friendship.objects.filter(
        Q(user=request.user, friend=friend) | Q(user=friend, friend=request.user)
    ).delete()
    messages.success(request, f'{friend.username} removed from friends.')
    return redirect('friends:friend_list')

@login_required
def friend_requests(request):
    received_requests = FriendRequest.objects.filter(to_user=request.user)
    sent_requests = FriendRequest.objects.filter(from_user=request.user)
    return render(request, 'friends/friend_requests.html', {
        'received_requests': received_requests,
        'sent_requests': sent_requests
    })