from .views import RegisterView, OrganizationView, LoginView, send_contact_email, ResetPasswordView, ConfirmResetPasswordView
from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'users', RegisterView)
router.register(r'organization', OrganizationView)


urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    
    path('send-contact-email/', send_contact_email, name='send_contact_email'),
    path('password-reset/', ResetPasswordView.as_view(), name='password-reset-request'),
    path('reset-password/<uidb64>/<token>/', ConfirmResetPasswordView.as_view(), name='reset-password'),
]


