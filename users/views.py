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
import africastalking
from twilio.rest import Client

class OrganizationSubscriptionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        organizations = Organization.objects.all().order_by('id')
        data = []

        for org in organizations:
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
                    'subscription_plan_name': ' 30-Day Trial',
                    'subscription_start_time': org.trial_start_date,
                    'subscription_end_time': org.trial_end_date,
                    'subscription_duration': (org.trial_end_date - org.trial_start_date).days,
                    'num_certificates_uploaded': org.num_certificates_uploaded,
                    'unique_subscriber_id': org.unique_subscriber_id
                }

            # Convert logo to base64 if it exists
            # if org.logo:
            #     try:
            #         logo_content = org.logo.read()
            #         subscription_data['logo'] = base64.b64encode(logo_content).decode('utf-8')
            #     except Exception as e:
            #         subscription_data['logo'] = None
            # else:
            #     subscription_data['logo'] = None

            data.append(subscription_data)

        return Response(data)


# class OrganizationSubscriptionView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request, *args, **kwargs):
#         organizations = Organization.objects.all().order_by('id')
#         data = []

#         for org in organizations:
#             # Check if the organization has an active subscription
#             subscription = UserSubscription.objects.filter(user=org, is_active=True).first()

#             if subscription:
#                 # If subscription exists and is active, get details
#                 data.append({
#                     'id': org.id,
#                     'name': org.name,
#                     'phone': org.phone,
#                     'email': org.email,
#                     'address': org.address,
#                     'logo': org.logo,
#                     'date_joined': org.date_joined,
#                     'subscription_plan_name': subscription.subscription_plan.name,
#                     'subscription_start_time': subscription.start_date,
#                     'subscription_end_time': subscription.end_date,
#                     'subscription_duration': (subscription.end_date - subscription.start_date).days,
#                     'num_certificates_uploaded': org.num_certificates_uploaded,
#                     'unique_subscriber_id': org.unique_subscriber_id
#                 })
#             else:
#                 # If no active subscription, assume they are using the free plan
#                 data.append({
#                     'id': org.id,
#                     'name': org.name,
#                     'phone': org.phone,
#                     'email': org.email,
#                     'address': org.address,
#                     'logo': org.logo,
#                     'date_joined': org.date_joined,
#                     'subscription_plan_name': 'Using Free Plan',
#                     'subscription_start_time': None,
#                     'subscription_end_time': None,

#                     'subscription_duration': (org.trial_end_date - org.trial_start_date).days,

#                     'num_certificates_uploaded': org.num_certificates_uploaded,
#                     'unique_subscriber_id': org.unique_subscriber_id
#                 })

#         return Response(data)


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
        # Validate and save the new organization
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            organization = serializer.save()  # Save the organization object

            # Send confirmation email
            company_email = organization.email  # Assuming the model has an 'email' field
            company_name = organization.name  # Assuming the model has a 'name' field
            if company_name:
                subject = "Account Registration Successful"
                message = f"""
                <html>
                <body>
                    <h3>Welcome to CMVP, {company_name}!</h3>
                    <p> Your account has been successfully created. Please confirm your email address by clicking the link below:</p>
                    <a href="https://new-cmvp-site.vercel.app/login?email={company_email}">Confirm Email</a>
                    <p>Thank you for registering with us!</p>
                </body>
                </html>
                """
                from_email = settings.DEFAULT_FROM_EMAIL


                recipient_list = [company_email]

                send_mail(
                    subject,
                    '',
                    from_email,
                    recipient_list,
                    fail_silently=False,
                    html_message=message,
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # print("serializer.errors")
        # print(serializer.data)
        # print("serializer.errors")
        # print(serializer.errors)
        # print("serializer.errors")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LoginView(generics.GenericAPIView):
#     serializer_class = LoginSerializer
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         email = serializer.validated_data['email']
#         password = serializer.validated_data['password']

#         # print(f"Login attempt: email={email}, password={password}")

#         # Custom authentication using email
#         try:
#             user = get_user_model().objects.get(email=email)
#             if user.check_password(password):
#                 # print(f"User found: {user.email}")
#                 refresh = RefreshToken.for_user(user)
#                 login_time = datetime.now()
                
         
#                 return Response({
#                     'refresh': str(refresh),
#                     'access': str(refresh.access_token),
#                     'email': user.email,
#                     'userId': user.id,
#                     'name': user.name,
#                     'user_role': user.role,
#                     'phone': user.phone,
#                     'address': user.address,
#                     'login_time': login_time.strftime('%I:%M %p'),  # Format time
#                     'unique_subscriber_id': user.unique_subscriber_id,
#                     'date_joined': user.date_joined,
#                 }, status=status.HTTP_200_OK)
#             else:
#                 # print("Authentication failed: Incorrect password")
#                 return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
#         except get_user_model().DoesNotExist:
#             # print("Authentication failed: User does not exist")
#             return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
from django.core.mail import send_mail
from django.utils.timezone import now
import re

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = get_user_model().objects.get(email=email)
            if user.check_password(password):
                # Generate refresh token for the user
                refresh = RefreshToken.for_user(user)
                login_time = now()

                # Extract user-agent from request headers
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                device_name, browser_name = self.extract_device_and_browser(user_agent)

                # Send email notification of login
                subject = "Login Notification"
                message = f"""
                <html>
                <body>
                    <h3>Hello {user.name},</h3>
                    <p>This is a notification that your account with <strong>cmvp.net</strong> has been successfully logged into at {login_time.strftime('%I:%M %p')}.</p>
                    <p><strong>Login Details:</strong></p>
                    <ul>
                        <li><strong>Login Time:</strong> {login_time.strftime('%I:%M %p')}</li>
                        <li><strong>Device:</strong> {device_name}</li>
                        <li><strong>Browser:</strong> {browser_name}</li>
                    </ul>
                    <p>If you did not initiate this login, please contact support immediately or recover your account with our forgotten password feature.</p>
                    <p>Best regards,</p>
                    <p>Your Support Team</p>
                </body>
                </html>
                """
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email]

                send_mail(
                    subject,
                    '',
                    from_email,
                    recipient_list,
                    fail_silently=False,
                    html_message=message
                )

                return Response({
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

            else:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except get_user_model().DoesNotExist:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

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
        reset_link = f"https://new-cmvp-site.vercel.app/forgotten_pass_reset/{uid}/{token}/"

        # Prepare email content
        subject = 'Password Reset Request'

        # Use a proper HTML template for the message
        message = f"Please click the following link to reset your password: {reset_link}"
        html_message = f'''
            <html>
                <body>
                    <h3>Please click on the link below to reset your password</h3>
                    <p><a href="{reset_link}"><strong>Reset Password</strong></a></p>
                    <p> Note this email will expire in five (5) minutes. </p>
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
            <body>
                <h3>Contact Form Submission</h3>
                <p><strong>Full Name:</strong> {full_name}</p>
                <p><strong>Email Address:</strong> {email}</p>
                <p><strong>Phone Number:</strong> {phone_number}</p>
                <p><strong>Interest Service:</strong> {interest_service}</p>
                <p><strong>Message:</strong> {message_body}</p>
            </body>
            </html>
            '''
            recipient_list = [email]

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



# @api_view(['POST'])
# @permission_classes([AllowAny])
# def send_sms(request):
#     africastalking_API_KEY = 'atsk_8b605cfd45b12b3748fe81ccde7a4b4ef5a8805e0260714296884907fc371d1f7c15183d'
#     africastalking_username = "sandbox"

#     if request.method == 'POST':
#         phone_number = request.data.get('phone')
#         message_body = request.data.get('message')

#         if not phone_number or not message_body:
#             return Response({"error": "Phone number and message are required."}, status=400)

#         africastalking.initialize(africastalking_username, africastalking_API_KEY)

#         sms = africastalking.SMS
#         try:
#             response = sms.send(message_body, [phone_number])

#             return Response({"success": True, "response": response}, status=200)
#         except Exception as e:
#             return Response({"error": str(e)}, status=500)






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

