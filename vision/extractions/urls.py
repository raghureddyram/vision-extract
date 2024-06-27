from django.urls import path

from . import views

urlpatterns = [
    path('<str:pdf_name>/<str:png_name>', views.index, name="index"),
]