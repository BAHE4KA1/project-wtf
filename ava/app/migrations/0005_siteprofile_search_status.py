# Generated by Django 5.1.5 on 2025-01-26 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_useraccount_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteprofile',
            name='search_status',
            field=models.CharField(default=None, max_length=256),
            preserve_default=False,
        ),
    ]
