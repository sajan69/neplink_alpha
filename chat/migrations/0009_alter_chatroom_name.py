# Generated by Django 5.1.1 on 2024-10-04 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_alter_chatroom_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroom',
            name='name',
            field=models.CharField(blank=True, default=1, max_length=255),
            preserve_default=False,
        ),
    ]
