from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.patient_home, name='patient_home'),
    path('prescriptions', views.prescriptions, name='prescriptions'),
    path('my_pharmacy', views.my_pharmacy, name='my_pharmacy'),
    path('account', views.account, name='account'),
    path('reminders', views.reminders, name='reminders'),
    path('reminder_suggestions', views.reminder_suggestions, name='reminder_suggestions'),
    path('toggle_reminder', views.toggle_reminder, name='toggle_reminder'),
    path('toggle_time', views.toggle_time, name='toggle_time'),
    path('unarchive', views.unarchive, name='unarchive'),
    path('delete_reminder', views.delete_reminder, name='delete_reminder'),
    path('edit_reminder', views.edit_reminder, name='edit_reminder')
]