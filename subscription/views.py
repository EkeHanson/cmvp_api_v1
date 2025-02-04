from rest_framework import generics, status
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets, status, generics, views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now
from datetime import timedelta
import requests
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view
from django.conf import settings
from .models import SubscriptionPlan
from rest_framework import viewsets, permissions
from .models import SubscriptionPlan, UserSubscription
from users.models import Organization
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer, UserSubscriptionDetailSerializer

# CRUD View for Subscription Plans

class SubscriptionPlanView(ModelViewSet):
    permission_classes = [AllowAny]
    queryset = SubscriptionPlan.objects.all().order_by('id')
    serializer_class = SubscriptionPlanSerializer

    def create(self, request, *args, **kwargs):
        """Handle POST requests with detailed error logging."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Log and print the errors
            error_message = f"POST request errors: {serializer.errors}"
            print(error_message)  # Print to console
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        # print("Received request data:", request.data)  # Debug log
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            # print("Before save:", instance.features)
            serializer.save()
            # print("After save:", instance.features)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserSubscription.objects.all().order_by('id')
    serializer_class = UserSubscriptionSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """Handle POST requests with detailed error logging."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Log and print the errors
            error_message = f"POST request errors: {serializer.errors}"
            print(error_message)  # Print to console
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
                # Ensure subscribed_duration is provided
        subscribed_duration = request.data.get('subscribed_duration')
        if not subscribed_duration:
            return Response({'detail': 'Subscribed duration is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.data.get('user')
        subscription_plan_uuid = request.data.get('subscription_plan')

        if not user_id or not subscription_plan_uuid:
            error_message = "User ID and Subscription Plan UUID must be provided in the request."
            print(error_message)
            return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Organization.objects.get(unique_subscriber_id=user_id)
        except Organization.DoesNotExist:
            error_message = "The provided user does not exist or is not valid."
            print(error_message)
            return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Check for any active or not yet expired subscriptions
        existing_subscription = UserSubscription.objects.filter(
            user=user,
            end_date__gte=now().date()  # Checks if there's any subscription that hasn't expired
        ).exists()

        if existing_subscription:
            error_message = f"{user.name}  has an active  subscription and cannot subscribe again until the current subscription expires."
            print(error_message)
            return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # try:
        #     subscription_plan = SubscriptionPlan.objects.get(unique_subscription_plan_id=subscription_plan_uuid)
        # except SubscriptionPlan.DoesNotExist:
        #     error_message = f"Subscription plan with UUID {subscription_plan_uuid} does not exist."
        #     print(error_message)
        #     return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subscription_plan = SubscriptionPlan.objects.get(unique_subscription_plan_id=subscription_plan_uuid)
        except SubscriptionPlan.DoesNotExist:
            error_message = "The selected subscription plan does not exist."
            return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # serializer.save(user=user, subscription_plan=subscription_plan)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
                # Save the new subscription
        subscription = serializer.save(user=user, subscription_plan=subscription_plan)


        # Update the organization's is_subscribed field to True
        user.is_subscribed = True
        user.save()

        # Ensure is_active is updated after saving
        subscription.is_active = True
        subscription.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserSubscriptionDetailView(generics.RetrieveAPIView):
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return self.queryset.filter(user__unique_subscriber_id=user_id)

    def get_object(self):
        queryset = self.get_queryset()
        obj = generics.get_object_or_404(queryset)
        return obj


def initiate_payment(user, subscription_plan):
    remita_url = "https://remita.net/api/payment/initiate"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.REMITA_API_KEY}"
    }
    payload = {
        "amount": str(subscription_plan.price),
        "currency": "NGN",
        "description": f"Subscription for {subscription_plan.name}",
        "customerId": user.id,
        "customerEmail": user.email,
        "returnUrl": "https://yourwebsite.com/payment-confirmation"
    }
    response = requests.post(remita_url, json=payload, headers=headers)
    return response.json()



@api_view(['POST'])
def payment_confirmation(request):
    data = request.data
    transaction_status = data.get("status")
    transaction_id = data.get("transactionId")
    user_id = data.get("customerId")

    try:
        subscription = UserSubscription.objects.get(user__id=user_id, is_active=False, transaction_id=transaction_id)
        
        if transaction_status == "success":
            subscription.is_active = True
            subscription.start_date = now()
            subscription.end_date = subscription.start_date + timedelta(days=subscription.subscription_plan.duration_in_months * 30)
            subscription.save()
            return Response({"message": "Subscription activated successfully."}, status=200)
        else:
            return Response({"message": "Payment failed."}, status=400)

    except UserSubscription.DoesNotExist:
        return Response({"message": "Subscription not found."}, status=404)