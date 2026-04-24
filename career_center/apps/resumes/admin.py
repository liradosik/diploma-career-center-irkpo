from django.contrib import admin

from .models import ResumeSettings


@admin.register(ResumeSettings)
class ResumeSettingsAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'template', 'is_public')
