from django.contrib import admin
from .models import Building, Activity, Organization


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['id', 'address', 'latitude', 'longitude']
    list_display_links = ['id', 'address']
    search_fields = ['address']
    list_per_page = 20


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent', 'level']
    list_display_links = ['id', 'name']
    search_fields = ['name']
    list_filter = ['level', 'parent']
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'building', 'display_phone_numbers', 'display_activities']
    list_display_links = ['id', 'name']
    search_fields = ['name']
    list_filter = ['building', 'activities']
    list_per_page = 20

    def display_phone_numbers(self, obj):
        return ", ".join(obj.phone_numbers) if obj.phone_numbers else "-"

    display_phone_numbers.short_description = "Телефоны"

    def display_activities(self, obj):
        return ", ".join([activity.name for activity in obj.activities.all()])

    display_activities.short_description = "Виды деятельности"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('building').prefetch_related('activities')
