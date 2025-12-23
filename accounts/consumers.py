import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from .models import Message, Thread, Notifications, ReadStatus
from .utils import send_notification_with_counts
from asgiref.sync import sync_to_async

User = get_user_model()

active_notification_users = {}
active_message_users = {}

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.current_thread = None

        if self.user.is_anonymous:
            await self.close()
            return
        
        self.group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        active_notification_users[self.user.id] = self
        await self.accept()
    
    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('type') == 'set_current_thread':
            self.current_thread = str(data['thread_id'])

    
    async def disconnect(self, close_code):
        if self.user.id in active_notification_users:
            del active_notification_users[self.user.id]
            
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    
    async def send_notification(self, event):
        notification = event['notification']

        if notification.get("id") == 0:
            await self.send(text_data=json.dumps({
                "notification": {
                    "unread_count": notification["unread_count"],
                    "unread_messages": notification["unread_messages"],
                }
            }))
            return
        
        await self.send(text_data=json.dumps({
            "notification": notification
        }))


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"] 

        active_message_users[self.user.id] = self

        self.current_thread = None
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'thread_{self.thread_id}'

        await self.channel_layer.group_add(
            self.room_group_name, 
            self.channel_name
        )

        await self.accept()
    
    async def disconnect(self, close_code):
        if self.user.id in active_message_users:
            del active_message_users[self.user.id]

        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            if data.get("type") == "set_current_thread":
                self.current_thread = str(data["thread_id"])
                return

            content = data.get('content')
            if not content:
                print("ERROR: No content in message")
                return

            user = self.scope["user"]

            thread = await self.get_thread(self.thread_id)

            message, notifications = await self.create_message(thread, user, content)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': message.id,
                    'message': content,
                    'sender': f"{user.first_name} {user.last_name}",
                    'timestamp': timezone.localtime(message.timestamp).strftime("%b %d, %I:%M %p"),
                }
            )

            other_participants = await self.get_other_participants(thread, user)
            channel_layer = get_channel_layer()

            # Process notifications for each participant
            for participant in other_participants:
                try:
                    notification_obj = next((n for n in notifications if n.user == participant), None)

                    # Get unread counts for this participant
                    unread_count = await self.get_unread_count(participant)
                    unread_messages = await self.get_unread_messages(participant)

                    notification_data = {
                        "id": notification_obj.id if notification_obj else 0,
                        "unread_count": unread_count,
                        "unread_messages": unread_messages,
                    }

                    if notification_obj:
                        notification_data.update({
                            "thread_id": thread.id,
                            "message_id": message.id,
                            "sender": f"{user.first_name} {user.last_name}",
                            "content": message.content,
                            "timestamp": timezone.localtime(message.timestamp).strftime("%b %d, %I:%M %p"),
                            "is_read": False,
                        })

                    await channel_layer.group_send(
                        f"user_{participant.id}",
                        {
                            "type": "send_notification",
                            "notification": notification_data
                        }
                    )

                except Exception as participant_error:
                    print(f"ERROR processing participant {participant.id}: {participant_error}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            print(f"ERROR in MessageConsumer.receive: {e}")
            import traceback
            traceback.print_exc()
                
    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'id': event['id'],
                'sender': event['sender'],
                'content': event['message'],
                'timestamp': event['timestamp'],
            }))
        except Exception as e:
            print(f"ERROR in MessageConsumer.chat_message: {e}")
            import traceback
            traceback.print_exc()
        
    async def get_thread(self, thread_id):
        try:
            return await Thread.objects.aget(id=thread_id)
        except Thread.DoesNotExist:
            print(f"ERROR: Thread {thread_id} does not exist")
            raise
        except Exception as e:
            print(f"ERROR in get_thread: {e}")
            raise
    
    @sync_to_async
    def get_other_participants(self, thread, user):
        return list(thread.participant.exclude(id=user.id))

    @sync_to_async
    def create_message(self, thread, sender, content):
        message = Message.objects.create(
            thread=thread,
            sender=sender,
            content=content,
            timestamp=timezone.now(),
        )

        notifications = []
        participants = thread.participant.exclude(id=sender.id)

        for participant in participants:
            notif_ws = active_notification_users.get(participant.id)
            is_viewing_thread = notif_ws and getattr(notif_ws, "current_thread", None) == str(thread.id)
            if is_viewing_thread:
                ReadStatus.objects.create(message=message, user=participant, read=True)
            else:
                ReadStatus.objects.create(message=message, user=participant, read=False)
                noti = Notifications.objects.create(user=participant, message=message,is_read=False)
                notifications.append(noti)

        return message, notifications

    @sync_to_async
    def get_unread_count(self, user):
        return Notifications.objects.filter(user=user, is_read=False).count()

    @sync_to_async
    def get_unread_messages(self, user):
        return ReadStatus.objects.filter(user=user, read=False).count()
    

