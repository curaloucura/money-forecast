from datetime import datetime

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _, get_language
from django.utils import formats 
from records.models import Record, Category, SYSTEM_CATEGORIES,\
             INITIAL_BALANCE_SLUG, UNSCHEDULED_DEBT_SLUG, UNSCHEDULED_CREDIT_SLUG,\
             get_last_date_of_month, tmz


# TODO: needs to properly localize date and times

class RecordForm(forms.ModelForm):
    new_category = forms.CharField(max_length=50, required=False)
    type_category = forms.IntegerField(required=False, widget=forms.HiddenInput)
    category = forms.ModelChoiceField(required=False, queryset=Category.objects.none())

    class Meta:
        model = Record
        exclude = ('user', 'parent')

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop('user', None)

        instance = kwargs.get('instance', None)
        if instance:
            type_category_pk = instance.category.type_category
        else:
            type_category_pk = kwargs.pop('type_category_pk', None)

        initial = kwargs.get('initial', {})
        initial.update({'type_category':type_category_pk})

        kwargs['initial'] = initial
        super(RecordForm, self).__init__(*args, **kwargs) 

        if type_category_pk:
            self.fields['category'].queryset = Category.objects.filter(type_category=type_category_pk, user=self.user)
        else:
            try:
                self.fields['category'].queryset = Category.objects.filter(type_category=self.instance.category.type_category, user=self.user)
            except:
                self.fields['category'].queryset = Category.objects.filter(user=self.user)

    def clean_category(self):
        data = self.data
        cat_instance =  self.cleaned_data['category']
        # If user gives a new category, create and reassign record to it
        if data['new_category']:
            try:
                cat_instance = Category.objects.create(type_category=int(data['type_category']), name=data['new_category'], 
                                                        slug=slugify(data['new_category']), user=self.user)
            except:
                raise forms.ValidationError(_("This field is required."), code="required")
        else:
            if not cat_instance:
                raise forms.ValidationError(_("This field is required."), code="required")

        return cat_instance


class ChangeRecurrentMonthForm(forms.ModelForm):
    parent = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Record
        fields = ('amount', 'start_date', 'parent')

    def __init__(self, *args, **kwargs):
        parent_pk = kwargs.pop('parent_pk', None)
        self.user = kwargs.pop('user', None)
        self.month = kwargs.pop('month', None)
        self.year = kwargs.pop('year', None)
        self.instance = kwargs.get('instance', None)
        initial = kwargs.get('initial', {})

        if self.instance:
            self.parent_obj = self.instance.parent
            self.month = self.instance.start_date.month
            self.year = self.instance.start_date.year
        else:
            self.parent_obj = Record.objects.get(pk=parent_pk, user=self.user)

        # Set initial amount
        if self.parent_obj and not self.instance:
            initial['parent'] = self.parent_obj.pk
            initial['amount'] = self.parent_obj.amount
            initial['start_date'] = self._get_date_for_month()

        # Make sure all necessary information is there 
        if not self.instance and not self.parent_obj:
            raise Exception("Invalid options for changing a recurrent record.")

        super(ChangeRecurrentMonthForm, self).__init__(*args, **kwargs)

    def clean_parent(self):
        data = self.cleaned_data['parent']
        data = Record.objects.get(pk=data, user=self.user)
        return data

    def get_action(self):
        if self.instance.pk:
            return reverse('edit_recurrent_month', kwargs={'pk':self.instance.pk})
        else:
            return reverse('create_recurrent_month', kwargs={'parent_pk': self.parent_obj.pk, 'month': self.month, 'year':self.year})

    def _get_date_for_month(self):
        day_of_month = self.parent_obj.day_of_month
        last_day = get_last_date_of_month(self.month, self.year)
        if day_of_month > last_day.day:
            day = last_day
        else:
            day = tmz(datetime(day=day_of_month, month=self.month, year=self.year))

        return day

    def min_date(self):
        return tmz(datetime(day=1, month=self.month, year=self.year))        

    def max_date(self):
        return get_last_date_of_month(self.month, self.year)

    def save(self, commit=True):
        instance = super(ChangeRecurrentMonthForm, self).save(commit=False)
        if not instance.pk:
            p = self.parent_obj
            instance.parent = p
            instance.description = p.description
            instance.category = p.category
            instance.user = self.user

        if commit:
            instance.save()

        return instance


class InitialBalanceForm(forms.ModelForm):
    slug_category = INITIAL_BALANCE_SLUG

    class Meta:
        model = Record
        fields = ('description', 'amount', 'start_date', 'notes')

    def save(self, user, commit=False):
        instance = super(InitialBalanceForm, self).save(commit=False)
        if not instance.pk:
            instance.user = user
        else:
            if instance.user != user:
                raise Exception("Invalid user")

        instance.category = Category.objects.get(type_category=SYSTEM_CATEGORIES, slug=self.slug_category, user=instance.user) 
        instance.save()
        return instance


class UnscheduledDebtForm(InitialBalanceForm):
    slug_category = UNSCHEDULED_DEBT_SLUG


class UnscheduledCreditForm(InitialBalanceForm):
    slug_category = UNSCHEDULED_CREDIT_SLUG