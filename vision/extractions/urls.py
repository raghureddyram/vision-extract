from django.urls import path

from . import views

urlpatterns = [
    path('<str:pdf_name>', views.index, name="index"),
]