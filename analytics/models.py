from django.db import models
from users.models import CustomUser

class SiteAnalytics(models.Model):
    event = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
