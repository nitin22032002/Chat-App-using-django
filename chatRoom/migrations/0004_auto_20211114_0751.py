# Generated by Django 3.2.4 on 2021-11-14 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatRoom', '0003_auto_20211114_0745'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='meeting_password',
            field=models.CharField(default='xxxxx', max_length=8),
        ),
        migrations.AddField(
            model_name='room',
            name='meeting_password_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='room',
            name='name',
            field=models.CharField(default='group meeting 1', max_length=100),
        ),
    ]
