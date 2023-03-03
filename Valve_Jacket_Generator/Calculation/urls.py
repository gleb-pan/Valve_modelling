from django.urls import path
from . import views

urlpatterns = [
    path('generate_files/', views.generate_files, name='generate_files'),
]