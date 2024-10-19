from rest_framework import serializers
from .models import ChatRoom, Message, CallLog
from accounts.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'timestamp', 'is_file', 'file']
        read_only_fields = ['id', 'timestamp']

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'participants', 'is_group_chat', 'active_call', 'created_at', 'messages']
        read_only_fields = ['id', 'created_at']

class CallLogSerializer(serializers.ModelSerializer):
    caller = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = CallLog
        fields = ['id', 'room', 'caller', 'participants', 'start_time', 'end_time', 'total_time', 'status', 'agora_channel', 'call_type']
        read_only_fields = ['id', 'start_time', 'end_time', 'total_time']