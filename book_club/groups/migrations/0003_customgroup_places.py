# Generated by Django 5.0.1 on 2024-05-06 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customgroup',
            name='places',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
