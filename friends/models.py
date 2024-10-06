from django.db import models
from django.conf import settings

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_requests_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')


class Friendship(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='friendships', 
        on_delete=models.CASCADE
    )
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='friends', 
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')

    def __str__(self):
        return f'{self.user} - {self.friend}'
    
    

