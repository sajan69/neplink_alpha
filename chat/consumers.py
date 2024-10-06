
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CallLog, ChatRoom, Message
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')

        if message_type == 'message':
            await self.handle_message(data)
        elif message_type == 'file_share':
            await self.handle_file_share(data)

    async def handle_message(self, data):
        message = data['message']
        user_id = data['user_id']

        message = await self.save_message(user_id, self.room_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.content,
                'user_id': user_id,
                'username': message.sender.username,
                'timestamp': str(message.timestamp),
                'is_file': message.is_file,
                'file_url': message.file.url if message.is_file else None,
                'file_name': message.file.name if message.is_file else None
            }
        )

    async def chat_message(self, event):
        # Send the message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def handle_file_share(self, data):
        # Only broadcast the file, as it is already saved via upload_file view
        user_id = data['user_id']
        file_url = data['file_url']
        file_name = data['file_name']

        # Send the file message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f"Shared file: {file_name}",
                'user_id': user_id,
                'username': self.scope['user'].username,  # Get the username
                'timestamp': str(datetime.now()),
                'is_file': True,
                'file_url': file_url,
                'file_name': file_name
            }
        )

    async def chat_incoming_call(self, event):
        await self.send(text_data=json.dumps({
            'type': 'incoming_call',
            'call_log_id': event['call_log_id'],
            'caller_name': event['caller_name'],
            'call_type': event['call_type'],
        }))

    async def chat_call_ended(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_ended',
            'call_log_id': event['call_log_id'],
            'ended_by': event['ended_by'],
        }))

    async def chat_call_rejected(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_rejected',
            'call_log_id': event['call_log_id'],
            'rejected_by': event['rejected_by'],
        }))
    # @database_sync_to_async
    # def save_file_message(self, user_id, room_id, file_url, file_name):
    #     user = User.objects.get(id=user_id)
    #     room = ChatRoom.objects.get(id=room_id)
        
    #     # Save the file URL in the file field of the Message model
    #     return Message.objects.create(
    #         sender=user,
    #         room=room,
    #         content=f"Shaed file: {file_name}",
    #         is_file=True,
    #         file=file_url  # Save the URL to the file field
    #     )


    @database_sync_to_async
    def save_message(self, user_id, room_id, message):
        user = User.objects.get(id=user_id)
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(sender=user, room=room, content=message)

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'call_{self.room_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.end_call()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']

        handler = getattr(self, f"handle_{message_type}", None)
        if handler:
            await handler(data)
        else:
            logger.warning(f"Unhandled message type: {message_type}")

    async def handle_start_call(self, data):
        user_id = data['user_id']
        call_type = data['call_type']
        user = await self.get_user(user_id)
        room = await self.get_room(self.room_id)

        call_log = await self.create_call_log(user, room, call_type)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_started',
                'user_id': user_id,
                'username': user.username,
                'call_type': call_type,
                'call_log_id': call_log.id
            }
        )

    async def handle_end_call(self, data):
        user_id = data['user_id']
        call_log = await self.get_active_call_log(self.room_id)
        if call_log:
            await self.update_call_log(call_log)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_ended',
                'user_id': user_id
            }
        )

    async def handle_offer(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_offer',
                'offer': data['offer']
            }
        )

    async def handle_answer(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_answer',
                'answer': data['answer']
            }
        )

    async def handle_new_ice_candidate(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'new_ice_candidate',
                'candidate': data['candidate']
            }
        )

    async def handle_file_share(self, data):
        user_id = data['user_id']
        file_url = data['file_url']
        file_name = data['file_name']
        user = await self.get_user(user_id)
        room = await self.get_room(self.room_id)

        message = await self.save_file_message(user, room, file_url, file_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'file_shared',
                'username': user.username,
                'file_url': file_url,
                'file_name': file_name,
                'timestamp': str(message.timestamp)
            }
        )

    async def call_started(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_ended(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_offer(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_answer(self, event):
        await self.send(text_data=json.dumps(event))

    async def new_ice_candidate(self, event):
        await self.send(text_data=json.dumps(event))

    async def file_shared(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def get_room(self, room_id):
        return ChatRoom.objects.get(id=room_id)

    @database_sync_to_async
    def create_call_log(self, user, room, call_type):
        return CallLog.objects.create(
            room=room,
            caller=user,
            receiver=room.participants.exclude(id=user.id).first(),
            call_type=call_type
        )

    @database_sync_to_async
    def get_active_call_log(self, room_id):
        return CallLog.objects.filter(room_id=room_id, status='ongoing').first()

    @database_sync_to_async
    def update_call_log(self, call_log):
        call_log.end_time = timezone.now()
        call_log.status = 'ended'
        call_log.save()

    @database_sync_to_async
    def save_file_message(self, user, room, file_url, file_name):
        return Message.objects.create(
            sender=user,
            room=room,
            content=f"Shared file: {file_name}",
            is_file=True,
            file=file_url
        )