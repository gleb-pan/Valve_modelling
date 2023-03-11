from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('the_file/', views.gen_file, name='gen_file'),
]
