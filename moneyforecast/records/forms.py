from django import forms
from records.models import Record, Category, SYSTEM_CATEGORIES, INITIAL_BALANCE_SLUG

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
    class Meta:
        model = Record
        fields = ('description', 'amount', 'start_date')

    def save(self, commit=False):
        instance = super(InitialBalanceForm, self).save(commit=False)
        instance.category = Category.objects.get(type_category=SYSTEM_CATEGORIES, slug=INITIAL_BALANCE_SLUG) 
        return instance.save()
