from rest_framework import generics, status, viewsets
from .models import Certificate, VerificationLog
from .serializers import CertificateSerializer, VerificationSerializer, BackgroundImageSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Organization
from .models import BackgroundImage
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination


class CertificatesByOrganizationView(generics.ListAPIView):
    """
    View to fetch all certificates associated with an organization by unique_subscriber_id.
    """
    serializer_class = CertificateSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination  # Add pagination class

    def get_queryset(self):
        unique_subscriber_id = self.kwargs.get('unique_subscriber_id')
        organization = get_object_or_404(Organization, unique_subscriber_id=unique_subscriber_id)
        return Certificate.objects.filter(organization=organization, deleted=False).order_by('certificate_id')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)  # Use pagination
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)  # Return paginated response
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class CertificateVerificationByOrganizationView(generics.GenericAPIView):
    """
    View for verifying a certificate with organization-specific validation.
    Accepts certificate ID, issue date, and organization unique_subscriber_id.
    """
    permission_classes = [AllowAny]
    serializer_class = VerificationSerializer  # Add this line to avoid the error

    def post(self, request, unique_subscriber_id, *args, **kwargs):
        certificate_id = request.data.get('certificate_id')
        issued_date = request.data.get('issued_date')

        # Normalize the date to 'YYYY-MM-DD'
        try:
            issued_date = datetime.strptime(issued_date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"status": "error", "message": "Invalid date format. Please use 'YYYY-MM-DD'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate inputs
        if not certificate_id or not issued_date:
            return Response(
                {"status": "error", "message": "Certificate ID and issued date are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if organization exists
        try:
            organization = Organization.objects.get(unique_subscriber_id=unique_subscriber_id)
        except Organization.DoesNotExist:
            return Response(
                {"status": "error", "message": "Organization with the provided ID does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if certificate exists for this organization
        certificate = Certificate.objects.filter(
            certificate_id=certificate_id,
            issue_date=issued_date,
            organization=organization,
            deleted=False
        ).first()

        if certificate:
            # Log the verification attempt
            VerificationLog.objects.create(
                certificate=certificate,
                verifier_ip=request.META.get('REMOTE_ADDR')
            )

            # Increment verification count
            certificate.verification_count += 1
            certificate.save()

            # Serialize the certificate details
            serializer = CertificateSerializer(certificate)
            return Response(
                {"status": "valid", "certificate_details": serializer.data},
                status=status.HTTP_200_OK
            )

        # Check why the certificate is invalid
        invalid_reason = "Certificate not found for the provided details."
        if Certificate.objects.filter(certificate_id=certificate_id, deleted=True).exists():
            invalid_reason = "The certificate has been deleted."
        elif Certificate.objects.filter(certificate_id=certificate_id).exists():
            invalid_reason = "The certificate issue date does not match."

        # Return detailed invalid response
        return Response(
            {"status": "invalid", "message": invalid_reason},
            status=status.HTTP_404_NOT_FOUND
        )


# class SoftDeletedCertificateView(generics.ListAPIView):
#     queryset = Certificate.objects.filter(deleted=True).order_by('certificate_id')  # Order by certificate_id (or another field)
#     serializer_class = CertificateSerializer
#     permission_classes = [AllowAny]  # Adjust permission as required

#     def get(self, request, *args, **kwargs):
#         certificates = self.get_queryset()
#         serializer = self.get_serializer(certificates, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
class SoftDeletedCertificateView(generics.ListAPIView):
    """
    View to fetch soft-deleted certificates associated with an organization by unique_subscriber_id.
    """
    serializer_class = CertificateSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination  # Add pagination if necessary

    def get_queryset(self):
        unique_subscriber_id = self.kwargs.get('unique_subscriber_id')
        organization = get_object_or_404(Organization, unique_subscriber_id=unique_subscriber_id)
        return Certificate.objects.filter(organization=organization, deleted=True).order_by('certificate_id')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)  # Handle pagination
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CertificateCreateView(viewsets.ModelViewSet):
    queryset = Certificate.objects.filter(deleted=False).order_by('id')
    serializer_class = CertificateSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        # print(f"POST request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        

        print(f"Serializer errors: {serializer.errors}")  # Logs serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class CertificateVerificationView(generics.GenericAPIView):
#     serializer_class = VerificationSerializer

#     def post(self, request, *args, **kwargs):
#         certificate_id = request.data.get('certificate_id')
#         certificate = Certificate.objects.filter(certificate_id=certificate_id, deleted=False).first()  # Exclude deleted
#         if certificate:
#             VerificationLog.objects.create(certificate=certificate, verifier_ip=request.META.get('REMOTE_ADDR'))
#             certificate.verification_count += 1
#             certificate.save()
#             return Response({"status": "valid"}, status=status.HTTP_200_OK)
#         return Response({"status": "invalid"}, status=status.HTTP_404_NOT_FOUND)


class CertificateSoftDeleteView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, certificate_id, *args, **kwargs):
        certificate = Certificate.objects.filter(certificate_id=certificate_id).first()
        if certificate and not certificate.deleted:
            certificate.soft_delete()
            return Response({"status": "certificate deleted"}, status=status.HTTP_200_OK)
        return Response({"error": "Certificate not found or already deleted"}, status=status.HTTP_404_NOT_FOUND)



class CertificateRestoreView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, certificate_id, *args, **kwargs):
        certificate = Certificate.objects.filter(certificate_id=certificate_id).first()
        if certificate and certificate.deleted:
            certificate.restore()
            return Response({"status": "certificate restored"}, status=status.HTTP_200_OK)
        return Response({"error": "Certificate not found or not deleted"}, status=status.HTTP_404_NOT_FOUND)







class BackgroundImageView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = BackgroundImage.objects.all().order_by('id')
    serializer_class = BackgroundImageSerializer

    def partial_update(self, request, *args, **kwargs):
        unique_subscriber_id = kwargs.get('unique_subscriber_id')
        organization = get_object_or_404(Organization, unique_subscriber_id=unique_subscriber_id)

        # Validate and update the organization object using the serializer
        serializer = self.get_serializer(organization, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()  # Save the updated data
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # print("serializer.errors")
        # print(serializer.data)
        # print("serializer.errors")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        # Validate and save the new organization
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            organization = serializer.save()  # Save the organization object

            # Send confirmation email
            company_email = organization.email  # Assuming the model has an 'email' field
            company_name = organization.name  # Assuming the model has a 'name' field
            # if company_name:
            #     subject = "Account Registration Successful"
            #     message = f"""
            #     <html>
            #     <body>
            #         <h3>Welcome to CMVP, {company_name}!</h3>
            #         <p>Your account has been successfully created. Please confirm your email address by clicking the link below:</p>
            #         <a href="https://new-cmvp-site.vercel.app?email={company_email}">Confirm Email</a>
            #         <p>Thank you for registering with us!</p>
            #     </body>
            #     </html>
            #     """
            #     from_email = "ekenehanson@sterlingspecialisthospitals.com"
            #     recipient_list = [company_email]

            #     send_mail(
            #         subject,
            #         '',
            #         from_email,
            #         recipient_list,
            #         fail_silently=False,
            #         html_message=message,
            #     )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # print("serializer.errors")
        # print(serializer.data)
        # print("serializer.errors")
        # print(serializer.errors)
        # print("serializer.errors")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
