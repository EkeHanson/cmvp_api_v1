# Generated by Django 5.1.4 on 2025-01-30 10:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='organization',
            name='verification_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 1, 10, 53, 49, 697278, tzinfo=datetime.timezone.utc)),
        ),
    ]
