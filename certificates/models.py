from django.db import models
from users.models import Organization

class Certificate(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    certificate_id = models.CharField(max_length=100, unique=True)
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
