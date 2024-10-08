# Generated by Django 5.1.1 on 2024-10-05 06:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_alter_chatroom_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calllog',
            name='receiver',
        ),
        migrations.AddField(
            model_name='calllog',
            name='call_type',
            field=models.CharField(choices=[('audio', 'Audio'), ('video', 'Video')], default='video', max_length=10),
        ),
        migrations.AddField(
            model_name='calllog',
            name='participants',
            field=models.ManyToManyField(related_name='call_participations', to=settings.AUTH_USER_MODEL),
        ),
    ]
