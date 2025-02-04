from rest_framework import generics, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import NewsletterSubscription
from .serializers import NewsletterSubscriptionSerializer

# CRUD View for Subscription Plans

class NewsletterSubscriptionView(ModelViewSet):
    permission_classes = [AllowAny]
    queryset = NewsletterSubscription.objects.all().order_by('id')
    serializer_class = NewsletterSubscriptionSerializer
