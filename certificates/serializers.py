from rest_framework import serializers
from .models import Certificate, VerificationLog


# class CertificateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Certificate
#         fields = ['id', 'organization', 'certificate_id', 'client_name', 'issue_date', 'expiry_date', 'pdf_file']

#     def validate(self, data):
#         # Example of custom validation
#         if 'pdf_file' in data and not data['pdf_file'].name.endswith(('.pdf', '.jpg', '.jpeg', '.png')):
#             raise serializers.ValidationError("File must be a PDF, JPG, JPEG, or PNG.")
#         return data


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
