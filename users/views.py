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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                    <p>Your account has been successfully created. Please confirm your email address by clicking the link below:</p>
                    <a href="https://new-cmvp-site.vercel.app?email={company_email}">Confirm Email</a>
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
        
        print("serializer.errors")
        print(serializer.data)
        print("serializer.errors")
        print(serializer.errors)
        print("serializer.errors")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # print(f"Login attempt: email={email}, password={password}")

        # Custom authentication using email
        try:
            user = get_user_model().objects.get(email=email)
            if user.check_password(password):
                # print(f"User found: {user.email}")
                refresh = RefreshToken.for_user(user)
                login_time = datetime.now()
                
         
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'email': user.email,
                    'userId': user.id,
                    'name': user.name,
                    'phone': user.phone,
                    'address': user.address,
                    'login_time': login_time.strftime('%I:%M %p'),  # Format time
                    'unique_subscriber_id': user.unique_subscriber_id,
                    'date_joined': user.date_joined,
                }, status=status.HTTP_200_OK)
            else:
                # print("Authentication failed: Incorrect password")
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except get_user_model().DoesNotExist:
            # print("Authentication failed: User does not exist")
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

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
        full_name = request.data.get('full_name')
        phone_number = request.data.get('phone_number')
        interest_service = request.data.get('interest_service')
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
            recipient_list = ['info@artstraining.co.uk', 'support@artstraining.co.uk', 'ekenhanson@gmail.com', 'Diana@adada.co.uk']
            from_email = 'admin@artstraining.co.uk'
            send_mail(subject, '', from_email, recipient_list, fail_silently=False, html_message=message)
            return Response({'message': 'Email sent successfully'})
        else:
            return Response({'error': 'Email not provided in POST data'}, status=400)
    else:
        return Response({'error': 'Invalid request method'}, status=400)

