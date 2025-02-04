from rest_framework import serializers
from .models import Organization, BackgroundImage
from django.utils.timezone import now, timedelta
from rest_framework import serializers
from .models import Organization
from subscription.models import  UserSubscription
import uuid
from rest_framework import serializers
from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default='sub_admin')
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Organization
        fields = "__all__"

    def create(self, validated_data):
        password = validated_data.pop("password")

        # Set trial dates
        validated_data['trial_start_date'] = now()
        validated_data['trial_end_date'] = now() + timedelta(days=30)

        user = Organization(**validated_data)
        user.set_password(password)

        # Generate a 6-digit verification token
        user.generate_verification_token()

        user.save()
        
        return user



  
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, 
        min_length=8, 
        required=True,
        error_messages={
            'required': 'New password is required.',
            'min_length': 'Password must be at least 8 characters long.'
        }
    )


class BackgroundImageSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BackgroundImage
        fields = "__all__"

    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None


class OrganizationSubscriptionSerializer(serializers.ModelSerializer):
    subscription_plan_name = serializers.CharField(source='usersubscription.subscription_plan.name', default="Using Free Plan")
    subscription_start_time = serializers.DateTimeField(source='usersubscription.start_date', default=None)
    subscription_end_time = serializers.DateTimeField(source='usersubscription.end_date', default=None)
    subscription_duration = serializers.SerializerMethodField()
    num_certificates_uploaded = serializers.IntegerField()

    class Meta:
        model = Organization
        fields = ['name', 'subscription_plan_name', 'subscription_start_time', 'subscription_end_time', 'subscription_duration', 'num_certificates_uploaded', 'unique_subscriber_id']

    def get_subscription_duration(self, obj):
        subscription = obj.usersubscription.filter(is_active=True).first()
        if subscription:
            start_date = subscription.start_date
            end_date = subscription.end_date
            if start_date and end_date:
                duration = end_date - start_date
                return duration.days
        return "Free Trial"
