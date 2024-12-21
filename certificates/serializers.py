from rest_framework import serializers
from .models import Certificate, VerificationLog
from rest_framework import serializers
from .models import Certificate

class CertificateSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField()
    

    class Meta:
        model = Certificate
        fields = "__all__"
        # fields = [
        #     'id', 
        #     'organization_name',  # Include the custom field
        #     'certificate_id', 
        #     'client_name', 
        #     'issue_date', 
        #     'expiry_date'
        # ]

    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None



class VerificationSerializer(serializers.Serializer):
    certificate_id = serializers.CharField()
