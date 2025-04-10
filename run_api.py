#!/usr/bin/env python
import os
import sys
import logging
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Check if the JWT_SECRET environment variable is set
    if not os.getenv("JWT_SECRET"):
        logger.error("JWT_SECRET environment variable is not set")
        sys.exit(1)
    
    # Check if the AWS environment variables are set
    required_aws_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "AWS_BUCKET_NAME"
    ]
    
    for var in required_aws_vars:
        if not os.getenv(var):
            logger.error(f"{var} environment variable is not set")
            sys.exit(1)
    
    # Run the FastAPI application
    try:
        logger.info("Starting the FastAPI application...")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"Error running the FastAPI application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 