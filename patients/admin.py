from django.contrib import admin
from .models import PatientProfile, MedicationReminder, ReminderTime

# Register your models here.
class ReminderTimeInline(admin.TabularInline):
    model = ReminderTime
    extra = 1      # Show 1 empty form by default
    max_num = 5    # Allow a max of 5 total ReminderTime entries

class MedicationReminderAdmin(admin.ModelAdmin):
    inlines = [ReminderTimeInline]

admin.site.register(PatientProfile)
admin.site.register(MedicationReminder, MedicationReminderAdmin)
