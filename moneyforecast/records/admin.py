import logging
from django.contrib import admin
from records.models import Category, Record, Budget, SYSTEM_CATEGORIES

logger = logging.getLogger(__name__)


class CurrentUserAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)

    def get_queryset(self, request):
        qs = super(CurrentUserAdmin, self).get_queryset(request)
        # make sure all users, even superusers, see only their own objects
        # to see all categories a superuser need to add a hidden option
        # ?all=True to the querystring eg.: /admin/categories/?all=True
        if request.user.is_superuser and request.GET.get("all"):
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'user', None) is None:
            obj.user = request.user
        obj.save()


class CategoryAdmin(CurrentUserAdmin):
    list_display = ('name', 'type_category')
    list_filter = ('type_category', )
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        qs = super(CategoryAdmin, self).get_queryset(request)
        return qs.exclude(type_category=SYSTEM_CATEGORIES)


class RecordAdmin(CurrentUserAdmin):
    list_display = (
        'description', 'category', 'amount', 'start_date',
        'day_of_month', 'end_date', 'is_paid_out')
    list_filter = ('start_date', 'end_date', 'is_paid_out', 'category')
    list_display_links = ('description', 'category')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(user=request.user)
        return super(RecordAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)


class BudgetAdmin(CurrentUserAdmin):
    list_display = ('description', 'amount', 'category')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(Budget, BudgetAdmin)
