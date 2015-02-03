from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'currency', 'timezone')
	readonly_fields = ('user',)

	def get_queryset(self, request):
		qs = super(ProfileAdmin, self).queryset(request)
		 # make sure all users, even superusers, see only their own objects
		return qs.filter(user=request.user)

	def save_model(self, request, obj, form, change):
		if getattr(obj, 'user', None) is None:
			obj.user = request.user
		obj.save()

admin.site.register(Profile, ProfileAdmin)
