from django.urls import path

from .views import builder, public_resume

urlpatterns = [
    path('builder/', builder, name='builder'),
    path('public/<str:token>/', public_resume, name='public'),
]
