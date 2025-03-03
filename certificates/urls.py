from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CertificateCreateView,
    CertificateVerificationByOrganizationView,
    SoftDeletedCertificateView,
    CertificateSoftDeleteView,
    CertificateRestoreView,
    CertificatesByOrganizationView,
    CertificateCategoryCreateView,


    CertificateCategoryByOrganizationView,
    CertificateDeleteView,
)


router = DefaultRouter()
router.register(r'create', CertificateCreateView)
router.register(r'categories', CertificateCategoryCreateView)



urlpatterns = [
    path('', include(router.urls)),
    path('<str:certificate_id>/delete/', CertificateSoftDeleteView.as_view(), name='soft_delete_certificate'),
    path('<str:certificate_id>/restore/', CertificateRestoreView.as_view(), name='restore_certificate'),
    path('verify-certificate/<str:unique_subscriber_id>/', CertificateVerificationByOrganizationView.as_view(), name='verify-certificate-by-org'),
    path('organization/<str:unique_subscriber_id>/', CertificatesByOrganizationView.as_view(), name='certificates-by-organization'),

    path('certificateCategory/<str:unique_subscriber_id>/', CertificateCategoryByOrganizationView.as_view(), name='category-by-certificate'),
    
     path('<str:certificate_id>/delete-permanently/', CertificateDeleteView.as_view(), name='delete_permanently_certificate'),

    path('soft-deleted-certificates/<str:unique_subscriber_id>/', SoftDeletedCertificateView.as_view(), name='soft-deleted-certificates'),
]
