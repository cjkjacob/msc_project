# Generated by Django 5.1.7 on 2025-04-01 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0002_pendingeffort'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendingeffort',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
