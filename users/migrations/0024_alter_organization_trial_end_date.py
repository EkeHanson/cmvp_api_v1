# Generated by Django 5.1.4 on 2025-01-24 16:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_alter_organization_trial_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 23, 16, 3, 46, 801956, tzinfo=datetime.timezone.utc)),
        ),
    ]
