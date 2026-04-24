from django.contrib import admin

from .models import Vacancy, VacancyResponse


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'employment_type', 'format_type', 'status')
    list_filter = ('status', 'employment_type', 'format_type', 'direction')
    search_fields = ('title', 'company', 'description')


@admin.register(VacancyResponse)
class VacancyResponseAdmin(admin.ModelAdmin):
    list_display = ('student', 'vacancy', 'created_at')
