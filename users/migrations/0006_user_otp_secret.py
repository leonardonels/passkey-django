# Generated by Django 5.0.3 on 2024-03-20 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_remove_user_otp_secret'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='otp_secret',
            field=models.CharField(blank=True, max_length=16),
        ),
    ]