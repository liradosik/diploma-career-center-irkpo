from django.urls import path

from .views import course_list, register_course

urlpatterns = [
    path('', course_list, name='list'),
    path('<int:pk>/register/', register_course, name='register'),
]
