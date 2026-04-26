from django.urls import path

from .views import create_entry, delete_entry, edit_entry, list_entries, review_queue

urlpatterns = [
    path('', list_entries, name='list'),
    path('create/', create_entry, name='create'),
    path('<int:pk>/edit/', edit_entry, name='edit'),
    path('<int:pk>/delete/', delete_entry, name='delete'),
    path('curator/review/', review_queue, name='review_queue'),
]
