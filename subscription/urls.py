# from django.urls import path
# from .views import SubscriptionPlanView, UserSubscriptionView

# urlpatterns = [
#     # CRUD operations for subscription plans
#     path('plans/', SubscriptionPlanView.as_view(), name='subscription-plans'),

#     # Create and list user subscriptions
#     #path('subscriptions/', UserSubscriptionView.as_view(), name='user-subscriptions'),
# ]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionPlanView

router = DefaultRouter()
router.register(r'subscription-plans', SubscriptionPlanView)

urlpatterns = [
    path('api/', include(router.urls)),
]
