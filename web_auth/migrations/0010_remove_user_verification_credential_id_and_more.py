# Generated by Django 5.0.3 on 2024-03-26 13:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_auth', '0009_user_verification_credential_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_verification',
            name='credential_id',
        ),
        migrations.AddField(
            model_name='user_verification',
            name='credential',
            field=models.ForeignKey(default=69, on_delete=django.db.models.deletion.CASCADE, to='web_auth.credential'),
            preserve_default=False,
        ),
    ]
