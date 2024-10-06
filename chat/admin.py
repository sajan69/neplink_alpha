from django.contrib import admin
from .models import ChatRoom, Message,CallLog

# Register your models here.
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_group_chat', 'created_at']
    list_filter = ['is_group_chat', 'created_at']
    search_fields = ['name']
    filter_horizontal = ['participants']

class MessageAdmin(admin.ModelAdmin):
    list_display = [ 'sender', 'timestamp', 'is_file','file']
    list_filter = ['sender', 'timestamp', 'is_file']
    search_fields = ['sender', 'content']

admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(CallLog)