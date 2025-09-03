from django.contrib import admin
from .models import PharmacyProfile, PharmacistProfile, Prescription, Drug

# Register your models here.
admin.site.register(Prescription)
admin.site.register(Drug)


class PharmacistInline(admin.TabularInline):  # or admin.StackedInline for a bigger form
    model = PharmacistProfile
    extra = 1  # how many empty forms to show by default
    fields = ('first_name', 'last_name', 'user')

@admin.register(PharmacyProfile)
class PharmacyProfileAdmin(admin.ModelAdmin):
    list_display = ('pharmacy_name', 'city', 'state')
    inlines = [PharmacistInline]

@admin.register(PharmacistProfile)
class PharmacistProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'pharmacy')
