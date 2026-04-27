from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Specialty, StudentProfile, StudyGroup, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    ordering = ('email',)
    list_display = ('email', 'full_name', 'role', 'group', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Профиль', {'fields': ('full_name', 'role', 'group', 'specialty', 'admission_year', 'curator')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Временные метки', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'full_name', 'role', 'password1', 'password2')}),
    )
    search_fields = ('email', 'full_name')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'updated_at')
    search_fields = ('user__full_name', 'user__email')


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'letter_code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name', 'letter_code')


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty_ref', 'admission_year', 'curator')
    list_filter = ('admission_year', 'specialty_ref')
    search_fields = ('name', 'specialty', 'specialty_ref__name', 'specialty_ref__code')
