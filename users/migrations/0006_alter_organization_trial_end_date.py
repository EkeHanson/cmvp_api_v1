# Generated by Django 5.1.4 on 2025-02-01 14:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_organization_trial_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 3, 14, 19, 44, 18487, tzinfo=datetime.timezone.utc)),
        ),
    ]
