from django.http import JsonResponse
from .services.ai_service_agent import AiServiceAgent

def index(request, pdf_name):
    ai_service = AiServiceAgent(pdf_name)
    extractions = ai_service.extract_with_context()
    return JsonResponse({'response': extractions})
