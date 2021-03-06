# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-18 06:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0003_record_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Please, use only the monthly amount. This field is required', max_digits=12, verbose_name='How much?'),
        ),
    ]
