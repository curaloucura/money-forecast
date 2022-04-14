# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0002_auto_20150207_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='parent',
            field=models.ForeignKey(blank=True, to='records.Record', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
