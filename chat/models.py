from datetime import datetime, timezone
from django.db import models
from django.conf import settings

class ChatRoom(models.Model):
    name = models.CharField(max_length=255 ,  blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    is_group_chat = models.BooleanField(default=False)
    active_call = models.OneToOneField('CallLog', null=True, blank=True, on_delete=models.SET_NULL, related_name='active_in_room',default=None)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_participant(self, user):
        return self.participants.filter(id=user.id).exists()

    def get_name(self, user):
        if self.is_group_chat:
            return self.name
        else:
            other_user = self.participants.exclude(id=user.id).first()
            return other_user.username if other_user else self.name
        
    def unread_messages_count(self, user):
        return self.messages.exclude(read_by=user).count()

    def mark_messages_as_read(self, user):
        unread_messages = self.messages.exclude(read_by=user)
        for message in unread_messages:
            message.read_by.add(user)

    def save(self, *args, **kwargs):
        # Save the instance first (to generate an ID)
        super().save(*args, **kwargs)

        # After saving, update the name if it's not a group chat
        if not self.is_group_chat and not self.name:
            participants = self.participants.all()
            if participants.count() == 2:
                participant_names = [user.username for user in participants]
                self.name = " - ".join(participant_names)
                
                # Save again with the updated name (only if necessary)
                super().save(*args, **kwargs)

    def __str__(self):
        return self.name if self.name else "Unnamed ChatRoom"
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_file = models.BooleanField(default=False)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='read_messages', blank=True)
    class Meta:
        ordering = ['timestamp']

    def mark_as_read(self, user):
        self.read_by.add(user)

    def __str__(self):
        return f'{self.sender} - {self.room}'

class CallLog(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='call_logs')
    caller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='caller_logs')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='call_participations')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_time = models.DurationField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('ongoing', 'Ongoing'), ('ended', 'Ended')], default='ongoing')
    agora_channel = models.CharField(max_length=255, null=True, blank=True)
    call_type = models.CharField(max_length=10, choices=[('audio', 'Audio'), ('video', 'Video')], default='video')

    def __str__(self):
        return f'Call in {self.room.name} - {self.status}'
   
    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            self.total_time = self.end_time - self.start_time
        else:
                self.total_time = None
        super().save(*args, **kwargs)

    def end_call(self):
        self.status = 'ended'
        self.end_time = (datetime.now(timezone.utc))
        self.save()
        self.room.active_call = None
        self.room.save()
