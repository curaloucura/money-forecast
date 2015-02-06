# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='currency',
            field=models.CharField(default=b'$', max_length=5, choices=[(b'd', b'$'), (b'eur', b'\xe2\x82\xac'), (b'brl', b'R$'), (b'bpd', b'\xc2\xa3'), (b'usd', b'US$')]),
            preserve_default=True,
        ),
    ]
