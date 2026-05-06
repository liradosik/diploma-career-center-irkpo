from django.urls import path

from .views import cancel_registration, course_list, register_course

urlpatterns = [
    path('', course_list, name='list'),
    path('<int:pk>/register/', register_course, name='register'),
    path('registration/<int:pk>/cancel/', cancel_registration, name='cancel_registration'),
]
