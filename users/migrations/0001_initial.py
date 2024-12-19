# Generated by Django 5.0.2 on 2024-12-06 02:35

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('first_name', models.CharField(blank=True, max_length=225, null=True)),
                ('last_name', models.CharField(blank=True, max_length=225, null=True)),
                ('phone', models.CharField(max_length=15)),
                ('address', models.CharField(max_length=225)),
                ('company_name', models.CharField(blank=True, max_length=225, null=True)),
                ('email', models.EmailField(max_length=80, unique=True)),
                ('company_logo', models.ImageField(blank=True, null=True, upload_to='organization_logos/')),
                ('unique_subscriber_id', models.CharField(max_length=50)),
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
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='organization_logos/')),
                ('unique_subscriber_id', models.CharField(max_length=50)),
            ],
        ),
    ]
