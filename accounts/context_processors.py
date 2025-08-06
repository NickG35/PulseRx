from .models import Notifications

def notification_display(request):
    if request.user.is_authenticated:
        notifications = Notifications.objects.filter(user=request.user).order_by('-time')
        return {'notifications': notifications}
    return {}