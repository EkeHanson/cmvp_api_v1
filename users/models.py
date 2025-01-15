import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.utils.timezone import now, timedelta

class CustomUserManager(BaseUserManager):

    def authenticate(self, email, password):
        try:
            user = self.get(email=email)
            if user.check_password(password):
                return user
        except self.model.DoesNotExist:
            return None
        
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class Organization(AbstractBaseUser):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='organization_logos/', null=True, blank=True)
    unique_subscriber_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=225)
    email = models.EmailField(max_length=80, unique=True)

    #30 DAY FREE TRIAL AFTER ACCOUNT CREATION FIELDS STARTS HERE

    trial_start_date = models.DateTimeField(auto_now_add=True)
    trial_end_date = models.DateTimeField(default=now() + timedelta(days=30))
    is_subscribed = models.BooleanField(default=False)

    
    #30 DAY FREE TRIAL AFTER ACCOUNT CREATION FIELDS ENDS HERE

    num_certificates_uploaded = models.PositiveIntegerField(default=0)  # New field to track uploaded certificates

    contact_first_name= models.CharField(max_length=255, null=True, blank=True)
    contact_last_name= models.CharField(max_length=255, null=True, blank=True)
    contact_telephone= models.CharField(max_length=255, null=True, blank=True)
    business_type= models.CharField(max_length=255, null=True, blank=True)
    registration_number= models.CharField(max_length=255, null=True, blank=True)
    staff_number= models.CharField(max_length=255, null=True, blank=True)
    nationality= models.CharField(max_length=255, null=True, blank=True)
    state= models.CharField(max_length=255, null=True, blank=True)
    year_incorporated= models.DateTimeField(max_length=255, null=True, blank=True)


    ROLE_CHOICES = (
        ('general', 'General User'),
        ('sub_admin', 'Sub Admin'),
        ('super_admin', 'Super Admin'),
    )

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='general')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    username = models.CharField(max_length=80, unique=False, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the given permission, based on their role.
        """
        # Example: Modify this to fit your permission model, if necessary.
        return True  # Customize permission check as needed

    def has_module_perms(self, app_label):
        """
        Return True if the user has access to the specified app's permissions.
        """
        # Example: Adjust this based on whether you want users to have access to specific apps
        return True  # Customize app access check as needed


# class BackgroundImage(models.Model):
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, to_field='unique_subscriber_id')
#     backgroundImage = models.FileField(upload_to='background_image/')
#     is_selected = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.organization.name} - {'Selected' if self.is_selected else 'Not Selected'}"
class BackgroundImage(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, to_field='unique_subscriber_id')
    backgroundImage = models.FileField(upload_to='background_image/')
    is_selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.organization.name} - {'Selected' if self.is_selected else 'Not Selected'}"
    
    @staticmethod
    def get_selected_background(organization):
        try:
            return BackgroundImage.objects.get(organization=organization, is_selected=True)
        except BackgroundImage.DoesNotExist:
            return None
