from rest_framework import serializers
from .models import Certificate, VerificationLog
from rest_framework import serializers
from .models import Certificate, CertificateCategory


class CertificateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateCategory
        fields = '__all__'

class CertificateSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField()
    certificate_category_name = serializers.SerializerMethodField()
    # certificate_category = serializers.UUIDField()  # Accept UUID directly

    class Meta:
        model = Certificate
        fields = "__all__"

    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None
    
    def get_certificate_category_name(self, obj):
        return obj.certificate_category.name if obj.certificate_category else None

    # def validate_certificate_category(self, value):
    #     """Ensure certificate_category is referenced by unique_certificate_category_id."""
    #     try:
    #         return CertificateCategory.objects.get(unique_certificate_category_id=value)
    #     except CertificateCategory.DoesNotExist:
    #         raise serializers.ValidationError("Invalid certificate category UUID provided.")

class VerificationSerializer(serializers.Serializer):
    certificate_id = serializers.CharField()
