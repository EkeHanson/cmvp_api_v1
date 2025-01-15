from rest_framework import serializers
from .models import Certificate, VerificationLog
from rest_framework import serializers
from .models import Certificate

class CertificateSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Certificate
        fields = "__all__"

    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None


class VerificationSerializer(serializers.Serializer):
    certificate_id = serializers.CharField()
