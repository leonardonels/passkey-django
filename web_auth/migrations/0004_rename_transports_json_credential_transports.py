# Generated by Django 5.0.3 on 2024-03-25 21:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web_auth', '0003_remove_credential_transports_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='credential',
            old_name='transports_json',
            new_name='transports',
        ),
    ]