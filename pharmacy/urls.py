from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.pharmacy_home, name='pharmacy_home'),
]