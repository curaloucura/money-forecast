# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('records', 'initial_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='type_account',
            field=models.IntegerField(choices=[(0, 'Outcome'), (1, 'Income'), (2, 'Savings'), (3, 'System Internals')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='record',
            name='start_date',
            field=models.DateField(default=datetime.datetime.today),
            preserve_default=True,
        ),
    ]
