# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('type_account', models.IntegerField(choices=[(0, 'Outcome'), (1, 'Income'), (2, 'Savings'), (3, 'System Internals')])),
                ('slug', models.SlugField(null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=50, blank=True)),
                ('value', models.FloatField(default=0, help_text='Please, use only the monthly value')),
                ('day_of_month', models.SmallIntegerField(help_text='Use este campo para contas mensais', null=True, blank=True)),
                ('number_payments', models.SmallIntegerField(null=True, blank=True)),
                ('start_date', models.DateField(default=datetime.datetime.today)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('is_paid_off', models.BooleanField(default=False)),
                ('notes', models.TextField(null=True, blank=True)),
                ('account', models.ForeignKey(to='records.Account')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
