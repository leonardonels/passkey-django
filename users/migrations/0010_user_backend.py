# Generated by Django 5.0.3 on 2024-03-26 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_user_backup_codes'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='backend',
            field=models.CharField(default='django.contrib.auth.backends.ModelBackend', max_length=100),
            preserve_default=False,
        ),
    ]
