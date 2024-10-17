# Generated by Django 5.1.1 on 2024-10-16 14:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0007_post_is_shared_post_shared_post'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='tagged_users',
            field=models.ManyToManyField(blank=True, related_name='tagged_posts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='UserTagSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allow_tagging', models.BooleanField(default=True)),
                ('show_tagged_posts', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tag_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]