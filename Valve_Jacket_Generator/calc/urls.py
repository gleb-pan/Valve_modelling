from django.urls import path
from . import views


urlpatterns = [
    path('', views.start, name='start'),
    path('the_file/', views.gen_file, name='gen_file'),
]
