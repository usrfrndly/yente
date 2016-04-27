# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pygrl', '0003_auto_20150901_2253'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='seen',
            field=models.IntegerField(default=1),
        ),
    ]
