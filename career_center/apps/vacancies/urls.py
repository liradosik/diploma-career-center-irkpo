from django.urls import path

from .views import respond, toggle_favorite, vacancy_detail, vacancy_list

urlpatterns = [
    path('', vacancy_list, name='list'),
    path('<int:pk>/', vacancy_detail, name='detail'),
    path('<int:pk>/respond/', respond, name='respond'),
    path('<int:pk>/favorite/', toggle_favorite, name='toggle_favorite'),
]
