from django.urls import path

from .views import cancel_registration, course_detail, course_list, register_course, toggle_favorite_course

urlpatterns = [
    path('', course_list, name='list'),
    path('<int:pk>/', course_detail, name='detail'),
    path('<int:pk>/register/', register_course, name='register'),
    path('registration/<int:pk>/cancel/', cancel_registration, name='cancel_registration'),
    path('<int:pk>/favorite/', toggle_favorite_course, name='toggle_favorite'),
]
