import openai
import base64

# Set your API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Load the image and encode it as base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Prepare the API request
def extract_receipt_text(image_path):
    base64_image = encode_image_to_base64(image_path)

    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all readable text from this receipt and try to structure it as a list of items with name and price if possible."},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high"
                    }},
                ]
            }
        ],
        max_tokens=2000,
    )

    return response['choices'][0]['message']['content']

# Example usage
if __name__ == "__main__":
    receipt_text = extract_receipt_text("tickets/w1.jpg")
    print(receipt_text)
21