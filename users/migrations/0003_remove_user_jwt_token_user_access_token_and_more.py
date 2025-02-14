# Generated by Django 5.1.4 on 2025-01-07 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_created_at_user_jwt_token_alter_user_api_key_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='jwt_token',
        ),
        migrations.AddField(
            model_name='user',
            name='access_token',
            field=models.BinaryField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='api_key',
            field=models.BinaryField(max_length=500),
        ),
    ]
