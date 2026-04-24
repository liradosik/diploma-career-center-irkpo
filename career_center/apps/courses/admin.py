from django.contrib import admin

from .models import Course, CourseRegistration


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'format_type', 'date', 'places', 'status')
    list_filter = ('kind', 'format_type', 'status')


@admin.register(CourseRegistration)
class CourseRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'created_at')
