# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from django.utils.translation import ugettext as _
from records.models import INCOME, OUTCOME, SAVINGS, SYSTEM_ACCOUNTS, INITIAL_BALANCE_ID


def initial_accounts(apps, schema_editor):
    Account = apps.get_model("records", "Account")
    Account.objects.create(
        id = 1,
        name = _("Extra Income"),
        type_account = INCOME
    )
    Account.objects.create(
        id = 2,
        name = _("Extra Outcome"),
        type_account = OUTCOME
    )
    Account.objects.create(
        id = 3,
        name = _("Savings"),
        type_account = SAVINGS
    )
    Account.objects.create(
        id = INITIAL_BALANCE_ID,
        name = _("Initial Balance"),
        type_account = SYSTEM_ACCOUNTS
    )
    Account.objects.create(
        id = UNSCHEDULED_DEBTS_ID,
        name = _("Initial Balance"),
        type_account = SYSTEM_ACCOUNTS
    )


class Migration(migrations.Migration):

    dependencies = [
        ("records","0001_initial"),
    ]

    operations = [
        migrations.RunPython(initial_accounts)
    ]