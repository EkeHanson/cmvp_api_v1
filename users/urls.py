from .views import  OrganizationView, LoginView, send_contact_email, ResetPasswordView, ConfirmResetPasswordView, GetOrganizationBySubscriberIdView
from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
# router.register(r'users', RegisterView)
router.register(r'organization', OrganizationView)


urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    
    path('send-contact-email/', send_contact_email, name='send_contact_email'),
    path('password-reset/', ResetPasswordView.as_view(), name='password-reset-request'),
    path('reset-password/<str:uidb64>/<str:token>/', ConfirmResetPasswordView.as_view(), name='reset-password'),
    path('organizations/<str:unique_subscriber_id>/', GetOrganizationBySubscriberIdView.as_view(), name='organization-by-subscriber-id'),

    path('organizations/<str:unique_subscriber_id>/update-by-subscriber-id/', OrganizationView.as_view({'patch': 'partial_update'}), name='organization-update-by-subscriber-id'),
]


