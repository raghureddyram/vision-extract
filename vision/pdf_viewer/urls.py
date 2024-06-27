from django.urls import path

from . import views

urlpatterns = [
    path('process', views.process_all, name="process_all"),
    path('<str:file_name>', views.index, name="index"),
]