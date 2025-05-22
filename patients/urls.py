from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.patient_home, name='patient_home'),
    path('prescriptions', views.prescriptions, name='prescriptions'),
    path('my_pharmacy', views.my_pharmacy, name='my_pharmacy'),
    path('account', views.account, name='account'),
    path('reminders', views.reminders, name='reminders'),
    path('messages', views.messages, name='messages'),
]