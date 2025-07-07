from django.contrib import admin
from .models import CustomAccount, Message

# Register your models here.
admin.site.register(CustomAccount)
admin.site.register(Message)