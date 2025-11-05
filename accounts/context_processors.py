from .models import Notifications

def notification_display(request):
    if request.user.is_authenticated:
        notifications = Notifications.objects.filter(user=request.user).order_by('-time')
        unread_count = notifications.filter(is_read=False).count()
        return {
            'notifications': notifications,
            'unread_count': unread_count
        }
    return {}