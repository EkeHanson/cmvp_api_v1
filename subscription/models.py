from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from users.models import Organization
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from dateutil.relativedelta import relativedelta

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unique_subscription_plan_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Add unique=True
    duration_in_months = models.PositiveIntegerField()  # 1, 3, 6, 12 months
    # price = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)  # Explicitly define price per month
    is_basic_plan = models.BooleanField(default=False)  # Identify basic plans
    features = models.JSONField(default=dict)
    

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.duration_in_months} months"

class UserSubscription(models.Model):
    user = models.ForeignKey(Organization, on_delete=models.CASCADE, to_field='unique_subscriber_id')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, to_field='unique_subscription_plan_id')
    start_date = models.DateField(default=now)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    subscribing_organization_name = models.CharField(max_length=100, null=True, blank=True)
    
    # New fields to record the amount and duration
    subscribed_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Amount paid by the user
    subscribed_duration = models.PositiveIntegerField(null=True, blank=True)  # Duration in months

    def save(self, *args, **kwargs):
        if not self.end_date and self.subscription_plan:
            # Calculate end_date based on subscribed_duration
            self.end_date = self.start_date + relativedelta(months=self.subscribed_duration)
        
        # Calculate the total amount if not provided
        if not self.subscribed_amount and self.subscription_plan:
            self.subscribed_amount = self.subscription_plan.price_per_month * self.subscribed_duration
        
        super().save(*args, **kwargs)

# Post-Save Signal:

@receiver(post_save, sender=UserSubscription)
def deactivate_basic_plan(sender, instance, **kwargs):
    if instance.subscription_plan.is_basic_plan and instance.end_date <= now().date():
        instance.is_active = False
        instance.save()