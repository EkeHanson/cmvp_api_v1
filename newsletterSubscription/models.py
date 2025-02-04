from django.db import models
from django.utils import timezone
from django.utils.timezone import now, timedelta
import uuid

class NewsletterSubscription(models.Model):
    email = models.EmailField(max_length=80, null=True, blank=True)
    is_active = models.BooleanField(default=True)
  
    def __str__(self):
        return self.email

 