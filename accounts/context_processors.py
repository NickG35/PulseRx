from .models import Notifications, ReadStatus
from pharmacy.models import PharmacistProfile

def notification_display(request):
    if request.user.is_authenticated:
        notifications = Notifications.objects.filter(user=request.user).order_by('-time')
        unread_count = notifications.filter(is_read=False).count()

        if request.user.role == 'pharmacist':
            pharmacist = PharmacistProfile.objects.get(user=request.user)
            pharmacy = pharmacist.pharmacy

            unread_messages = ReadStatus.objects.filter(
                user=pharmacy.user,
                read=False
            ).exclude(
                message__sender__role='system'
            ).count()

        else:
            unread_messages = ReadStatus.objects.filter(
                user=request.user,
                read=False
            ).exclude(
                message__sender__role='system'
            ).count()

        print(f"User: {request.user} | Role: {request.user.role} | Unread messages: {unread_messages}")
        return {
            'notifications': notifications,
            'unread_count': unread_count,
            'unread_messages': unread_messages
        }

    return {}