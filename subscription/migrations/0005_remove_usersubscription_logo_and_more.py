# Generated by Django 5.1.4 on 2025-02-10 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0004_usersubscription_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersubscription',
            name='logo',
        ),
        migrations.AddField(
            model_name='usersubscription',
            name='organization_logo',
            field=models.ImageField(blank=True, null=True, upload_to='subscribed_organization_logos/'),
        ),
    ]
