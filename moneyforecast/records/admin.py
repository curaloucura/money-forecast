from django.contrib import admin
from records.models import Account, Record, SYSTEM_ACCOUNTS


class CurrentUserAdmin(admin.ModelAdmin):
	readonly_fields = ('user',)

	def queryset(self, request):
		qs = super(CurrentUserAdmin, self).queryset(request)
		 # make sure all users, even superusers, see only their own objects
		return qs.filter(user=request.user)

	def save_model(self, request, obj, form, change):
		if getattr(obj, 'user', None) is None:
			obj.user = request.user
			obj.save()


class AccountAdmin(CurrentUserAdmin):
	list_display = ('name','type_account')
	list_filter = ('type_account',)
	prepopulated_fields = {"slug": ("name",)} # TODO: block changing the slug for internal accounts

	def queryset(self, request):
		qs = super(CurrentUserAdmin, self).queryset(request)
		 # make sure all users, even superusers, see only their own objects
		return qs.exclude(type_account=SYSTEM_ACCOUNTS)


class RecordAdmin(CurrentUserAdmin):
	list_display = ('description','account','value','start_date','day_of_month','end_date','is_paid_off')
	list_filter = ('start_date','end_date','is_paid_off')
	list_display_links = ('description', 'account')


admin.site.register(Account, AccountAdmin)
admin.site.register(Record, RecordAdmin)
