# Generated by Django 5.1.5 on 2025-01-26 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_siteprofile_search_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteprofile',
            name='id',
            field=models.CharField(max_length=256, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
