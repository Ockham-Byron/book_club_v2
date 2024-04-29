# Generated by Django 5.0.1 on 2024-04-29 10:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('books', '0001_initial'),
        ('groups', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='give_up',
            field=models.ManyToManyField(blank=True, related_name='give_up', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='book',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='books', to='groups.customgroup'),
        ),
        migrations.AddField(
            model_name='book',
            name='in_library',
            field=models.ManyToManyField(blank=True, related_name='in_libraries', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='book',
            name='in_wishlist',
            field=models.ManyToManyField(blank=True, related_name='in_wishlist', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='book',
            name='no_read',
            field=models.ManyToManyField(blank=True, related_name='no_read', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='book',
            name='readers',
            field=models.ManyToManyField(blank=True, related_name='readers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='book',
            name='readings',
            field=models.ManyToManyField(blank=True, related_name='readings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='book',
            name='wont_read',
            field=models.ManyToManyField(blank=True, related_name='wont_read', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='borrow',
            name='borrower',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_comments', to='books.book'),
        ),
        migrations.AddField(
            model_name='custombook',
            name='admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='admin', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='custombook',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='kbook', to='books.book'),
        ),
        migrations.AddField(
            model_name='custombook',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='kbook_group', to='groups.customgroup'),
        ),
        migrations.AddField(
            model_name='custombook',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='custombook',
            name='sharing_groups',
            field=models.ManyToManyField(blank=True, related_name='shared_book', to='groups.customgroup'),
        ),
        migrations.AddField(
            model_name='borrow',
            name='custom_book',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='borrowing', to='books.custombook'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='attendees',
            field=models.ManyToManyField(blank=True, related_name='attendees', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='meeting',
            name='book',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='meeting', to='books.custombook'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='groups.customgroup'),
        ),
        migrations.AddField(
            model_name='reservations',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='books.custombook'),
        ),
        migrations.AddField(
            model_name='reservations',
            name='borrower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrowers', to=settings.AUTH_USER_MODEL),
        ),
    ]
