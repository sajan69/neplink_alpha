# Generated by Django 5.1.1 on 2024-10-16 10:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0005_remove_post_media_postmedia'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='visibility',
            field=models.CharField(choices=[('everyone', 'Everyone'), ('friends', 'Friends'), ('private', 'Private'), ('selected', 'Selected Friends')], default='everyone', max_length=50),
        ),
        migrations.CreateModel(
            name='SelectedFriend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selected_friends', to='post.post')),
            ],
            options={
                'unique_together': {('post', 'friend')},
            },
        ),
    ]
