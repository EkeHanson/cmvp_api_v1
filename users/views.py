from rest_framework import viewsets, status, generics, views
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Organization, BackgroundImage
from .serializers import  LoginSerializer, OrganizationSerializer, BackgroundImageSerializer, OrganizationSubscriptionSerializer
from rest_framework.permissions import AllowAny
from .serializers import LoginSerializer
from rest_framework.response import Response
from .serializers import  ResetPasswordSerializer
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from subscription.models import UserSubscription
import base64
from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework.pagination import PageNumberPagination
from twilio.rest import Client
from django.utils.timezone import now
import re
class OrganizationPagination(PageNumberPagination):
    page_size = 10  # 10 results per page
    page_size_query_param = 'page_size'
    max_page_size = 1000  # Maximum page size is 1000


class OrganizationSubscriptionView(APIView):
    permission_classes = [AllowAny]
    pagination_class = OrganizationPagination

    # def get(self, request, *args, **kwargs):
    #     organizations = Organization.objects.all().order_by('id')
    #     data = []

    #     for org in organizations:
    #         # Check if the organization has an active subscription
    #         subscription = UserSubscription.objects.filter(user=org, is_active=True).first()

    #         if subscription:
    #             subscription_data = {
    #                 'id': org.id,
    #                 'name': org.name,
    #                 'phone': org.phone,
    #                 'email': org.email,
    #                 'address': org.address,
    #                 'date_joined': org.date_joined,
    #                 'subscription_plan_name': subscription.subscription_plan.name,
    #                 'subscription_start_time': subscription.start_date,
    #                 'subscription_end_time': subscription.end_date,
    #                 'subscription_duration': (subscription.end_date - subscription.start_date).days,
    #                 'num_certificates_uploaded': org.num_certificates_uploaded,
    #                 'unique_subscriber_id': org.unique_subscriber_id
    #             }
    #         else:
    #             subscription_data = {
    #                 'id': org.id,
    #                 'name': org.name,
    #                 'phone': org.phone,
    #                 'email': org.email,
    #                 'address': org.address,
    #                 'date_joined': org.date_joined,
    #                 'subscription_plan_name': ' 30-Day Trial',
    #                 'subscription_start_time': org.trial_start_date,
    #                 'subscription_end_time': org.trial_end_date,
    #                 'subscription_duration': (org.trial_end_date - org.trial_start_date).days,
    #                 'num_certificates_uploaded': org.num_certificates_uploaded,
    #                 'unique_subscriber_id': org.unique_subscriber_id
    #             }

    #         data.append(subscription_data)

    #     return Response(data)
    def get(self, request, *args, **kwargs):
        organizations = Organization.objects.all().order_by('id')
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(organizations, request)

        data = []
        for org in result_page:
            # Check if the organization has an active subscription
            subscription = UserSubscription.objects.filter(user=org, is_active=True).first()

            if subscription:
                subscription_data = {
                    'id': org.id,
                    'name': org.name,
                    'phone': org.phone,
                    'email': org.email,
                    'address': org.address,
                    'date_joined': org.date_joined,
                    'subscription_plan_name': subscription.subscription_plan.name,
                    'subscription_start_time': subscription.start_date,
                    'subscription_end_time': subscription.end_date,
                    'subscription_duration': (subscription.end_date - subscription.start_date).days,
                    'num_certificates_uploaded': org.num_certificates_uploaded,
                    'unique_subscriber_id': org.unique_subscriber_id
                }
            else:
                subscription_data = {
                    'id': org.id,
                    'name': org.name,
                    'phone': org.phone,
                    'email': org.email,
                    'address': org.address,
                    'date_joined': org.date_joined,
                    'subscription_plan_name': '30-Day Trial',
                    'subscription_start_time': org.trial_start_date,
                    'subscription_end_time': org.trial_end_date,
                    'subscription_duration': (org.trial_end_date - org.trial_start_date).days,
                    'num_certificates_uploaded': org.num_certificates_uploaded,
                    'unique_subscriber_id': org.unique_subscriber_id
                }

            data.append(subscription_data)

        return paginator.get_paginated_response(data)

class GetOrganizationBySubscriberIdView(APIView):
    """
    API view to fetch an organization by its unique_subscriber_id.
    """
    permission_classes = [AllowAny]

    def get(self, request, unique_subscriber_id):
        organization = get_object_or_404(Organization, unique_subscriber_id=unique_subscriber_id)
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class OrganizationView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Organization.objects.all().order_by('id')
    serializer_class = OrganizationSerializer

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
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            organization = serializer.save()

            verification_link = f"{settings.DEFAULT_WEB_PAGE_BASE_URL}/verification-code/:{organization.verification_token}:/{organization.email}"

            subject = "CMVP Registration Verification Email"
            message = f"""

            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>CMVP Registration Email Verification </title>
            </head>
            <body style="margin: 0; padding: 0; font-family: Poppins, sans-serif; font-size: 15px; font-weight: 400; line-height: 1.5; width: 100%; background: #081C15; color: #fff; overflow-x: hidden; min-height: 100vh; text-align: center;">
                <div style="position: relative; width: 100%; height: auto; min-height: 100%; display: flex; justify-content: center;">
                    <div style="position: relative; width: 700px; height: auto; text-align: center; padding: 80px 0px; padding-bottom: 0px !important;">
                        <img src="https://cmvp.net/assets/logo-lit-Cz1jHCfU.png" style="max-width: 150px; margin-bottom: 80px;" />
                        <h3 style="font-size: 30px; font-weight: 700;">{organization.name}!</h3>
                        <p style="margin-top: 10px; color:#D8F3DC;">Click the link below to verify your email:</p>
                        <a href="{verification_link}" style="position: relative; margin: 30px 0px; display: inline-flex; align-items: center; justify-content: center; text-align: center; padding: 10px 30px; background-color: #FE6601; color: #fff; margin-top: 50px; border-radius: 8px; border:1px solid #FE6601; text-decoration: none; transition:all 0.3s ease-in-out;">Verify Email</a>
                        <p style="margin-top: 10px; color:#D8F3DC;">Or copy and paste this token on the verification page:</p>
                        <h1 style="font-size: 40px; font-weight: 700; color: #FE6601; margin-top: 30px;">{organization.verification_token}</h1>
                        <footer style="position: relative; width: 100%; height: auto; margin-top: 50px; padding: 30px; background-color: rgba(255,255,255,0.1);">
                            <h5>Thanks for using our platform</h5>
                            <p style="font-size: 13px !important; color: #fff !important;">You can reach us via <a href="mailto:support@cmvp.net" style="color:#D8F3DC !important; text-decoration: underline !important;">support@cmvp.net</a>. We are always available to answer your questions.</p>
                            <p style="font-size: 13px !important; color: #fff !important;">© <script>document.write(new Date().getFullYear());</script> CMVP. All rights reserved.</p>
                        </footer>
                    </div>
                </div>
            </body>
            </html>

            """
            send_mail(
                subject,
                '',
                settings.DEFAULT_FROM_EMAIL,
                [organization.email],
                fail_silently=False,
                html_message=message,
            )

            return Response({"message": "Please verify your email."}, status=status.HTTP_201_CREATED)

        # Debugging: Print error details in logs
        print("Serializer errors:", serializer.errors)

        # Return structured error messages
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        token = request.data.get("token")
        organization = get_object_or_404(Organization, verification_token=token)

        if organization:
            organization.is_verified = True
            organization.verification_token = None  # Remove token after verification
            organization.save()

            # Retrieve the user linked to this organization
            user = get_user_model().objects.get(email=organization.email)

            # Generate authentication tokens
            refresh = RefreshToken.for_user(user)
            login_time = now()

            return Response({
                'message': "Email verified successfully!",
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'email': user.email,
                'userId': user.id,
                'name': user.name,
                'user_role': user.role,
                'phone': user.phone,
                'address': user.address,
                'login_time': login_time.strftime('%I:%M %p'),
                'unique_subscriber_id': user.unique_subscriber_id,
                'date_joined': user.date_joined,
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)



class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
            email = request.data.get("email")

            if not email:
                return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

            organization = Organization.objects.filter(email=email).first()

            if not organization:
                return Response({"error": "Organization not found"}, status=status.HTTP_404_NOT_FOUND)

            if organization.is_verified:
                return Response({"error": "Email is already verified"}, status=status.HTTP_400_BAD_REQUEST)

            # Generate a consistent 6-digit token
            organization.generate_verification_token()

            verification_link = f"{settings.DEFAULT_WEB_PAGE_BASE_URL}/verification-code/{organization.verification_token}/{organization.email}"

            subject = "CMVP Registration Verification Email"
            message = f"""
                <html>
                    <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <title>CMVP Registration Email Verification </title>
                        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
                    </head>
                    <body style="margin: 0; padding: 0; font-family: Poppins, sans-serif; font-size: 15px; font-weight: 400; line-height: 1.5; width: 100%; background: #081C15; color: #fff; overflow-x: hidden; min-height: 100vh; z-index: 1;">
                        <div style="position: relative; width: 100%; height: auto; min-height: 100%; display: flex; justify-content: center;">
                            <div style="position: relative; width: 700px; height: auto; text-align: center; padding: 80px 0px;">
                                <img src="https://cmvp.net/assets/logo-lit-Cz1jHCfU.png" style="max-width: 150px; margin-bottom: 80px;" />
                                <h3 style="font-size: 30px; font-weight: 700;">Welcome, {organization.name}!</h3>
                                <p style="margin-top: 10px; color:#D8F3DC;">Click the link below to verify your email:</p>
                                <a href="{verification_link}" style="position: relative; margin: 30px 0px; display: inline-flex; align-items: center; justify-content: center; text-align: center; padding: 10px 30px; background-color: #FE6601; color: #fff; margin-top: 50px; border-radius: 8px; border:1px solid #FE6601; transition: all 0.3s ease-in-out; text-decoration: none;">Verify Email</a>
                                <p style="color: #6b7280; font-size: 18px; margin-top: 10px;">Or copy and paste this token on the verification page:</p>
                                <h1 style="font-size: 40px; font-weight: 700; color: #FE6601; margin-top: 30px;">{organization.verification_token}</h1>
                                 <footer style="position: relative; width: 100%; height: auto; margin-top: 50px; padding: 30px; background-color: rgba(255,255,255,0.1);">
                                    <h5>Thanks for using our platform</h5>
                                    <p style="font-size: 13px !important; color: #fff !important;">You can reach us via <a href="mailto:support@cmvp.net" style="color:#D8F3DC !important; text-decoration: underline !important;">support@cmvp.net</a>. We are always available to answer your questions.</p>
                                    <p style="font-size: 13px !important; color: #fff !important;">© <script>document.write(new Date().getFullYear());</script> CMVP. All rights reserved.</p>
                                </footer>
                            </div>
                        </div>
                    </body>
                </html>
            """

            send_mail(
                subject, '', settings.DEFAULT_FROM_EMAIL, [organization.email], 
                fail_silently=False, html_message=message
            )

            return Response({"message": "Verification code resent to your email."}, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = get_user_model().objects.get(email=email)

            if not user.check_password(password):
                return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_verified:
                return Response(
                    {"error": "User is not verified. Please check your email for verification."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Generate refresh token for the user
            refresh = RefreshToken.for_user(user)
            login_time = now()

            # Extract user-agent from request headers
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            device_name, browser_name = self.extract_device_and_browser(user_agent)

            # Send login notification email
            subject = "Login Notification"
            message = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>CMVP LOGIN EMAIL</title>
            </head>
            <body style="margin: 0; padding: 0; font-family: Poppins, sans-serif; font-size: 15px; font-weight: 400; line-height: 1.5; width: 100%; background: #081C15; color: #fff; overflow-x: hidden; min-height: 100vh; z-index: 1;">
                <div style="position: relative; width: 100%; height: auto; min-height: 100%; display: flex; justify-content: center;">
                    <div style="position: relative; width: 700px; height: auto; text-align: center; padding: 80px 0px; padding-bottom: 0px !important;">
                        <img src="https://cmvp.net/assets/logo-lit-Cz1jHCfU.png" style="max-width: 150px; margin-bottom: 80px;" />
                            <h3 style="font-size: 30px; font-weight: 700;">Hello {user.name},</h3>
                            <p style="margin-top: 10px; color:#D8F3DC;">Your account was logged into at {login_time.strftime('%I:%M %p')}.</p>
                            <p style="margin-top: 10px; color:#D8F3DC;"><strong style="color: #FE6601 !important;">Device:</strong> {device_name}</p>
                            <p style="margin-top: 10px; color:#D8F3DC;"><strong style="color: #FE6601 !important;">Browser:</strong> {browser_name}</p>
                            <p style="margin-top: 10px; color:#D8F3DC;">If this wasn't you, please reset your password immediately.</p>
                            <footer style="position: relative; width: 100%; height: auto; margin-top: 50px; padding: 30px; background-color: rgba(255,255,255,0.1);">
                                <h5>Thanks you for using our platform</h5>
                                <p style="font-size: 13px !important; color: #fff !important;">You can reach us via <a href="mailto:support@cmvp.net" style="color:#D8F3DC !important; text-decoration: underline !important;">support@cmvp.net</a>. We are always available to answer your questions.</p>
                                <p style="font-size: 13px !important; color: #fff !important;">
                                    ©
                                <script>
                                    document.write(new Date().getFullYear());
                                </script>
                                CMVP. All rights reserved.
                                </p>
                            </footer>
                        </div>
                </div>
            </body>
            </html>
            
            """

            send_mail(
                subject, "",
                settings.DEFAULT_FROM_EMAIL, [user.email], 
                fail_silently=False,
                html_message=message
            )

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "email": user.email,
                    "userId": user.id,
                    "name": user.name,
                    "user_role": user.role,
                    "phone": user.phone,
                    "address": user.address,
                    "login_time": login_time.strftime("%I:%M %p"),
                    "unique_subscriber_id": user.unique_subscriber_id,
                    "date_joined": user.date_joined,
                },
                status=status.HTTP_200_OK,
            )

        except get_user_model().DoesNotExist:
            return Response({"error": "User does not exist. Please sign up."}, status=status.HTTP_404_NOT_FOUND)

    def extract_device_and_browser(self, user_agent):
        """
        Extracts device name and browser name from the user-agent string.
        """
        device_name = "Unknown Device"
        browser_name = "Unknown Browser"

        # Simple regex to extract browser name from the user-agent
        browser_patterns = [
            (r'Chrome/([0-9.]+)', 'Chrome'),
            (r'Firefox/([0-9.]+)', 'Firefox'),
            (r'Safari/([0-9.]+)', 'Safari'),
            (r'Edge/([0-9.]+)', 'Edge'),
            (r'Opera/([0-9.]+)', 'Opera'),
            (r'MSIE ([0-9.]+)', 'Internet Explorer'),
        ]

        # Check if any browser pattern matches
        for pattern, browser in browser_patterns:
            match = re.search(pattern, user_agent)
            if match:
                browser_name = browser
                break

        # Device name (simplified method, can be enhanced with more patterns)
        if "Mobile" in user_agent:
            device_name = "Mobile Device"
        elif "Tablet" in user_agent:
            device_name = "Tablet"
        else:
            device_name = "Desktop"

        return device_name, browser_name
    
    
class ResetPasswordView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        # Check if email is provided
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Find user with provided email
        try:
            user = Organization.objects.get(email=email)
        except Organization.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Generate reset token and UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.DEFAULT_WEB_PAGE_BASE_URL}/forgotten_pass_reset/{uid}/{token}/"

        # Prepare email content
        subject = 'Password Reset Request'

        # Use a proper HTML template for the message
        message = f"Please click the following link to reset your password: {reset_link}"
        html_message = f'''
                <html>
                    <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <title>CMVP Registration Email Verification </title>
                        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
                    </head>
                    <body style="margin: 0; padding: 0; font-family: Poppins, sans-serif; font-size: 15px; font-weight: 400; line-height: 1.5; width: 100%; background: #081C15; color: #fff; overflow-x: hidden; min-height: 100vh; z-index: 1;">
                        <div style="position: relative; width: 100%; height: auto; min-height: 100%; display: flex; justify-content: center;">
                            <div style="position: relative; width: 700px; height: auto; text-align: center; padding: 80px 0px;">
                                <img src="https://cmvp.net/assets/logo-lit-Cz1jHCfU.png" style="max-width: 150px; margin-bottom: 80px;" />
                                <h3 style="font-size: 30px; font-weight: 700;">Please click on the link below to reset your password!</h3>
                                <p style="margin-top: 10px; color:#D8F3DC;"><a href="{reset_link}"><strong>Reset Password</strong></a></p>
                                
                                <p style="color: #6b7280; font-size: 18px; margin-top: 10px;">Note this email will expire in five (5) minutes.</p>

                                 <footer style="position: relative; width: 100%; height: auto; margin-top: 50px; padding: 30px; background-color: rgba(255,255,255,0.1);">
                                    <h5>Thanks for using our platform</h5>
                                    <p style="font-size: 13px !important; color: #fff !important;">You can reach us via <a href="mailto:support@cmvp.net" style="color:#D8F3DC !important; text-decoration: underline !important;">support@cmvp.net</a>. We are always available to answer your questions.</p>
                                    <p style="font-size: 13px !important; color: #fff !important;">© <script>document.write(new Date().getFullYear());</script> CMVP. All rights reserved.</p>
                                </footer>
                            </div>
                        </div>
                    </body>
                </html>
        '''

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        # Send the email with the HTML content
        send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

        return Response({'message': 'Password reset link has been sent to your email'}, status=status.HTTP_200_OK)


class ConfirmResetPasswordView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token, *args, **kwargs):

        serializer = ResetPasswordSerializer(data=request.data)

        # print(request.data)

        if not serializer.is_valid():
            print(serializer.errors)  # Log the exact errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Organization.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Organization.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            # Token is valid; proceed with password reset
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid token or user'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_contact_email(request):
    if request.method == 'POST':
        email = request.data.get('email')
        full_name = request.data.get('fullName')
        phone_number = request.data.get('phone')
        interest_service = request.data.get('serviceInterest')
        message_body = request.data.get('message')

        if email:
            subject = 'Contact Form Submission'
            message = f'''

            <html>
                    <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <title>CMVP Registration Email Verification </title>
                        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
                    </head>
                    <body style="margin: 0; padding: 0; font-family: Poppins, sans-serif; font-size: 15px; font-weight: 400; line-height: 1.5; width: 100%; background: #081C15; color: #fff; overflow-x: hidden; min-height: 100vh; z-index: 1;">
                        <div style="position: relative; width: 100%; height: auto; min-height: 100%; display: flex; justify-content: center;">
                            <div style="position: relative; width: 700px; height: auto; text-align: center; padding: 80px 0px;">
                                <img src="https://cmvp.net/assets/logo-lit-Cz1jHCfU.png" style="max-width: 150px; margin-bottom: 80px;" />
                                <h3 style="font-size: 30px; font-weight: 700;">Contact Form Submission</h3>
                                <p style="margin-top: 10px; color:#D8F3DC;">Full Name:</strong> {full_name}</p>
                                <p style="margin-top: 10px; color:#D8F3DC;"><strong>Phone Number:</strong> {phone_number}</p>
                                
                                <p style="color: #6b7280; font-size: 18px; margin-top: 10px;"><strong>Interest Service:</strong> {interest_service}.</p>
                                <p style="color: #6b7280; font-size: 18px; margin-top: 10px;">Message:</strong> {message_body}</p>

                                 <footer style="position: relative; width: 100%; height: auto; margin-top: 50px; padding: 30px; background-color: rgba(255,255,255,0.1);">
                                    <h5>Thanks for using our platform</h5>
                                    <p style="font-size: 13px !important; color: #fff !important;">You can reach us via <a href="mailto:support@cmvp.net" style="color:#D8F3DC !important; text-decoration: underline !important;">support@cmvp.net</a>. We are always available to answer your questions.</p>
                                    <p style="font-size: 13px !important; color: #fff !important;">© <script>document.write(new Date().getFullYear());</script> CMVP. All rights reserved.</p>
                                </footer>
                            </div>
                        </div>
                    </body>
                </html>
            '''
            recipient_list = ['info@prolinaceltd.com', 'enterprise@prolianceltd.com']

            from_email = settings.DEFAULT_FROM_EMAIL

            send_mail(subject, '', from_email, recipient_list, fail_silently=False, html_message=message)
            return Response({'message': 'Email sent successfully'})
        else:
            return Response({'error': 'Email not provided in POST data'}, status=400)
    else:
        return Response({'error': 'Invalid request method'}, status=400)


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
            # company_email = organization.email  # Assuming the model has an 'email' field
            # company_name = organization.name  # Assuming the model has a 'name' field
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


class BackgroundImageByOrganizationView(generics.ListAPIView):
    """
    View to fetch all certificates associated with an organization by unique_subscriber_id.
    """
    serializer_class = BackgroundImageSerializer
    permission_classes = [AllowAny]
    #pagination_class = PageNumberPagination  # Add pagination class

    def get_queryset(self):
        unique_subscriber_id = self.kwargs.get('unique_subscriber_id')
        organization = get_object_or_404(Organization, unique_subscriber_id=unique_subscriber_id)
        return BackgroundImage.objects.filter(organization=organization).order_by('id')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)  # Use pagination
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)  # Return paginated response
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SetSelectedBackgroundImageView(APIView):
    """
    View to set a specific background image as the selected background for an organization.
    """
    permission_classes = [AllowAny]  # Require authentication

    def post(self, request, *args, **kwargs):
        background_image_id = kwargs.get('id')
        background_image = get_object_or_404(BackgroundImage, id=background_image_id)
        
        # Unselect all other background images for the organization
        BackgroundImage.objects.filter(organization=background_image.organization).update(is_selected=False)
        
        # Set the selected background image
        background_image.is_selected = True
        background_image.save()

        return Response({"message": "Background image set as selected."}, status=status.HTTP_200_OK)


class GetSelectedBackgroundImageView(APIView):
    """
    View to fetch the selected background image for an organization.
    """
    permission_classes = [AllowAny]  # Require authentication
    def get(self, request, *args, **kwargs):
        unique_subscriber_id = kwargs.get('unique_subscriber_id')
        organization = get_object_or_404(Organization, unique_subscriber_id=unique_subscriber_id)
        
        selected_bg_image = BackgroundImage.get_selected_background(organization)

        if selected_bg_image:
            # Return the background image details (e.g., URL)
            return Response({
                'background_image': selected_bg_image.backgroundImage.url
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No selected background image found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_sms(request):
    account_sid = 'AC500ccdccd6ebc368dc82d8e36731e000'  # Your Twilio Account SID
    auth_token = 'cc78f85b4552f9c448fcfbac0226b72c'    # Your Twilio Auth Token

    if request.method == 'POST':
        phone_number = request.data.get('phone')
        message_body = request.data.get('message')

        if not phone_number or not message_body:
            return Response({"error": "Phone number and message are required."}, status=400)

        try:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                from_='+15074426880',  # Your Twilio phone number
                body=message_body,
                to=phone_number
            )

            return Response({"success": True, "message_sid": message.sid}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

