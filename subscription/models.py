# subscriptions/models.py

from django.db import models
from users.models import Organization

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    duration_in_months = models.PositiveIntegerField()  # 1, 3, 6, 12 months
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=dict)  # Store plan-specific features as JSON

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.duration_in_months} months"

# class UserSubscription(models.Model):
#     user = models.ForeignKey(Organization, on_delete=models.CASCADE)
#     subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
#     start_date = models.DateField()
#     end_date = models.DateField()  certificate cartegories
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.user.name} - {self.subscription_plan.name}"
