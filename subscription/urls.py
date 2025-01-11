
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionPlanView, UserSubscriptionViewSet, payment_confirmation, UserSubscriptionDetailView

router = DefaultRouter()
router.register(r'subscription-plans', SubscriptionPlanView)
router.register(r'user-subscriptions', UserSubscriptionViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('payment-confirmation/', payment_confirmation, name='payment_confirmation'),
    path('api/user-subscription/<str:user_id>/', UserSubscriptionDetailView.as_view(), name='user_subscription_detail'),
]
