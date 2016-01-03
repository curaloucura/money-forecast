import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DeleteView

from records.forms import (
    RecordForm, ChangeRecurrentMonthForm, InitialBalanceForm,
    UnscheduledDebtForm, UnscheduledCreditForm)
from records.models import (
    Record, INCOME, OUTCOME, Category,
    SAVINGS, SYSTEM_CATEGORIES, INITIAL_BALANCE_SLUG, UNSCHEDULED_DEBT_SLUG,
    UNSCHEDULED_CREDIT_SLUG, get_last_date_of_month)
from records.month_control import (
    MonthControl, MonthControlWithBudget, _cache_key)

logger = logging.getLogger(__name__)


def _get_category_id(user, type_category, slug):
    category = Category.objects.filter(
        user=user, type_category=type_category, slug=slug)
    # The slugs might have changed
    if category.count():
        return category[0].id
    else:
        return 0


@login_required
def index(request):
    month_list = []
    today = timezone.now().replace(hour=0, minute=0)
    tomorrow = today+relativedelta(days=1)

    use_budget = request.GET.get('budget', 'True') == 'True'
    if use_budget:
        month_class = MonthControlWithBudget
    else:
        month_class = MonthControl

    t1 = datetime.now()
    cached_months = {}
    for i in range(0, 16):
        target_month = today+relativedelta(months=i)
        cached_months[_cache_key(target_month)] = month_class(
            request.user, target_month.month,
            target_month.year, cache=cached_months)
        month_list.append(cached_months[_cache_key(target_month)])
    t2 = datetime.now()
    logger.debug("Time to process months: {}".format(t2-t1))

    current_month = month_list[0]

    income_id = _get_category_id(request.user, INCOME, 'extra_income')
    outcome_id = _get_category_id(request.user, OUTCOME, 'extra_outcome')
    savings_id = _get_category_id(request.user, SAVINGS, 'savings')
    income_type = INCOME
    outcome_type = OUTCOME
    savings_type = SAVINGS
    unscheduled_debt_id = _get_category_id(
        request.user, SYSTEM_CATEGORIES, UNSCHEDULED_DEBT_SLUG)
    unscheduled_credit_id = _get_category_id(
        request.user, SYSTEM_CATEGORIES, UNSCHEDULED_CREDIT_SLUG)
    set_balance_id = _get_category_id(
        request.user, SYSTEM_CATEGORIES, INITIAL_BALANCE_SLUG)

    currency = request.user.profile.get_currency_display()
    record_form = RecordForm()
    t1 = datetime.now()
    response = render(request, "dashboard.html", locals())
    t2 = datetime.now()
    logger.debug("Time to render the template: {}".format(t2-t1))
    return response


def set_language(request):
    from django.utils import translation
    from django.conf import settings
    # TODO: validate language codes receive
    next = request.GET.get("next", "/")
    lang = request.GET.get("language", settings.LANGUAGE_CODE)
    translation.activate(lang)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang

    return redirect(next)


class CreateRecordView(CreateView):
    template_name = 'includes/create_record_form.html'
    form_class = RecordForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()

        return JsonResponse({'id': instance.id})

    def get_form_kwargs(self):
        kwargs = super(CreateRecordView, self).get_form_kwargs()
        kwargs['type_category_pk'] = self.kwargs['type']
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateRecordView, self).get_context_data(**kwargs)
        self.type_category = self.kwargs['type']
        context['type_category'] = self.type_category
        return context


class UpdateRecordView(UpdateView):
    template_name = 'includes/edit_record_form.html'
    form_class = RecordForm

    def get_queryset(self):
        return Record.objects.filter(user=self.request.user)

    def form_valid(self, form):
        instance = form.save(commit=False)
        # Make sure the record is owned by the user
        if self.request.user == instance.user:
            instance.save()

        return JsonResponse({'id': instance.id})

    def get_form_kwargs(self):
        kwargs = super(UpdateRecordView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class DeleteRecordView(DeleteView):
    def get_queryset(self):
        return Record.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return JsonResponse({'id': 0})


class CreateRecurrentMonthView(CreateView):
    template_name = 'includes/create_edit_recurrent_month_form.html'
    form_class = ChangeRecurrentMonthForm

    def form_valid(self, form):
        instance = form.save(commit=True)

        return JsonResponse({'id': instance.id})

    def get_form_kwargs(self):
        kwargs = super(CreateRecurrentMonthView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['parent_pk'] = self.kwargs['parent_pk']
        kwargs['month'] = int(self.kwargs['month'])
        kwargs['year'] = int(self.kwargs['year'])
        return kwargs


class EditRecurrentMonthView(UpdateView):
    template_name = 'includes/create_edit_recurrent_month_form.html'
    form_class = ChangeRecurrentMonthForm

    def get_queryset(self):
        return Record.objects.filter(user=self.request.user)

    def form_valid(self, form):
        instance = form.save(commit=True)
        return JsonResponse({'id': instance.id})

    def get_form_kwargs(self):
        kwargs = super(EditRecurrentMonthView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class BaseCreateRecordView(CreateView):
    model = Record
    form_class = InitialBalanceForm
    template_name = 'includes/edit_balance_form.html'
    title = _('Create Initial Balance')
    url_name = 'create_initial_balance'

    def form_valid(self, form):
        instance = form.save(self.request.user)

        return JsonResponse({'id': instance.id})

    def get_context_data(self, **kwargs):
        context = super(BaseCreateRecordView, self).get_context_data(
            **kwargs)
        current_date = timezone.now()
        min_date = datetime(
            day=1, month=current_date.month, year=current_date.year)
        context['min_date'] = min_date.strftime("%d.%m.%Y")
        last_date = get_last_date_of_month(
            current_date.month, current_date.year)
        context['max_date'] = last_date.strftime("%d.%m.%Y")
        start_date = context['form'].fields['start_date'].initial()
        context['start_date'] = start_date.strftime('%d.%m.%Y')

        return context


class BaseUpdateRecordView(UpdateView):
    model = Record
    form_class = InitialBalanceForm
    template_name = 'includes/edit_balance_form.html'
    title = _('Update Initial Balance')
    url_name = 'update_initial_balance'
    can_delete = False

    def form_valid(self, form):
        instance = form.save(self.request.user)

        return JsonResponse({'id': instance.id})

    def get_context_data(self, **kwargs):
        context = super(BaseUpdateRecordView, self).get_context_data(
            **kwargs)
        current_date = timezone.now()
        min_date = datetime(
            day=1, month=current_date.month, year=current_date.year)
        context['min_date'] = min_date.strftime("%d.%m.%Y")
        last_date = get_last_date_of_month(
            current_date.month, current_date.year)
        context['max_date'] = last_date.strftime("%d.%m.%Y")
        start_date = context['form'].initial['start_date']
        start_date = timezone.localtime(start_date)
        context['start_date'] = start_date.strftime('%d.%m.%Y')

        return context


class CreateInitialBalanceView(BaseCreateRecordView):
    pass


class UpdateInitialBalanceView(BaseUpdateRecordView):
    pass


class CreateUnscheduledDebtView(BaseCreateRecordView):
    title = _('Create Unscheduled Debt')
    form_class = UnscheduledDebtForm
    url_name = 'create_unscheduled_debt'
    template_name = 'includes/edit_unscheduled_form.html'


class CreateUnscheduledCreditView(BaseCreateRecordView):
    title = _('Create Unscheduled Credit')
    form_class = UnscheduledCreditForm
    url_name = 'create_unscheduled_credit'
    template_name = 'includes/edit_unscheduled_form.html'


class UpdateUnscheduledDebtView(BaseUpdateRecordView):
    title = _('Update Unscheduled Debt')
    form_class = UnscheduledDebtForm
    url_name = 'update_unscheduled_debt'
    can_delete = True
    template_name = 'includes/edit_unscheduled_form.html'


class UpdateUnscheduledCreditView(BaseUpdateRecordView):
    title = _('Update Unscheduled Credit')
    form_class = UnscheduledCreditForm
    url_name = 'update_unscheduled_credit'
    can_delete = True
    template_name = 'includes/edit_unscheduled_form.html'
