from rest_framework import serializers
from rest_framework import serializers
from .models import NewsletterSubscription


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = '__all__'

