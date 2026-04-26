from django.urls import path

from .views import (
    CustomLoginView,
    CustomLogoutView,
    admin_dashboard,
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
]
