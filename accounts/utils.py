from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from accounts.models import Notifications, ReadStatus


def send_notification_with_counts(user, notification_data):
    """
    Send notification via WebSocket with unread counts included.

    This helper ensures all notifications (messages, reminders, prescriptions, etc.)
    automatically include updated unread counts for both notifications and messages.

    Args:
        user: CustomAccount object - the recipient of the notification
        notification_data: dict - the notification payload containing:
            - id: notification ID
            - type: notification type (optional: "reminder", "create_prescription", etc.)
            - other fields specific to notification type

    Returns:
        None - sends notification via WebSocket channel layer
    """
    # Calculate current unread counts for this user
    unread_count = Notifications.objects.filter(user=user, is_read=False).count()
    unread_messages = ReadStatus.objects.filter(user=user, read=False).count()

    # Add counts to notification payload
    notification_data['unread_count'] = unread_count
    notification_data['unread_messages'] = unread_messages

    # Send via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "notification": notification_data
        }
    )
