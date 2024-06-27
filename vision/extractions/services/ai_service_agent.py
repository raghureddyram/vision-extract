import base64
import pdb
from collections import defaultdict

import requests
from dotenv import load_dotenv
import os
from pathlib import Path
from django.conf import settings
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
import re
import instructor

load_dotenv()
openai_api_key = os.getenv('OPENAI_KEY')
client = instructor.patch(OpenAI(api_key=openai_api_key))

class PortfolioHolding(BaseModel):
    HoldingName: str
    CostBasis: Optional[float]
    AccountNumber: Optional[str]

class StatementSummary(BaseModel):
    AccountHolderEntityName: str
    PortfolioValue: float
    AccountNumber: str


class AiServiceAgent:
    def __init__(self, pdf_name):
        self.pdf_folder = Path(settings.BASE_DIR) / 'media' / pdf_name
        self.holding_extractions = set()
        self.summary_extractions = set()
        self.api_key = openai_api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def get_file_names(self):
        return [file.name for file in self.pdf_folder.iterdir() if file.is_file()]

    def get_holding_extractions(self, content):
        holding_extractions = set({})
        holdings = client.chat.completions.create(
            model="gpt-4o",
            response_model=List[PortfolioHolding],
            messages=[
                {"role": "user",
                 "content": "Extract Portfolio holding names and each holding's cost basis, and account number which is /[\d-]+/ from the following financial statement. Please note that holdings may be stocks, preferred stocks, bonds and will typicall have a unique identifier: " + content},
            ]
        )
        for holding in holdings:
            if holding.AccountNumber and holding.HoldingName and holding.CostBasis:
                holding_extractions.add((holding.AccountNumber, holding.HoldingName, holding.CostBasis))

        return holding_extractions

    def get_summary_extractions(self, content):
        summary_extractions = set({})
        summaries = client.chat.completions.create(
            model="gpt-4o",
            response_model=List[StatementSummary],
            messages=[
                {"role": "user",
                 "content": "Extract the Account Owner Entity Names and Total Portfolio Values from the following financial statement. Account owners will have an account number: " + content},
            ]
        )
        for result in summaries:
            if result.AccountNumber and result.AccountHolderEntityName and result.PortfolioValue:
                summary_extractions.add((result.AccountNumber, result.AccountHolderEntityName, result.PortfolioValue))
        return summary_extractions

    def process_image(self, image_path):
        base64_image = self.encode_image(image_path)
        conversation = [
            {"role": "user", "content": [
                {"type": "text", "text": "You're looking at a financial statement. Can you summarize what you see? Please consider using words such as 'portfolio summary', any account name, account number formatted like 1111-3333, holdings, ticker symbols/cusips, and cost basis. Respond ONLY with 'NOT_RELEVANT' if you do not see such language."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ]

        payload = {
            "model": "gpt-4o",
            "messages": conversation,
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload)
        response_json = response.json()
        relevant_data = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")

        return relevant_data

    def extract_with_context(self, start=0, stop=-1):
        for image_name in self.get_file_names()[start:stop]:
            image_path = self.pdf_folder / image_name
            relevant_data = self.process_image(image_path)
            print(relevant_data)

            if relevant_data != "NOT_RELEVANT":
                if re.search(r'portfolio.*summary', relevant_data, re.IGNORECASE):
                    self.summary_extractions = self.get_summary_extractions(relevant_data)
                elif re.search(r'holding', relevant_data, re.IGNORECASE):
                    self.holding_extractions.update(self.get_holding_extractions(relevant_data))
        pdb.set_trace()
        return self._clean_results(self.summary_extractions, self.holding_extractions)

    def _clean_results(self, summary_extractions, holding_extractions):
        result = {"accounts": {}}
        for account_number, account_entity_owner, portfolio_value in summary_extractions:
            if account_number not in result["accounts"]:
                result["accounts"] = {}
                result["accounts"][account_number] = {
                    "account_entity_owner": account_entity_owner,
                    "portfolio_value": portfolio_value,
                    "holdings": []
                }
        for account_number, holding_name, cost_basis in holding_extractions:
            if account_number in result["accounts"]:
                result["accounts"][account_number]["holdings"].append({
                    "holding_name": holding_name,
                    "cost_basis": cost_basis
                })

        return result
