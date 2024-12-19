# Generated by Django 5.0.2 on 2024-12-06 02:49

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='unique_subscriber_id',
            field=models.CharField(default=uuid.uuid4, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='unique_subscriber_id',
            field=models.CharField(default=uuid.uuid4, max_length=50, unique=True),
        ),
    ]
