# Generated by Django 5.0.1 on 2024-04-12 08:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_remove_custombook_group_custombook_groups_and_more'),
        ('groups', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='custombook',
            name='groups',
        ),
        migrations.AddField(
            model_name='custombook',
            name='groups',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='kbook_group', to='groups.customgroup'),
        ),
    ]
