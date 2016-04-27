# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pygrl.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_id', models.CharField(unique=True, max_length=30)),
                ('_data', models.TextField(default=b'')),
                ('bio', models.CharField(max_length=300)),
                ('birth_date', models.DateTimeField()),
                ('fuzzy_birth_date', models.NullBooleanField()),
                ('common_friend_count', models.IntegerField(default=0)),
                ('common_friends', models.TextField(default=b'')),
                ('common_like_count', models.IntegerField(default=0)),
                ('common_likes', models.TextField(default=b'')),
                ('connection_count', models.IntegerField(default=0)),
                ('distance_km', models.FloatField(default=0)),
                ('gender', models.CharField(max_length=15)),
                ('name', models.CharField(max_length=100)),
                ('photos', pygrl.models.ListField()),
                ('ping_time', models.DateTimeField()),
            ],
        ),
    ]
