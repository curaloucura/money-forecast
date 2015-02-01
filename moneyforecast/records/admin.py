from django.contrib import admin
from records.models import Account, Record


class RecordAdmin(admin.ModelAdmin):
	list_display = ('description','account','value','start_date','day_of_month','end_date','is_paid_off')
	list_filter = ('start_date','end_date','is_paid_off')
	list_display_links = ('description', 'account')


class AccountAdmin(admin.ModelAdmin):
	list_display = ('name','type_account')
	list_filter = ('type_account',)


admin.site.register(Account, AccountAdmin)
admin.site.register(Record, RecordAdmin)
