from .views import (
    OrganizationView, 
    LoginView,
    send_contact_email,
    ResetPasswordView,
    ConfirmResetPasswordView,
    GetOrganizationBySubscriberIdView,
    BackgroundImageView,
    BackgroundImageByOrganizationView,
    SetSelectedBackgroundImageView,
    GetSelectedBackgroundImageView,
    OrganizationSubscriptionView, send_sms, VerifyEmailView, ResendVerificationEmailView,
)

from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'organization', OrganizationView)
router.register(r'background_image', BackgroundImageView)


urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('send-contact-email/', send_contact_email, name='send_contact_email'),
    path('send-contact-sms/', send_sms, name='send_sms'),
    path('password-reset/', ResetPasswordView.as_view(), name='password-reset-request'),
    path('reset-password/<str:uidb64>/<str:token>/', ConfirmResetPasswordView.as_view(), name='reset-password'),
    path('organizations/<str:unique_subscriber_id>/', GetOrganizationBySubscriberIdView.as_view(), name='organization-by-subscriber-id'),

    path('organizations/<str:unique_subscriber_id>/update-by-subscriber-id/', OrganizationView.as_view({'patch': 'partial_update'}), name='organization-update-by-subscriber-id'),

    path('organization/<str:unique_subscriber_id>/backgorundImage/', BackgroundImageByOrganizationView.as_view(), name='backgorundImage-by-organization'),

    path('organization/background_image/<int:id>/select/', SetSelectedBackgroundImageView.as_view(), name='select-background-image'),

    path('organization/background_image/selected/<str:unique_subscriber_id>/', GetSelectedBackgroundImageView.as_view(), name='get-selected-background-image'),

    path('subscription/organizations/subscriptions/', OrganizationSubscriptionView.as_view(), name='organization-subscriptions'),

    # New email verification endpoint
    path('api/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('api/resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
]


