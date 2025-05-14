from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.patient_home, name='patient_home'),
]