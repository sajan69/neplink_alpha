# Generated by Django 5.1.1 on 2024-10-19 07:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CallLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('total_time', models.DurationField(blank=True, null=True)),
                ('status', models.CharField(choices=[('ongoing', 'Ongoing'), ('ended', 'Ended')], default='ongoing', max_length=10)),
                ('agora_channel', models.CharField(blank=True, max_length=255, null=True)),
                ('call_type', models.CharField(choices=[('audio', 'Audio'), ('video', 'Video')], default='video', max_length=10)),
                ('caller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='caller_logs', to=settings.AUTH_USER_MODEL)),
                ('participants', models.ManyToManyField(related_name='call_participations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('is_group_chat', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('active_call', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_in_room', to='chat.calllog')),
                ('participants', models.ManyToManyField(related_name='chat_rooms', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='calllog',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='call_logs', to='chat.chatroom'),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_file', models.BooleanField(default=False)),
                ('file', models.FileField(blank=True, null=True, upload_to='chat_files/')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.chatroom')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
    ]
