import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, phone, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        role = extra_fields.pop('general', 'General User')
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        return self.create_user(email, password, **extra_fields)


class Organization(AbstractBaseUser):

    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='organization_logos/', null=True, blank=True)
    unique_subscriber_id = models.CharField(
        max_length=50, 
        unique=True, 
        default=uuid.uuid4  # Automatically generate a unique UUID
    )



    # first_name = models.CharField(max_length=225, blank=True, null=True)
    # last_name = models.CharField(max_length=225, blank=True, null=True)

    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=225)


    email = models.EmailField(max_length=80, unique=True)



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

