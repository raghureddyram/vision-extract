from django.shortcuts import render
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
from .utils import ImageConverter


def index(request, file_name):
    base_name = file_name.split('.')[0]
    images_dir = Path(settings.BASE_DIR) / 'media' / base_name
    if not images_dir.exists():
        return render(request, 'list_png_files.html', {'png_files': []})  # Handle directory not found
    try:
        # Filter the list to include only .png files
        png_images = [f for f in images_dir.iterdir() if f.suffix == '.png']
        # Create full file paths
        png_file_urls = [f"{settings.MEDIA_URL}/{base_name}/{file.name}" for file in png_images]
    except Exception as e:
        png_paths = []
        print(f"Error reading files: {e}")

    return render(request, 'pdf_viewer/index.html', {'png_urls': png_file_urls})

def process_all(request):
    ImageConverter(stop_phrases=["Activity", "Estimated Cash Flow", "Endnotes"]).convert_pdf_to_images()
    return JsonResponse({'success': 'True'})