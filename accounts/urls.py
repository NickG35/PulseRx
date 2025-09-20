from django.urls import path
from . import views

urlpatterns = [
    path('login', views.CustomLoginView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.role_picker, name='register'),
    path('register/<str:role>', views.register_role, name='register_role'),
    path('account_settings', views.account_settings, name='account_settings'),
    path('messages', views.account_messages, name='messages'),
    path('thread/<int:thread_id>', views.thread_view, name='threads'),
    path('send_messages', views.send_messages, name='send_messages'),
    path('message_search', views.message_search, name='message_search'),
    path('patient_thread', views.patient_thread, name='patient_thread'),
    path('delete_notification', views.delete_notification, name='delete_notification'),
    path('read_notification', views.read_notification, name='read_notification')
]