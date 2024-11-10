# Generated by Django 4.2.9 on 2024-11-10 12:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rss_client', '0003_remove_group_sources'),
        ('sources', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='source',
            old_name='rss_url',
            new_name='url',
        ),
        migrations.AddField(
            model_name='source',
            name='group',
            field=models.ForeignKey(help_text='group associated with the source', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sources', to='rss_client.group'),
        ),
        migrations.AddField(
            model_name='source',
            name='user',
            field=models.ForeignKey(help_text='user associated with the source', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sources', to=settings.AUTH_USER_MODEL),
        ),
    ]
