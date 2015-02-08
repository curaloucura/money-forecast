from django import forms
from records.models import Record, Category

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        self.type_category = kwargs.pop('type_category', None)
        super(RecordForm, self).__init__(*args, **kwargs) 
        self.fields['category'].queryset = Category.objects.filter(type_category=self.type_category)