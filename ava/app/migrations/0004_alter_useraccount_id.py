# Generated by Django 5.1.5 on 2025-01-20 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_team_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='id',
            field=models.CharField(max_length=256, primary_key=True, serialize=False),
        ),
    ]
