from django.shortcuts import render
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
from .services.ai_service import AiService


def index(request, pdf_name, png_name):
    response = AiService(pdf_name).detail_image(png_name)

    return JsonResponse({'response': response})
