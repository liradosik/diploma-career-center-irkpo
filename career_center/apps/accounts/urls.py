from django.urls import path

from .views import (
    CustomLoginView,
    CustomLogoutView,
    admin_course_registrations,
    admin_courses,
    admin_curators,
    admin_dashboard,
    admin_responses,
    admin_students,
    admin_vacancies,
    curator_dashboard,
    curator_student_detail,
    curator_students,
    profile_edit,
    redirect_by_role,
    student_dashboard,
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('redirect/', redirect_by_role, name='redirect_by_role'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('student/profile/', profile_edit, name='profile_edit'),
    path('curator/dashboard/', curator_dashboard, name='curator_dashboard'),
    path('curator/students/', curator_students, name='curator_students'),
    path('curator/students/<int:student_id>/', curator_student_detail, name='curator_student_detail'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/students/', admin_students, name='admin_students'),
    path('admin/curators/', admin_curators, name='admin_curators'),
    path('admin/vacancies/', admin_vacancies, name='admin_vacancies'),
    path('admin/courses/', admin_courses, name='admin_courses'),
    path('admin/responses/', admin_responses, name='admin_responses'),
    path('admin/course-registrations/', admin_course_registrations, name='admin_course_registrations'),
]
