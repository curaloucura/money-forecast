from django.contrib import admin
from django.utils.timezone import utc
from records.models import Category, Record, SYSTEM_CATEGORIES


class CurrentUserAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)

    def get_queryset(self, request):
        qs = super(CurrentUserAdmin, self).queryset(request)
         # make sure all users, even superusers, see only their own objects
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'user', None) is None:
            obj.user = request.user
        obj.save()


class CategoryAdmin(CurrentUserAdmin):
    list_display = ('name','type_category')
    list_filter = ('type_category',)
    prepopulated_fields = {"slug": ("name",)} # TODO: block changing the slug for internal categories

    def get_queryset(self, request):
        qs = super(CurrentUserAdmin, self).queryset(request)
         # make sure all users, even superusers, see only their own objects
        return qs.exclude(type_category=SYSTEM_CATEGORIES) # TODO: Hide also extra income and others


class RecordAdmin(CurrentUserAdmin):
    list_display = ('description','category','amount','start_date','day_of_month','end_date','is_paid_out')
    list_filter = ('start_date','end_date','is_paid_out')
    list_display_links = ('description', 'category')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(user=request.user)
        return super(RecordAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)



admin.site.register(Category, CategoryAdmin)
admin.site.register(Record, RecordAdmin)
