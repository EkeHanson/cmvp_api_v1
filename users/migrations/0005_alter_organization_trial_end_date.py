# Generated by Django 5.1.4 on 2025-01-13 15:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_organization_is_subscribed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 12, 15, 34, 22, 921547, tzinfo=datetime.timezone.utc)),
        ),
    ]
