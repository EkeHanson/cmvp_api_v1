# Generated by Django 5.1.4 on 2025-02-18 13:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_alter_organization_trial_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 26, 13, 35, 17, 889019, tzinfo=datetime.timezone.utc)),
        ),
    ]
