# Generated by Django 4.0.3 on 2022-08-03 06:59

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0004_rename_image_message_files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='to_user',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
