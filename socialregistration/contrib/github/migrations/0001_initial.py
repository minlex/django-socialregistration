# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import socialregistration.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GithubAccessToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('access_token', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GithubProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('github', models.CharField(max_length=255)),
                ('site', models.ForeignKey(default=socialregistration.models.get_default_site, to='sites.Site')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='githubaccesstoken',
            name='profile',
            field=models.OneToOneField(related_name='access_token', to='github.GithubProfile'),
            preserve_default=True,
        ),
    ]
