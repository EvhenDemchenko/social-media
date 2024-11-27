# Generated by Django 5.1.3 on 2024-11-24 17:32

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0010_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='user_has_seen',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='notification',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]