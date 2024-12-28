from django.contrib import admin

# Register your models here.
# subscriptions/admin.py

from django.contrib import admin
from .models import SubscriptionPlan

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_in_months', 'price']

# @admin.register(UserSubscription)
# class UserSubscriptionAdmin(admin.ModelAdmin):
#     list_display = ['user', 'subscription_plan', 'start_date', 'end_date', 'is_active']
