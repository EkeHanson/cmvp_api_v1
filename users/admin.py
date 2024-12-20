from django.contrib import admin
from .models import Organization


@admin.register(Organization)
class CustomUserAdmin(admin.ModelAdmin):
    pass