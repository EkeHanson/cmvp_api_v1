from django.db import models
from users.models import Organization
from django.utils import timezone
from django.utils.timezone import now, timedelta
import uuid

class CertificateCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    unique_certificate_category_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    organization = models.ForeignKey(Organization,  on_delete=models.CASCADE, to_field='unique_subscriber_id')

    def __str__(self):
        return self.name



class Certificate(models.Model):
    organization = models.ForeignKey(Organization,  on_delete=models.CASCADE, to_field='unique_subscriber_id')

    certificate_category = models.ForeignKey(CertificateCategory,  on_delete=models.CASCADE, to_field='unique_certificate_category_id')
    
    certificate_id = models.CharField(max_length=100, unique=True)

    certificate_title= models.CharField(max_length=255, null=True, blank=True)

    examination_type= models.CharField(max_length=255, null=True, blank=True)
    issuedNumber= models.CharField(max_length=255, null=True, blank=True)

    issuedBy= models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    client_name = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='certificates/')
    verification_count = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)  # Soft delete field

    def soft_delete(self):
        """Soft delete a certificate by marking it as deleted."""
        self.deleted = True
        self.save()

    def restore(self):
        """Restore a deleted certificate by unmarking it as deleted."""
        self.deleted = False
        self.save()

class VerificationLog(models.Model):
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE)
    verifier_ip = models.GenericIPAddressField()
    verification_date = models.DateTimeField(auto_now_add=True)


