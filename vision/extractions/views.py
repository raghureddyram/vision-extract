from django.http import JsonResponse
from .services.ai_service import AiService



def index(request, pdf_name):
    service = AiService(pdf_name)
    summary_json = service.summarize_images_with_context(start=0, stop=2)
    summary_extraction = service.get_summary_extractions(summary_json)

    holdings_json = service.summarize_images_with_context(start=2, stop=-1)
    holding_set = service.get_holding_extractions(holdings_json)
    holdings = [{'holding_name': holding_name, 'cost_basis': cost_basis} for holding_name, cost_basis in holding_set]

    return JsonResponse({'response': {'account_holder': summary_extraction.AccountOwner,
                                      'portfolio_value': summary_extraction.PortfolioValue,
                                      'holdings': holdings}})
