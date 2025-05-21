from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('register', views.role_picker, name='register'),
    path('register/<str:role>', views.register_role, name='register_role'),
]