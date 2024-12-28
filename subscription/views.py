from rest_framework import generics, status
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets, status, generics, views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils.timezone import now
from datetime import timedelta
from .models import SubscriptionPlan
from .serializers import SubscriptionPlanSerializer

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
        """Handle PATCH requests with detailed error logging."""
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            # Log and print the errors
            error_message = f"PATCH request errors: {serializer.errors}"
            #print(error_message)  # Print to console
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# class SubscriptionPlanView(viewsets.ModelViewSet):
#     """
#     Handles listing, creating, retrieving, updating, and deleting subscription plans.
#     """
#     permission_classes = [AllowAny]  # Adjust permissions as needed
#     queryset = SubscriptionPlan.objects.all().order_by('created_at')
#     serializer_class = SubscriptionPlanSerializer

# Create and View User Subscriptions
# class UserSubscriptionView(generics.ListCreateAPIView):
#     """
#     Handles listing and creating user subscriptions.
#     """
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserSubscriptionSerializer

#     def get_queryset(self):
#         # Fetch only subscriptions related to the authenticated user
#         return UserSubscription.objects.filter(user=self.request.user)

#     def create(self, request, *args, **kwargs):
#         plan_id = request.data.get("plan_id")
#         plan = SubscriptionPlan.objects.filter(id=plan_id).first()
#         if not plan:
#             return Response({"error": "Subscription plan not found"}, status=status.HTTP_404_NOT_FOUND)

#         end_date = now().date() + timedelta(days=plan.duration_in_months * 30)
#         subscription = UserSubscription.objects.create(
#             user=request.user,
#             subscription_plan=plan,
#             start_date=now().date(),
#             end_date=end_date
#         )
#         return Response(
#             {"message": "Subscription successful", "subscription_id": subscription.id},
#             status=status.HTTP_201_CREATED
#         )
