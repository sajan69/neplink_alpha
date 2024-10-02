from datetime import timezone
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CallLog, ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'chat_{self.room_id}'

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        except Exception as e:
            logger.error(f"Error in connect: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"Error in disconnect: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data['message']
            user_id = data['user_id']

            # Save message to database
            message = await self.save_message(user_id, self.room_id, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message.content,
                    'user_id': user_id,
                    'username': message.sender.username,
                    'timestamp': str(message.timestamp)
                }
            )
        except Exception as e:
            logger.error(f"Error in receive: {e}")

    async def chat_message(self, event):
        try:
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'user_id': event['user_id'],
                'username': event['username'],
                'timestamp': event['timestamp']
            }))
        except Exception as e:
            logger.error(f"Error in chat_message: {e}")

    @database_sync_to_async
    def save_message(self, user_id, room_id, message):
        try:
            user = User.objects.get(id=user_id)
            room = ChatRoom.objects.get(id=room_id)
            return Message.objects.create(sender=user, room=room, content=message)
        except Exception as e:
            logger.error(f"Error in save_message: {e}")
            raise e
        


# consumers.py (CallConsumer)

from .models import CallLog, ChatRoom
from django.contrib.auth import get_user_model

User = get_user_model()

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'call_{self.room_id}'
        
        # Join the call group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the call group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Optionally log call disconnect here (end of call)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'start_call':
            user_id = data['user_id']
            user = await self.get_user(user_id)

            # Notify all users in the group that a call has started
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_started',
                    'username': user.username
                }
            )

        elif message_type == 'end_call':
            # Notify all users that the call has ended
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_ended'
                }
            )

    async def call_started(self, event):
        username = event['username']

        # Notify WebSocket that the call has started
        await self.send(text_data=json.dumps({
            'type': 'call_started',
            'username': username
        }))

    async def call_ended(self, event):
        # Notify WebSocket that the call has ended
        await self.send(text_data=json.dumps({
            'type': 'call_ended'
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)
