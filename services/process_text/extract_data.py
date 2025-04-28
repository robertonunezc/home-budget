from abc import ABC, abstractmethod
from openai import OpenAI
import os
from dotenv import load_dotenv

from services.upload.upload import UploadServiceFactory

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
class ProcessData(ABC):
    """
    Abstract base class for processing data.
    """

    @abstractmethod
    def extract_data_from_image(self, image_path: str) -> dict:
        """
        Extract data from an image.

        Args:
            image_path (str): Path to the image file.

        Returns:
            dict: Extracted data.
        """
        pass


class GptExtract(ProcessData):
    """
    Implementation of ProcessData using GPT for data extraction.
    """
    def __init__(self):
        """
        Initialize the GPT client with API key from environment variables.
        """
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Missing required OpenAI API key in environment variables")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.upload_service = UploadServiceFactory() 
        # Initialize the upload service
        

    def extract_data_from_image(self, image_url: str) -> dict:
        """
        Extract data from an image using GPT.

        Args:
            image_path (str): Path to the image file.

        Returns:
            dict: Extracted data.
        """

        # Download images from S3
        return {"data": "extracted data"}