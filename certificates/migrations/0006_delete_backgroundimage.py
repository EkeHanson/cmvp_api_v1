# Generated by Django 5.1.4 on 2025-01-15 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0005_certificate_issuednumber'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BackgroundImage',
        ),
    ]
