from django import template
from friends.models import FriendRequest

register = template.Library()

@register.filter
def is_friend(user, friend):
    return friend in user.friends.all()

@register.filter
def is_friend_request_sent(user, friend):
    return FriendRequest.objects.filter(from_user=user, to_user=friend).exists()

@register.filter
def is_friend_request_received(user, friend):
    return FriendRequest.objects.filter(from_user=friend, to_user=user).exists()