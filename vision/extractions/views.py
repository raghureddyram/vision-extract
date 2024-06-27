from django.shortcuts import render
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
from .services.ai_service import AiService
import pdb


def index(request, pdf_name):
    service = AiService(pdf_name)
    summary_json = service.summarize_images_with_context(start=0, stop=2)
    summary_extraction = service.get_summary_extractions(summary_json)

    holdings_json = service.summarize_images_with_context(start=2, stop=-1)
    holding_extraction = service.get_holding_extractions(holdings_json)


    return JsonResponse({'response': {'account_holder': summary_extraction.AccountOwner,
                                      'portfolio_value': summary_extraction.PortfolioValue,
                                      'holdings': list(holding_extraction)}})
