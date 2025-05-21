from django.urls import path
from . import views

urlpatterns = [
    path('login', views.CustomLoginView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.role_picker, name='register'),
    path('register/<str:role>', views.register_role, name='register_role'),
]