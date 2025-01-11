# subscriptions/serializers.py
from datetime import timedelta
from rest_framework import serializers
from django.utils.timezone import now
from .models import SubscriptionPlan, UserSubscription
from datetime import datetime, timedelta  # Import datetime here

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
        # fields = ['id', 'name', 'duration_in_months', 'price', 'features']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = '__all__'
        extra_kwargs = {
            'end_date': {'required': False}  # Set required to False because we will calculate it
        }

    def validate(self, data):
        # Convert start_date and end_date to date objects if they are datetime
        if 'start_date' in data and isinstance(data['start_date'], datetime.datetime):
            data['start_date'] = data['start_date'].date()
        if 'end_date' in data and isinstance(data['end_date'], datetime.datetime):
            data['end_date'] = data['end_date'].date()
        return data

    def create(self, validated_data):
        # Set start_date to now if not provided
        start_date = validated_data.get('start_date', now().date())
        validated_data['start_date'] = start_date

        # Retrieve subscription_plan and calculate end_date if not provided
        subscription_plan = validated_data.get('subscription_plan')
        if subscription_plan and not validated_data.get('end_date'):
            duration_days = subscription_plan.duration_in_months * 30  # Assuming each month is 30 days
            validated_data['end_date'] = start_date + timedelta(days=duration_days)

        return super().create(validated_data)


class UserSubscriptionDetailSerializer(serializers.ModelSerializer):
    subscription_plan = SubscriptionPlanSerializer()  # Nesting SubscriptionPlanSerializer

    class Meta:
        model = UserSubscription
        fields = '__all__'
        extra_kwargs = {
            'end_date': {'required': False}
        }
