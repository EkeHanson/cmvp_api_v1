# Generated by Django 5.1.4 on 2025-01-28 15:24

import datetime
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('name', models.CharField(max_length=255)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='organization_logos/')),
                ('unique_subscriber_id', models.CharField(default=uuid.uuid4, max_length=50, unique=True)),
                ('phone', models.CharField(max_length=15)),
                ('address', models.CharField(max_length=225)),
                ('email', models.EmailField(max_length=80, unique=True)),
                ('trial_start_date', models.DateTimeField(auto_now_add=True)),
                ('trial_end_date', models.DateTimeField(default=datetime.datetime(2025, 2, 27, 15, 24, 32, 928538, tzinfo=datetime.timezone.utc))),
                ('is_subscribed', models.BooleanField(default=False)),
                ('num_certificates_uploaded', models.PositiveIntegerField(default=0)),
                ('contact_first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_telephone', models.CharField(blank=True, max_length=255, null=True)),
                ('business_type', models.CharField(blank=True, max_length=255, null=True)),
                ('registration_number', models.CharField(blank=True, max_length=255, null=True)),
                ('staff_number', models.CharField(blank=True, max_length=255, null=True)),
                ('nationality', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('year_incorporated', models.DateTimeField(blank=True, max_length=255, null=True)),
                ('role', models.CharField(choices=[('general', 'General User'), ('sub_admin', 'Sub Admin'), ('super_admin', 'Super Admin')], default='general', max_length=15)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('username', models.CharField(blank=True, max_length=80, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BackgroundImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('backgroundImage', models.FileField(upload_to='background_image/')),
                ('is_selected', models.BooleanField(default=False)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='unique_subscriber_id')),
            ],
        ),
    ]
