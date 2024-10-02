from django.db import models
from django.conf import settings

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    is_group_chat = models.BooleanField(default=False)
    active_call = models.BooleanField(default=False)  # New field to track active calls

    created_at = models.DateTimeField(auto_now_add=True)

    def is_participant(self, user):
        return self.participants.filter(id=user.id).exists()

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_file = models.BooleanField(default=False)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender} - {self.room}'

class CallLog(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='call_logs')
    caller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='caller_logs')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receiver_logs')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('ongoing', 'Ongoing'), ('ended', 'Ended')], default='ongoing')

    def __str__(self):
        return f'Call from {self.caller.username} to {self.receiver.username} in {self.room.name}'
