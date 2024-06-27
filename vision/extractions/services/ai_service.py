import base64
import requests
from dotenv import load_dotenv
import pdb
import os
from pathlib import Path
from django.conf import settings
from openai import OpenAI
from pydantic.main import BaseModel
import instructor
from typing import List, Optional

load_dotenv()
openai_api_key = os.getenv('OPENAI_KEY')
client = instructor.patch(OpenAI(api_key=openai_api_key))
class PortfolioHolding(BaseModel):
    HoldingName: str
    CostBasis: Optional[float]
class StatementSummary(BaseModel):
    AccountOwner: str
    PortfolioValue: float
class StatementDetail(BaseModel):
    Summary: StatementSummary
    Holdings: List[PortfolioHolding]


class AiService:
    def __init__(self, pdf_name):
        self.pdf_folder = Path(settings.BASE_DIR) / 'media' / pdf_name
        self.holding_extractions = set({})
        self.summary_extractions = None
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
        holding_extractions = client.chat.completions.create(
            model="gpt-4o",
            response_model=List[PortfolioHolding],
            messages=[
                {"role": "user",
                 "content": "Extract portfolio holding names and each holding's cost basis from the following financial statement. Please note that holdings may be stocks, preferred stocks, bonds and have an identifier :" + f'{content}'},
            ]
        )

        for holding in holding_extractions:
            if holding.CostBasis:
                self.holding_extractions.add((holding.HoldingName, holding.CostBasis))

        return self.holding_extractions

    def get_summary_extractions(self, content):
        self.summary_extractions = client.chat.completions.create(
            model="gpt-4o",
            response_model=StatementSummary,
            messages=[
                {"role": "user",
                 "content": "Extract the Account Holder and Total Portfolio Value from the following financial statement:" + f'{content}'},
            ]
        )

        return self.summary_extractions

    def summarize_images_with_context(self, start=0, stop=-1):
        headers = self.headers
        conversation = []
        responses = []

        for image_name in self.get_file_names()[start:stop]:

            image_path = self.pdf_folder / image_name
            base64_image = self.encode_image(image_path)

            conversation.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are looking at a financial statement. Can you summarize what you see? Please pay special attention to any holdings, tickers, cusips, and the initial cost (cost basis). "
                                "Respond 'NOT_RELEVANT' if you do not see account information, holding information, or portfolio value."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            })

            payload = {
                "model": "gpt-4o",
                "messages": conversation,
                "max_tokens": 300
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response_json = response.json()
            relevant_data = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")

            if relevant_data != "NOT_RELEVANT":
                responses.append(response_json)

                # Add the assistant's response to the conversation
                conversation.append({
                    "role": "assistant",
                    "content": response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                })

        return responses