from django.contrib import admin
from .models import CustomAccount, Message, Notifications

# Register your models here.
admin.site.register(CustomAccount)
admin.site.register(Message)
admin.site.register(Notifications)