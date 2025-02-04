from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsletterSubscriptionView  # Correct import here

router = DefaultRouter()
router.register(r'subscribe', NewsletterSubscriptionView)

urlpatterns = [
    path('api/', include(router.urls)),
]
