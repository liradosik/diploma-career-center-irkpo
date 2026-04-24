from django.contrib import admin

from .models import PortfolioEntry


@admin.register(PortfolioEntry)
class PortfolioEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'type', 'status', 'date')
    list_filter = ('status', 'type')
    search_fields = ('title', 'student__full_name')
