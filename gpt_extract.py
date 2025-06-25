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
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": "Extract all readable text from this receipt and try to structure it as a list of items  with name and price if possible in a JSON structure." },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            } # type: ignore
        ],
    )
    return response.output_text

# Example usage
if __name__ == "__main__":
    receipt_text = extract_receipt_text("tickets/w2.jpg")
    print(receipt_text)
21