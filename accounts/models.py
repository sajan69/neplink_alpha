
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    contact = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    last_logged_in = models.DateTimeField(blank=True, null=True)  # Keep last_logged_in field
    last_active = models.DateTimeField(blank=True, null=True)  # New field to track activity
    is_private = models.BooleanField(default=False)
    show_email = models.BooleanField(default=False)
    show_full_name = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    def is_online(self):
        """Determine if the user is online based on last_active timestamp."""
        if self.last_active:
            # Consider a user online if they were active within the last 5 minutes
            return (timezone.now() - self.last_active).total_seconds() < 300
        return False  # User is offline if last_active is None or too old

    def last_online(self):
        """Return the last_active timestamp in a human-readable format like '5 minutes ago'."""
        if self.last_active:
            delta = timezone.now() - self.last_active
            if delta.total_seconds() < 60:
                return 'Just now'
            if delta.total_seconds() < 3600:
                return f'{int(delta.total_seconds() / 60)} minutes ago'
            if delta.total_seconds() < 86400:
                return f'{int(delta.total_seconds() / 3600)} hours ago'
            return f'{int(delta.total_seconds() / 86400)} days ago'
        
        return 'Never logged in'
    
    @property
    def tag_settings(self):
        settings, created = 'post.UserTagSettings'.objects.get_or_create(user=self) 
        return settings


# models.py (continued)
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out

@receiver(user_logged_in)
def set_last_logged_in(sender, user, **kwargs):
    """Set the last_logged_in timestamp when the user logs in."""
    user.last_logged_in = timezone.now()
    user.save(update_fields=['last_logged_in'])  # Save only the last_logged_in field


class Notification(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)  # String-based reference to avoid circular import
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    link = models.URLField(max_length=500, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.title} - { self.user.username if self.user else self.user_type }"
    
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    @classmethod
    def generate_otp(cls, user):
        # Generate a random 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Set expiration time to 10 minutes from now
        expires_at = timezone.now() + timezone.timedelta(minutes=10)
        
        # Create and save the OTP instance
        otp_instance = cls.objects.create(user=user, code=otp, expires_at=expires_at)
        return otp_instance

    def is_valid(self):
        return timezone.now() <= self.expires_at
 