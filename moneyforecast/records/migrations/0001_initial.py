# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('type_category', models.IntegerField(choices=[(0, 'Outcome'), (1, 'Income'), (2, 'Savings'), (3, 'System Internals')])),
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
                ('value', models.FloatField(default=0, help_text='Please, use only the monthly amount. This field is required', verbose_name='How much?')),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now, help_text='This field is required', verbose_name='Date')),
                ('day_of_month', models.SmallIntegerField(help_text='Use this field to set recurring bills. The day in which will you be billed every month', null=True, verbose_name='Day of the month', blank=True)),
                ('number_payments', models.SmallIntegerField(help_text='This is only used to generate the final payment date', null=True, verbose_name='Number of Payments', blank=True)),
                ('end_date', models.DateTimeField(help_text='This is the date when it will be the last payment for this record, after this date the record will not appear on the calculations', null=True, verbose_name='Last payment on', blank=True)),
                ('is_paid_out', models.BooleanField(default=False, help_text="If checked, the record won't appear in the calculations anymore. Click it only to hide a record from your spreadsheet", verbose_name='Is it totally paid?')),
                ('notes', models.TextField(null=True, blank=True)),
                ('category', models.ForeignKey(help_text='Select the category for this record. This field is required', to='records.Category')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
