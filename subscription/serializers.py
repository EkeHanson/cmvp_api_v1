# subscriptions/serializers.py

from rest_framework import serializers
from .models import SubscriptionPlan

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
        # fields = ['id', 'name', 'duration_in_months', 'price', 'features']

# class UserSubscriptionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserSubscription
#         fields = ['id', 'user', 'subscription_plan', 'start_date', 'end_date', 'is_active']
