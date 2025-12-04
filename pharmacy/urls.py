from django.urls import path
from . import views

urlpatterns = [
    path('admin/dashboard', views.pharmacy_home, name='pharmacy_home'),
    path('admin/regenerate_code', views.regenerate_code, name='regenerate_code'),
    path('pharmacist/dashboard', views.pharmacist_home, name='pharmacist_home'),
    path('create_prescriptions', views.create_prescriptions, name='create_prescriptions'),
    path('refill_prescriptions/<int:prescription_id>', views.refill_form, name='refill_form'),
    path('patient_search/', views.patient_search, name='patient_search'),
    path('medicine_search/', views.medicine_search, name='medicine_search'),
    path('my_patients', views.my_patients, name='my_patients'),
    path('patient_profile/<int:patient_id>', views.patient_profile, name='patient_profile'),
    path('inventory', views.inventory, name='inventory'),
    path('resupply/<int:drug_id>', views.resupply, name='resupply'),
    path('contact_admin/<int:drug_id>', views.contact_admin, name='contact_admin'),
    path('drug_detail/<int:drug_id>', views.drug_detail, name='drug_detail'),
]