# your_app/context_processors.py



from accounts.services import NotificationService
from chat.models import ChatRoom
from friends.models import FriendRequest


def global_context(request):
    if request.user.is_authenticated:
        unread_count = NotificationService.get_unread_notification_count(request.user.id)
        friend_requests_count = FriendRequest.objects.filter(to_user=request.user).count()
 # Calculate total unread messages
        chat_rooms = ChatRoom.objects.filter(participants=request.user)
        messages_count = sum(room.unread_messages_count(request.user) for room in chat_rooms)
        unread_messages_rooms = [room for room in chat_rooms if room.unread_messages_count(request.user) > 0]
        unread_messages_rooms_count = len(unread_messages_rooms)
    else:
        unread_count = 0
        friend_requests_count = 0
        messages_count = 0
        unread_messages_rooms_count = 0


    return {
        'unread_count': unread_count,
        'friend_requests_count': friend_requests_count,
        'messages_count': messages_count,
        'unread_messages_rooms_count': unread_messages_rooms_count,
    }

