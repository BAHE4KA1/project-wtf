# Generated by Django 5.1.5 on 2025-01-17 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_useraccount_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='logo',
            field=models.FileField(blank=True, upload_to='team_logo'),
        ),
    ]
