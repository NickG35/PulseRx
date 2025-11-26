from .models import Notifications, ReadStatus

def notification_display(request):
    if request.user.is_authenticated:
        notifications = Notifications.objects.filter(user=request.user).order_by('-time')
        unread_count = notifications.filter(is_read=False).count()

     
        unread_messages = ReadStatus.objects.filter(
            user=request.user,
            read=False
        ).exclude(
            message__sender__role='system'
        ).count()

        return {
            'notifications': notifications,
            'unread_count': unread_count,
            'unread_messages': unread_messages
        }

    return {}