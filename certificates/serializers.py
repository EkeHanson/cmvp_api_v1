from rest_framework import serializers
from .models import Certificate, VerificationLog


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'organization', 'certificate_id', 'client_name', 'issue_date', 'expiry_date', 'pdf_file']

    def validate(self, data):
        # Example of custom validation
        if 'pdf_file' in data and not data['pdf_file'].name.endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            raise serializers.ValidationError("File must be a PDF, JPG, JPEG, or PNG.")
        return data



class VerificationSerializer(serializers.Serializer):
    certificate_id = serializers.CharField()
