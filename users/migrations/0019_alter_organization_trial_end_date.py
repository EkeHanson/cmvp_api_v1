# Generated by Django 5.1.4 on 2025-01-24 10:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_alter_organization_trial_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 23, 10, 29, 39, 378335, tzinfo=datetime.timezone.utc)),
        ),
    ]
