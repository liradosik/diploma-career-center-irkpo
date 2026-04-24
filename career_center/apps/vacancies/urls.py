from django.urls import path

from .views import respond, vacancy_detail, vacancy_list

urlpatterns = [
    path('', vacancy_list, name='list'),
    path('<int:pk>/', vacancy_detail, name='detail'),
    path('<int:pk>/respond/', respond, name='respond'),
]
