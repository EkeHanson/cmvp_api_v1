# Generated by Django 5.1.4 on 2025-02-10 12:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_alter_organization_trial_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 25, 12, 44, 46, 17861, tzinfo=datetime.timezone.utc)),
        ),
    ]
