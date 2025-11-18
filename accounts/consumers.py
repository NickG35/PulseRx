import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from .models import Message, Thread, Notifications, ReadStatus
from asgiref.sync import sync_to_async

User = get_user_model()

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

        has_pharmacist_profile = await sync_to_async(
            lambda: hasattr(self.user, "pharmacistprofile")
        )()

        if has_pharmacist_profile:
            pharmacy_id = await sync_to_async(
                lambda: self.user.pharmacistprofile.pharmacy.id
            )()
            await self.channel_layer.group_add(
                f"pharmacy_{pharmacy_id}",
                self.channel_name
            )
            
        await self.accept()

    
    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    
    async def send_notification(self, event):
        notification = event['notification']

        unread_count = await sync_to_async(
            lambda: Notifications.objects.filter(user=self.user, is_read=False).count()
        )()

        unread_messages = await sync_to_async(lambda: (
            ReadStatus.objects.filter(
                user=self.user,
                read=False
            )
            .count()
        ))()

        notification["unread_count"] = unread_count
        notification["unread_messages"] = unread_messages
        
        await self.send(text_data=json.dumps({
            "notification": notification
        }))


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"] 
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'thread_{self.thread_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        print(f"Connected user: {self.user.id}, group: user_{self.user.id}")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data['content']
        user = self.scope["user"]

        thread = await self.get_thread(self.thread_id)
        recipient = await self.get_other_participant(thread, user)

        message = await self.create_message(thread, user, recipient, content)

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

        print("Sender:", user)
        print("Recipient:", recipient)
        print("Thread:", thread.id)

        channel_layer = get_channel_layer()
       
        notification_payload = {
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

        await channel_layer.group_send(f"user_{recipient.id}", notification_payload)

        pharmacy_profile = await sync_to_async(lambda: getattr(recipient, "pharmacyprofile", None))()
        if pharmacy_profile:
            pharmacy_id = pharmacy_profile.id
            await channel_layer.group_send(f"pharmacy_{pharmacy_id}", notification_payload)



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

    @sync_to_async
    def create_message(self, thread, sender, recipient, content):
        message = Message.objects.create(
            thread=thread,
            sender=sender,
            recipient=recipient,
            content=content,
            timestamp=timezone.now(),
        )

        participants = thread.participant.exclude(id=sender.id)
        for participant in participants:
            ReadStatus.objects.create(message=message, user=participant, read=False)
        
        return message
    
    @sync_to_async
    def create_notification(self, recipient, message):
        Notifications.objects.create(
            user=recipient, 
            message=message,
            is_read=False
        )

        if hasattr(recipient, "pharmacyprofile"):
            pharmacy = recipient.pharmacyprofile
            pharmacists = pharmacy.pharmacists.select_related("user")
            for pharmacist in pharmacists:
                Notifications.objects.create(
                    user=pharmacist.user,
                    message=message,
                    is_read=False
                )


