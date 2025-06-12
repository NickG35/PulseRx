from django.urls import path
from . import views

urlpatterns = [
    path('admin/dashboard', views.pharmacy_home, name='pharmacy_home'),
    path('pharmacist/dashboard', views.pharmacist_home, name='pharmacist_home'),
    path('create_prescriptions', views.create_prescriptions, name='create_prescriptions'),
    path('patient_search/', views.patient_search, name='patient_search'),
    path('medicine_search/', views.medicine_search, name='medicine_search'),
    path('my_patients', views.my_patients, name='my_patients'),
    path('pharmacy_account', views.account, name='pharmacy_account'),
    path('inventory', views.inventory, name='inventory'),
    path('drug_detail/<int:drug_id>', views.drug_detail, name='drug_detail'),
    path('pharmacy_messages', views.pharmacy_messages, name='pharmacy_messages'),
]