# Generated by Django 5.0.1 on 2024-04-12 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0008_alter_meeting_book'),
    ]

    operations = [
        migrations.RenameField(
            model_name='custombook',
            old_name='groups',
            new_name='group',
        ),
    ]
