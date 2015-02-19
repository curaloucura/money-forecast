from django import forms
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from records.models import Record, Category, SYSTEM_CATEGORIES, INITIAL_BALANCE_SLUG,\
             UNSCHEDULED_DEBT_SLUG, UNSCHEDULED_CREDIT_SLUG

class RecordForm(forms.ModelForm):
    new_category = forms.CharField(max_length=50, required=False)
    type_category = forms.IntegerField(required=False, widget=forms.HiddenInput)
    category = forms.ModelChoiceField(required=False, queryset=Category.objects.none())

    class Meta:
        model = Record
        exclude = ('user',)

    def __init__(self, *args, **kwargs):

        user = kwargs.pop('user', None)

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
            self.fields['category'].queryset = Category.objects.filter(type_category=type_category_pk, user=user)
        else:
            try:
                self.fields['category'].queryset = Category.objects.filter(type_category=self.instance.category.type_category, user=user)
            except:
                self.fields['category'].queryset = Category.objects.filter(user=user)

    def clean_category(self):
        data = self.data
        cat_instance =  self.cleaned_data['category']
        # If user gives a new category, create and reassign record to it
        if data['new_category']:
            try:
                cat_instance = Category.objects.create(type_category=int(data['type_category']), name=data['new_category'], 
                                                        slug=slugify(data['new_category']))
            except:
                raise forms.ValidationError(_("This field is required."), code="required")
        else:
            if not cat_instance:
                raise forms.ValidationError(_("This field is required."), code="required")

        return cat_instance


class InitialBalanceForm(forms.ModelForm):
    slug_category = INITIAL_BALANCE_SLUG

    class Meta:
        model = Record
        fields = ('description', 'amount', 'start_date', 'notes')

    def save(self, user, commit=False):
        instance = super(InitialBalanceForm, self).save(commit=False)
        instance.category = Category.objects.get(type_category=SYSTEM_CATEGORIES, slug=self.slug_category) 
        if not instance.pk:
            instance.user = user
        else:
            if instance.user != user:
                raise Exception("Invalid user")

        instance.save()
        return instance


class UnscheduledDebtForm(InitialBalanceForm):
    slug_category = UNSCHEDULED_DEBT_SLUG


class UnscheduledCreditForm(InitialBalanceForm):
    slug_category = UNSCHEDULED_CREDIT_SLUG