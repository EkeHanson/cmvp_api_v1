# subscriptions/serializers.py
from datetime import timedelta
from rest_framework import serializers
from django.utils.timezone import now
from .models import SubscriptionPlan, UserSubscription
import datetime  
from dateutil.relativedelta import relativedelta


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    features = serializers.JSONField()

    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

    def update(self, instance, validated_data):
        # Handle features field explicitly
        features_data = validated_data.pop('features', None)
        if features_data:
            # Ensure that features dictionary is updated with provided data
            instance.features.update(features_data)

        # Continue with regular update
        return super().update(instance, validated_data)


class UserSubscriptionSerializer(serializers.ModelSerializer):
    subscriptionPlan_name = serializers.SerializerMethodField()
    class Meta:
        model = UserSubscription
        fields = '__all__'
        extra_kwargs = {
            'end_date': {'required': False},  # Set required to False because we will calculate it
            'subscribed_amount': {'required': False},  # Optional, can be calculated
            'subscribed_duration': {'required': True}  # Required, as it determines the subscription length
        }

    def get_subscriptionPlan_name(self, obj):
        return obj.subscription_plan.name if obj.subscription_plan else None
    

    def validate(self, data):
        # Ensure subscribed_duration is provided
        if self.instance is None and 'subscribed_duration' not in data:
            raise serializers.ValidationError("Subscribed duration is required.")
        
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
            duration_months = validated_data.get('subscribed_duration')
            validated_data['end_date'] = start_date + relativedelta(months=duration_months)

        # Calculate subscribed_amount if not provided
        if not validated_data.get('subscribed_amount') and subscription_plan:
            validated_data['subscribed_amount'] = subscription_plan.price_per_month * duration_months

        return super().create(validated_data)
    


class UserSubscriptionDetailSerializer(serializers.ModelSerializer):
    subscription_plan = SubscriptionPlanSerializer()  # Nesting SubscriptionPlanSerializer

    class Meta:
        model = UserSubscription
        fields = '__all__'
        extra_kwargs = {
            'end_date': {'required': False}
        }
