# Generated by Django 5.1.4 on 2025-02-12 09:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_organization_is_activated_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 20, 9, 41, 40, 273570, tzinfo=datetime.timezone.utc)),
        ),
    ]
