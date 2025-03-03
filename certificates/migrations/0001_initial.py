# Generated by Django 5.1.4 on 2025-01-28 15:24

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('unique_certificate_category_id', models.CharField(default=uuid.uuid4, max_length=50, unique=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='unique_subscriber_id')),
            ],
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certificate_id', models.CharField(max_length=100, unique=True)),
                ('certificate_title', models.CharField(blank=True, max_length=255, null=True)),
                ('examination_type', models.CharField(blank=True, max_length=255, null=True)),
                ('issuedNumber', models.CharField(blank=True, max_length=255, null=True)),
                ('issuedBy', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('client_name', models.CharField(max_length=255)),
                ('issue_date', models.DateField()),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('pdf_file', models.FileField(upload_to='certificates/')),
                ('verification_count', models.IntegerField(default=0)),
                ('deleted', models.BooleanField(default=False)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='unique_subscriber_id')),
                ('certificate_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='certificates.certificatecategory', to_field='unique_certificate_category_id')),
            ],
        ),
        migrations.CreateModel(
            name='VerificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verifier_ip', models.GenericIPAddressField()),
                ('verification_date', models.DateTimeField(auto_now_add=True)),
                ('certificate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='certificates.certificate')),
            ],
        ),
    ]
