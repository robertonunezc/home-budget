from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np

def preprocess_image(path):
    # Load image in OpenCV
    image = cv2.imread(path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2
    )

    # Save temp preprocessed image
    temp_path = "temp_processed.png"
    cv2.imwrite(temp_path, thresh)

    return temp_path

def extract_text(image_path):
    processed = preprocess_image(image_path)
    custom_config = r'--oem 3 --psm 6'

    text = pytesseract.image_to_string(Image.open(processed), config=custom_config)

    return text

# Example usage
if __name__ == "__main__":
    img_path = "tickets/w2.jpg"
    result = extract_text(img_path)
    print("🧾 Extracted Text:\n")
    print(result)
