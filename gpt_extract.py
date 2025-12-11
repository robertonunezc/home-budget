from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import base64

# Set your API key

# Load the image and encode it as base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Prepare the API request
def extract_receipt_text(image_path):
    base64_image = encode_image_to_base64(image_path)
    logger.info(f"Extracting text from image: {image_path}")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all readable text from this receipt and structure it as a JSON object with the following format: {\"items\": [{\"name\": \"item name\", \"price\": 0.00, \"quantity\": 1, \"category\": \"category name\"}], \"total\": 0.00}. Categorize each item (e.g., food, beverage, household, other). Return ONLY valid JSON, no markdown formatting."
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
            max_tokens=1000
        )
        
        result = response.choices[0].message.content
        logger.info(f"GPT extraction successful: {len(result)} characters")
        return result
    except Exception as e:
        logger.error(f"GPT extraction failed: {str(e)}")
        raise

# Example usage
if __name__ == "__main__":
    receipt_text = extract_receipt_text("tickets/w2.jpg")
    print(receipt_text)
21