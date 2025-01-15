from rest_framework import serializers
from .models import Organization, BackgroundImage
from django.utils.timezone import now, timedelta

class OrganizationSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default='sub_admin')
    password = serializers.CharField(write_only=True)
    # trial_start_date = serializers.DateTimeField(read_only=True)  # Read-only as it is set automatically
    # trial_end_date = serializers.DateTimeField(read_only=True)  # Read-only as it is set automatically

    class Meta:
        model = Organization
        fields = "__all__"

    def create(self, validated_data):
        # Remove the password from the validated data
        password = validated_data.pop('password')
        
        # Set trial dates
        validated_data['trial_start_date'] = now()
        validated_data['trial_end_date'] = now() + timedelta(days=30)

        # Create the user without the password initially
        user = Organization(**validated_data)
        
        # Hash the password using set_password
        user.set_password(password)
        
        # Save the user instance
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

