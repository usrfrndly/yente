# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pygrl', '0002_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='liked',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='history',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
