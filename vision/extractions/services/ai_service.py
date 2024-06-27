import base64
import requests
from dotenv import load_dotenv
import pdb
import os
from pathlib import Path
from django.conf import settings


load_dotenv()

class AiService:
    def __init__(self, pdf_name):
        self.pdf_folder = Path(settings.BASE_DIR) / 'media' / pdf_name

    def detail_image(self, image_name):
        image_path = self.pdf_folder / image_name

        # OpenAI API Key

        api_key = os.getenv('OPENAI_KEY')


        # Function to encode the image
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        # Getting the base64 string
        base64_image = encode_image(image_path)


        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What’s in this image?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        print(response.json())