from rest_framework import viewsets, status, generics, views
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Organization
from .serializers import  LoginSerializer, OrganizationSerializer
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
                from_email = "ekenehanson@sterlingspecialisthospitals.com"
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
                from_email = "ekenehanson@sterlingspecialisthospitals.com"  # Replace with your sender email
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

        from_email = 'ekenehanson@sterlingspecialisthospitals.com'
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
            # from_email = "support@cmvp.net"
            from_email = "support@cmvp.net"
            send_mail(subject, '', from_email, recipient_list, fail_silently=False, html_message=message)
            return Response({'message': 'Email sent successfully'})
        else:
            return Response({'error': 'Email not provided in POST data'}, status=400)
    else:
        return Response({'error': 'Invalid request method'}, status=400)

