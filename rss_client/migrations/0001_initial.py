# Generated by Django 4.2.9 on 2024-11-07 14:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='feed title', max_length=500)),
                ('url', models.URLField(help_text='rss url', unique=True)),
                ('description', models.TextField(help_text='feed description', null=True)),
                ('active', models.BooleanField(default=True, help_text='feed is still active or not')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.TextField(help_text='report summary')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='source name', max_length=100)),
                ('rss_url', models.URLField(help_text='source url')),
                ('language_code', models.CharField(help_text='source language', max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='tag name', max_length=100, unique=True)),
                ('slug', models.SlugField(help_text='tag slug', max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(help_text='query question')),
                ('answer', models.TextField(help_text='query answer')),
                ('date_range_start', models.DateField(verbose_name='Date Range Start')),
                ('date_range_end', models.DateField(verbose_name='Date Range End')),
                ('tags', models.JSONField(default=list, help_text='query tags', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(help_text='user associated with the query', on_delete=django.db.models.deletion.CASCADE, related_name='user_queries', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProcessedFeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='processed feed title', max_length=500)),
                ('summary', models.TextField(help_text='processed feed summary')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('feed', models.ForeignKey(help_text='feed associated with the processed feed', on_delete=django.db.models.deletion.CASCADE, related_name='processed_feeds', to='rss_client.feed')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='group name', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sources', models.ManyToManyField(help_text='sources associated with the group', related_name='group', to='rss_client.source')),
                ('user', models.ForeignKey(help_text='user associated with the group', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='feed',
            name='tags',
            field=models.ManyToManyField(help_text='tags associated with the feed', related_name='feeds', to='rss_client.tag'),
        ),
        migrations.AddField(
            model_name='feed',
            name='user',
            field=models.ForeignKey(help_text='user associated with the feed', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feeds', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ConversationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(help_text='conversation message')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('query', models.ForeignKey(help_text='query associated with the conversation log', on_delete=django.db.models.deletion.CASCADE, related_name='conversation_logs', to='rss_client.userquery')),
                ('user', models.ForeignKey(help_text='user associated with the conversation log', on_delete=django.db.models.deletion.CASCADE, related_name='conversation_logs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='feed',
            index=models.Index(fields=['user', 'url'], name='user_url_index'),
        ),
        migrations.AlterUniqueTogether(
            name='feed',
            unique_together={('user', 'url')},
        ),
    ]
