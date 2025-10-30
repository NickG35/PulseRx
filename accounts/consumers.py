import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from .models import Message, Thread, Notifications
from asgiref.sync import sync_to_async

User = get_user_model

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print(self.scope['user'])

    
    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    
    async def send_notification(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps({
            "notification": notification
        }))


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'thread_{self.thread_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data['content']
        user = self.scope["user"]

        thread = await self.get_thread(self.thread_id)
        message = await self.create_message(thread, user, content)

        recipient = await self.get_other_participant(thread, user)

        await self.create_notification(recipient, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': content,
                'sender': f"{user.first_name} {user.last_name}" if user.is_authenticated else "Anonymous",
                'timestamp': timezone.localtime(message.timestamp).strftime("%b %d, %I:%M %p"),
            }
        )

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"user_{recipient.id}",
            {
                "type": "send_notification",
                "notification": {
                    "id": message.id,
                    "type": "message",
                    "sender": f"{user.first_name} {user.last_name}",
                    "thread_id": thread.id,
                    "content": content,
                    "timestamp": timezone.localtime(message.timestamp).strftime("%b %d, %I:%M %p"),
                }
            }
        )



    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'content': event['message'],
            'timestamp': event['timestamp'],
        }))
        
    async def get_thread(self, thread_id):
        return await Thread.objects.aget(id=thread_id)
    
    @sync_to_async
    def get_other_participant(self, thread, user):
        return thread.participant.exclude(id=user.id).first()

    async def create_message(self, thread, sender, content):
        return await Message.objects.acreate(
            thread=thread,
            sender=sender,
            content=content,
            timestamp=timezone.now(),
        )
    
    async def create_notification(self, recipient, message):
        await Notifications.objects.acreate(
            user=recipient, 
            message=message,
            is_read=False
        )


