# Generated by Django 5.1.1 on 2024-10-05 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_user_online'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='online',
        ),
        migrations.AddField(
            model_name='user',
            name='last_logged_in',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
