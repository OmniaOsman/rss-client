# Generated by Django 4.2.9 on 2024-11-27 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rss_client', '0015_alter_tag_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feed',
            name='url',
            field=models.URLField(help_text='rss url', max_length=5000),
        ),
    ]
