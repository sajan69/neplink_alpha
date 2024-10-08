# your_app/context_processors.py



from accounts.services import NotificationService
from chat.models import ChatRoom
from friends.models import FriendRequest


def global_context(request):
    if request.user.is_authenticated:
        unread_count = NotificationService.get_unread_notification_count(request.user.id)
        friend_requests_count = FriendRequest.objects.filter(to_user=request.user).count()
        messages_count = ChatRoom.objects.filter(participants=request.user).count()
    else:
        unread_count = 0
        friend_requests_count = 0
        messages_count = 0


    return {
        'unread_count': unread_count,
        'friend_requests_count': friend_requests_count,
        'messages_count': messages_count,
    }

