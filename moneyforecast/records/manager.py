from django.db import models
from django.db.models import Q

OUTCOME = 0
INCOME = 1
# Savings has it's own category because it must be grouped together
SAVINGS = 2
# System Categories are those not being accounted
SYSTEM_CATEGORIES = 3


class RecordQuerySet(models.QuerySet):

    def not_ended(self, max_date):
        return self.filter(
            Q(end_date__isnull=True) | Q(end_date__gte=max_date))

    def by_type_category(self, type_category):
        return self.filter(category__type_category=type_category)

    def recurring(self):
        return self.filter(day_of_month__isnull=False)

    def non_recurring(self):
        return self.filter(day_of_month__isnull=True)

    def exclude_child_records(self):
        return self.filter(
            parent__isnull=True)

    def starting_on(self, on_date):
        return self.filter(start_date__gte=on_date)

    def starting_before(self, on_date):
        return self.filter(start_date__lte=on_date)

    def start_ranging(self, min_date, max_date):
        return self.starting_on(min_date).starting_before(max_date)

    def ending_before(self, on_date):
        return self.filter(Q(end_date__lte=on_date) | Q(end_date__isnull=True))

    def by_user(self, user):
        return self.filter(user=self.user)

    def active_for(self, user, max_date):
        # TODO: improve the way to track paid off or it could disappear
        # prematurely
        records = self.by_user(user=user)
        records = records.filter(is_paid_out=False)
        records = records.starting_before(max_date)
        records = records.ending_before(max_date)
        return records


class RecordManager(models.Manager):

    def get_queryset(self):
        return RecordQuerySet(self.model, self._db)

    def active_for(self, user, max_date):
        return self.get_queryset().active_for(user, max_date)

    def _get_root_by_type_category_until(self, user, type_category, max_date):
        records = self.active_for(user, max_date)
        records = records.exclude_child_records()
        records = records.by_type_category(type_category)
        return records

    def get_records_by_type(self, user, type_category, min_date, max_date):
        records = self._get_root_by_type_category_until(
            user, type_category, max_date)
        records = records.non_recurring()
        records = records.start_ranging(min_date, max_date)
        record_list = list(records)

        return record_list

    def get_recurring_records_by_type(
            self, user, type_category, min_date, max_date, on_month, on_year):
        records = self._get_root_by_type_category_until(
            user, type_category, max_date)
        records = records.recurring()
        records = records.not_ended(min_date)
        record_list = []
        for record in records:
            record_list.append(
                record.get_record_for_month(on_month, on_year))
        return record_list

    def not_ended(self, date_limit):
        return self.get_queryset().not_ended(date_limit)

    def by_type_category(self, type_category):
        return self.get_queryset().by_type_category(
            category__type_category=type_category)

    def exclude_child_records_recurring(self):
        records = self.recurring()
        return records.exclude_child_records()

    def exclude_child_records(self):
        records = self.non_recurring()
        return records.exclude_child_records()

    def recurring(self):
        return self.get_queryset().recurring()

    def non_recurring(self):
        return self.get_queryset().non_recurring()

    def start_ranging(self, min_date, max_date):
        return self.get_queryset().start_ranging(min_date, max_date)
