from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView, DeleteView
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from records.forms import RecordForm, InitialBalanceForm
from records.models import tmz, get_last_day_of_month, Record, Category, INCOME, OUTCOME,\
                             SAVINGS, SYSTEM_CATEGORIES, INITIAL_BALANCE_SLUG, UNSCHEDULED_DEBT_SLUG,\
                             UNSCHEDULED_CREDIT_SLUG

class MonthControl(object):
    def __init__(self, user, month, year):
        self.user = user
        self.month = month
        self.year = year
        self.today = timezone.now().replace(hour=0, minute=0)
        self.start_date = tmz(datetime(day=1, month=month, year=year))
        # end_date is the last day of the month
        self.end_date = get_last_day_of_month(month, year).replace(hour=23, minute=59, second=59)
        self.last_month = (self.start_date-relativedelta(months=1))

        # Initialize variables
        self.initial_balance = 0
        self._get_records()
        self._calculate_totals()


    def is_current(self):
        return ((self.today >= self.start_date) and
                (self.today <= self.end_date))
    

    def _sum_after_date(self, date, record_list):
        total = 0.0
        for record in record_list:
            if record.is_accountable(date):
                total += record.amount

        return total

    def _calculate_totals(self):
        self.initial_balance = self.get_initial_balance()
        # TODO: disaply total amount but not use it for calculations
        self.income_monthly = sum([x.amount for x in self.income_monthly_list])
        self.income_variable = sum([x.amount for x in self.income_variable_list])
        self.outcome_monthly = sum([x.amount for x in self.outcome_monthly_list])
        self.outcome_variable = sum([x.amount for x in self.outcome_variable_list])
        self.accountable_income_monthly = self._sum_after_date(self.initial_balance_date, self.income_monthly_list)
        self.accountable_income_variable = self._sum_after_date(self.initial_balance_date, self.income_variable_list)
        self.accountable_outcome_monthly = self._sum_after_date(self.initial_balance_date, self.outcome_monthly_list)
        self.accountable_outcome_variable = self._sum_after_date(self.initial_balance_date, self.outcome_variable_list)
        self.total_income = self.income_monthly + self.income_variable
        self.total_outcome = self.outcome_monthly + self.outcome_variable
        self.difference = ((self.income_monthly+self.income_variable) -
                            (self.outcome_monthly+self.outcome_variable))
        self.accountable_difference = (
                (self.accountable_income_monthly+self.accountable_income_variable)-
                (self.accountable_outcome_monthly+self.accountable_outcome_variable)
            )
        self.final_balance = self.initial_balance + self.accountable_difference

    def _sort_records_by_date(self, record_list):
            results = []
            for record in record_list:
                # Calculate dates
                results.append((record.get_date_for_month(self.month, self.year), record))

            # Sort per date
            results.sort(key=lambda r: r[0])
            return results


    def _get_records(self):
        self.income_monthly_list = self._get_records_by_type(INCOME, False)
        self.income_variable_list = self._get_records_by_type(INCOME, True)
        self.outcome_monthly_list = self._get_records_by_type(OUTCOME, False)
        self.outcome_variable_list = self._get_records_by_type(OUTCOME, True)
        self.income_list = self.income_monthly_list | self.income_variable_list 
        self.sorted_income_list = self._sort_records_by_date(self.income_list)
        self.outcome_list = self.outcome_monthly_list | self.outcome_variable_list 
        self.sorted_outcome_list = self._sort_records_by_date(self.outcome_list)

    def _get_records_by_type(self, category, one_time_only):
        records = self.get_queryset() 
        records = records.filter( Q(end_date__isnull=True) | Q(end_date__range=(self.start_date, self.end_date)) )
        records = records.filter(category__type_category=category, day_of_month__isnull=one_time_only)
        records = records.filter(start_date__lte=self.end_date)

        if one_time_only:
            # If not recurring, then it should check the start date within this month
            records = records.filter(start_date__range=(self.start_date, self.end_date))
        return records

    def get_queryset(self):
        # Make sure to filter only records by the user
        # TODO: improve the way to track paid off or it could disappear prematurely
        records = Record.objects.filter(user=self.user, is_paid_out=False) 

        # All records must start in the month or earlier
        records = records.filter(start_date__lte=self.end_date)
        
        return records

    def _get_initial_balance_info(self):
        balance = self.get_queryset().filter(category__type_category=SYSTEM_CATEGORIES, category__slug=INITIAL_BALANCE_SLUG) 
        # Initial Balance must be from this month
        balance = balance.filter(start_date__range=(self.start_date, self.end_date))
        if balance.count():
            return (balance[0].start_date, balance[0].amount, balance[0])
        else:
            # TODO: Have to improve it, raising errors when no last balance is found
            last_balance = MonthControl(self.user, self.last_month.month, self.last_month.year)
            # If using last month, initial date is the first day of the month
            return (self.start_date, last_balance.final_balance, None)


    def get_initial_balance(self):
            if not self.initial_balance:
                (self.initial_balance_date, self.initial_balance, self.initial_balance_instance) = self._get_initial_balance_info()

            return self.initial_balance
        

    def set_initial_balance(self, amount):
        # TODO: set record for initial balance for the month
        pass

    def get_upcoming_records(self):
        """
        This will return a tuple with the date for the month and the record.
        It is necessary since you can't get the date of a recurring event inside the template
        """
        upcoming = []
        results = []

        for record in self.sorted_outcome_list:
            if record[0] >= self.today:
                upcoming.append(record)
        return upcoming

    def get_savings_totals(self):
        categories = Category.objects.filter(type_category=SAVINGS)
        savings_list = []
        total = 0
        for category in categories:
            total_category = self.get_queryset().filter(category=category).aggregate(Sum('amount'))['amount__sum']
            savings_list.append((category,total_category))
            total += (total_category or 0)

        return {'list': savings_list, 'total': total}

    def _get_unscheduled(self, slug_category):
        category = Category.objects.get(type_category=SYSTEM_CATEGORIES, slug=slug_category, user=self.user)
        records = Record.objects.filter(user=self.user, category=category)
        total = records.aggregate(Sum('amount'))['amount__sum']
        return {'list': records, 'total': total}

    def get_unscheduled_debt_totals(self):
        return self._get_unscheduled(UNSCHEDULED_DEBT_SLUG)

    def get_unscheduled_credit_totals(self):
        return self._get_unscheduled(UNSCHEDULED_CREDIT_SLUG)


def _get_category_id(user, type_category, slug):
    category = Category.objects.filter(user=user, type_category=type_category, slug=slug)
    # The slugs might have changed
    if category.count():
        return category[0].id
    else:
        return 0

@login_required
def index(request):
    month_list = []
    today = timezone.now().replace(hour=0, minute=0)
    tomorrow = today+timedelta(days=1)
    for i in range(0,13):
        target_month = today+relativedelta(months=i)
        month_list.append(MonthControl(request.user, target_month.month, target_month.year))

    current_month = month_list[0]

    income_id = _get_category_id(request.user, INCOME, 'extra_income')
    outcome_id = _get_category_id(request.user, OUTCOME, 'extra_outcome')
    savings_id = _get_category_id(request.user, SAVINGS, 'savings')
    income_type = INCOME
    outcome_type = OUTCOME
    savings_type = SAVINGS
    unscheduled_debt_id = _get_category_id(request.user, SYSTEM_CATEGORIES, UNSCHEDULED_DEBT_SLUG)
    unscheduled_credit_id = _get_category_id(request.user, SYSTEM_CATEGORIES, UNSCHEDULED_CREDIT_SLUG)
    set_balance_id = _get_category_id(request.user, SYSTEM_CATEGORIES, INITIAL_BALANCE_SLUG)

    currency = request.user.profile.get_currency_display()
    record_form = RecordForm()
    return render(request, "dashboard.html", locals())


def set_language(request):
    from django.utils import translation
    from django.conf import settings
    # TODO: validate language codes receive
    next = request.GET.get("next","/")
    lang = request.GET.get("language", settings.LANGUAGE_CODE)
    translation.activate(lang)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang

    return redirect(next) 


class CreateRecordView(CreateView):
    model = Record
    template_name = 'includes/create_record_form.html'
    form_class = RecordForm

    def form_valid(self, form): 
        instance = form.save(commit=False) 
        instance.user = self.request.user
        instance.save() 

        return HttpResponse('successfully-sent!')

    def get_form_kwargs(self):
        kwargs = super(CreateRecordView, self).get_form_kwargs()
        kwargs['type_category'] = self.kwargs['type']
        return kwargs

    def get_context_data(self, **kwargs):
        context = kwargs
        self.type_category = self.kwargs['type']
        context['type_category'] = self.type_category
        return context


class UpdateRecordView(UpdateView):
    model = Record
    template_name = 'includes/edit_record_form.html'
    form_class = RecordForm

    def form_valid(self, form): 
        instance = form.save(commit=False)
        # Make sure the record is owned by the user
        if self.request.user == instance.user:
            instance.save() 

        return HttpResponse('successfully-sent!')


class DeleteRecordView(DeleteView):
    def get_queryset(self):
        return Record.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        payload = {'delete': 'ok'}
        return HttpResponse('successfully-sent!')

class UpdateInitialBalanceView(UpdateView):
    model = Record
    form_class = InitialBalanceForm
    template_name = 'includes/edit_balance_form.html'

    def form_valid(self, form): 
        form.save()

        return HttpResponse('successfully-sent!')
