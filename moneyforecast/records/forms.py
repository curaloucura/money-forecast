from django import forms
from records.models import Record, Category, SYSTEM_CATEGORIES, INITIAL_BALANCE_SLUG,\
             UNSCHEDULED_DEBT_SLUG, UNSCHEDULED_CREDIT_SLUG

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        self.type_category = kwargs.pop('type_category', None)
        super(RecordForm, self).__init__(*args, **kwargs) 
        if self.type_category:
            self.fields['category'].queryset = Category.objects.filter(type_category=self.type_category)
        else:
            try:
                self.fields['category'].queryset = Category.objects.filter(type_category=self.instance.category.type_category)
            except:
                self.fields['category'].queryset = Category.objects.all()

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