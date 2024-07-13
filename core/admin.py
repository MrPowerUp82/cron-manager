from django.contrib import admin
from core.models import Page, Component


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ['label', 'html_id']
    search_fields = ['label', 'html_id']
