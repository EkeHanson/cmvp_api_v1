
from rest_framework import generics, status, viewsets
from .serializers import CertificateSerializer, VerificationSerializer, BackgroundImageSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Organization
from subscription.models import UserSubscription
from .models import BackgroundImage, Certificate, VerificationLog
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.timezone import now
from django.db import models, transaction
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Q

class CertificateCreateView(viewsets.ModelViewSet):
    queryset = Certificate.objects.filter(deleted=False).order_by('id')
    serializer_class = CertificateSerializer
    permission_classes = [AllowAny]  # Consider changing to IsAuthenticated if necessary
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        unique_subscriber_id = request.data.get('organization')

        if not unique_subscriber_id:
            return Response({'error': 'Organization ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        organization = get_object_or_404(Organization, unique_subscriber_id=unique_subscriber_id)

        current_time = now()
        # Check if the trial period has ended and the organization is not subscribed
        if current_time > organization.trial_end_date and not organization.is_subscribed:
            return Response({'error': 'Subscription is required to upload certificates after trial period.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if there is an active subscription
        active_subscription = UserSubscription.objects.filter(
            user=organization,
            end_date__gte=current_time.date()  # Ensures the subscription end date is not in the past
        ).exists()

        if not active_subscription:
            return Response({'error': 'No active subscription. Please renew your subscription to upload certificates.'}, status=status.HTTP_403_FORBIDDEN)

        # Continue with certificate creation if subscription is valid
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()

                # Increment num_certificates_uploaded field
                organization.num_certificates_uploaded = models.F('num_certificates_uploaded') + 1
                organization.save(update_fields=['num_certificates_uploaded'])

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def partial_update(self, request, *args, **kwargs):
        # Retrieve the certificate instance to be updated
        certificate = self.get_object()
        organization = certificate.organization
        
        # Store the previous values to compare them later
        old_data = CertificateSerializer(certificate).data

        # Validate and update the certificate instance
        serializer = self.get_serializer(certificate, data=request.data, partial=True)
        if serializer.is_valid():
            # Save the updated certificate
            updated_certificate = serializer.save()

            # Send email notification if there are any changes
            self.notify_organization_of_changes(organization, old_data, CertificateSerializer(updated_certificate).data)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def notify_organization_of_changes(self, organization, old_data, new_data):
        """
        Sends an email notification to the organization about the updated certificate details.
        """
        # Compare old and new data to find the changes
        changes = []
        for field, old_value in old_data.items():
            new_value = new_data.get(field)
            if old_value != new_value:
                changes.append(f"{field.capitalize()}: {old_value} → {new_value}")

        if changes:
            subject = f"Certificate Updated: {new_data.get('certificate_id')}"
            message = f"""
            <html>
            <body>
                <h3>Hello {organization.name},</h3>
                <p>The following certificate has been updated:</p>
                <ul>
                    <li><strong>Certificate ID:</strong> {new_data.get('certificate_id')}</li>
                    <li><strong>Updated Fields:</strong></li>
                    <ul>
                        {"".join([f"<li>{change}</li>" for change in changes])}
                    </ul>
                </ul>
                <p>If you did not request these changes, please contact support immediately.</p>
                <p>Best regards,</p>
                <p>cmvp Tech Support Team</p>
            </body>
            </html>
            """
            from_email = "ekenehanson@sterlingspecialisthospitals.com"  # Replace with your sender email
            recipient_list = [organization.email]

            send_mail(
                subject,
                '',
                from_email,
                recipient_list,
                fail_silently=False,
                html_message=message
            )


    

# class CertificateCreateView(viewsets.ModelViewSet):
#     queryset = Certificate.objects.filter(deleted=False).order_by('id')
#     serializer_class = CertificateSerializer
#     permission_classes = [AllowAny]  # Consider changing to IsAuthenticated if necessary
#     http_method_names = ['get', 'post', 'put', 'patch', 'delete']

#     def create(self, request, *args, **kwargs):
#         unique_subscriber_id = request.data.get('organization')

#         if not unique_subscriber_id:
#             return Response({'error': 'Organization ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         organization = get_object_or_404(Organization, unique_subscriber_id=unique_subscriber_id)

#         current_time = timezone.now()
#         if current_time > organization.trial_end_date and not organization.is_subscribed:
#             return Response({'error': 'Subscription is required to upload certificates after trial period.'}, status=status.HTTP_403_FORBIDDEN)


#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             with transaction.atomic():
#                 serializer.save()

#                 # Increment num_certificates_uploaded field
#                 organization.num_certificates_uploaded = models.F('num_certificates_uploaded') + 1
#                 organization.save(update_fields=['num_certificates_uploaded'])

#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def partial_update(self, request, *args, **kwargs):
#         # Retrieve the certificate instance to be updated
#         certificate = self.get_object()
#         organization = certificate.organization
        
#         # Store the previous values to compare them later
#         old_data = CertificateSerializer(certificate).data

#         # Validate and update the certificate instance
#         serializer = self.get_serializer(certificate, data=request.data, partial=True)
#         if serializer.is_valid():
#             # Save the updated certificate
#             updated_certificate = serializer.save()

#             # Send email notification if there are any changes
#             self.notify_organization_of_changes(organization, old_data, CertificateSerializer(updated_certificate).data)

#             return Response(serializer.data, status=status.HTTP_200_OK)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def notify_organization_of_changes(self, organization, old_data, new_data):
#         """
#         Sends an email notification to the organization about the updated certificate details.
#         """
#         # Compare old and new data to find the changes
#         changes = []
#         for field, old_value in old_data.items():
#             new_value = new_data.get(field)
#             if old_value != new_value:
#                 changes.append(f"{field.capitalize()}: {old_value} → {new_value}")

#         if changes:
#             subject = f"Certificate Updated: {new_data.get('certificate_id')}"
#             message = f"""
#             <html>
#             <body>
#                 <h3>Hello {organization.name},</h3>
#                 <p>The following certificate has been updated:</p>
#                 <ul>
#                     <li><strong>Certificate ID:</strong> {new_data.get('certificate_id')}</li>
#                     <li><strong>Updated Fields:</strong></li>
#                     <ul>
#                         {"".join([f"<li>{change}</li>" for change in changes])}
#                     </ul>
#                 </ul>
#                 <p>If you did not request these changes, please contact support immediately.</p>
#                 <p>Best regards,</p>
#                 <p>Your Support Team</p>
#             </body>
#             </html>
#             """
#             from_email = "ekenehanson@sterlingspecialisthospitals.com"  # Replace with your sender email
#             recipient_list = [organization.email]

#             send_mail(
#                 subject,
#                 '',
#                 from_email,
#                 recipient_list,
#                 fail_silently=False,
#                 html_message=message
#             )


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


# class CertificateCreateView(viewsets.ModelViewSet):
#     queryset = Certificate.objects.filter(deleted=False).order_by('id')
#     serializer_class = CertificateSerializer
#     permission_classes = [AllowAny]  # Consider changing to IsAuthenticated if necessary
#     http_method_names = ['get', 'post', 'put', 'patch', 'delete']

#     def create(self, request, *args, **kwargs):
#         unique_subscriber_id = request.data.get('organization')

#         if not unique_subscriber_id:
#             return Response({'error': 'Organization ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         organization = get_object_or_404(Organization, unique_subscriber_id=unique_subscriber_id)

#         current_time = timezone.now()
#         if current_time > organization.trial_end_date and not organization.is_subscribed:
#             return Response({'error': 'Subscription is required to upload certificates after trial period.'}, status=status.HTTP_403_FORBIDDEN)


#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             with transaction.atomic():
#                 serializer.save()

#                 # Increment num_certificates_uploaded field
#                 organization.num_certificates_uploaded = models.F('num_certificates_uploaded') + 1
#                 organization.save(update_fields=['num_certificates_uploaded'])

#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def partial_update(self, request, *args, **kwargs):
#         # Retrieve the certificate instance to be updated
#         certificate = self.get_object()
#         organization = certificate.organization
        
#         # Store the previous values to compare them later
#         old_data = CertificateSerializer(certificate).data

#         # Validate and update the certificate instance
#         serializer = self.get_serializer(certificate, data=request.data, partial=True)
#         if serializer.is_valid():
#             # Save the updated certificate
#             updated_certificate = serializer.save()

#             # Send email notification if there are any changes
#             self.notify_organization_of_changes(organization, old_data, CertificateSerializer(updated_certificate).data)

#             return Response(serializer.data, status=status.HTTP_200_OK)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def notify_organization_of_changes(self, organization, old_data, new_data):
#         """
#         Sends an email notification to the organization about the updated certificate details.
#         """
#         # Compare old and new data to find the changes
#         changes = []
#         for field, old_value in old_data.items():
#             new_value = new_data.get(field)
#             if old_value != new_value:
#                 changes.append(f"{field.capitalize()}: {old_value} → {new_value}")

#         if changes:
#             subject = f"Certificate Updated: {new_data.get('certificate_id')}"
#             message = f"""
#             <html>
#             <body>
#                 <h3>Hello {organization.name},</h3>
#                 <p>The following certificate has been updated:</p>
#                 <ul>
#                     <li><strong>Certificate ID:</strong> {new_data.get('certificate_id')}</li>
#                     <li><strong>Updated Fields:</strong></li>
#                     <ul>
#                         {"".join([f"<li>{change}</li>" for change in changes])}
#                     </ul>
#                 </ul>
#                 <p>If you did not request these changes, please contact support immediately.</p>
#                 <p>Best regards,</p>
#                 <p>Your Support Team</p>
#             </body>
#             </html>
#             """
#             from_email = "ekenehanson@sterlingspecialisthospitals.com"  # Replace with your sender email
#             recipient_list = [organization.email]

#             send_mail(
#                 subject,
#                 '',
#                 from_email,
#                 recipient_list,
#                 fail_silently=False,
#                 html_message=message
#             )


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
