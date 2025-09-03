from django.contrib import admin
from .models import CustomAccount, Message, Notifications, Thread

# Register your models here.
admin.site.register(CustomAccount)
admin.site.register(Message)
admin.site.register(Thread)
admin.site.register(Notifications)