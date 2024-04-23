# Generated by Django 4.1.3 on 2024-04-19 14:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customgroup',
            name='leader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='customgroup',
            name='members',
            field=models.ManyToManyField(related_name='group_members', to=settings.AUTH_USER_MODEL),
        ),
    ]
