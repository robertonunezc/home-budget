#!/usr/bin/env python
import os
import sys
import logging
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
    # Check if the TELEGRAM_BOT_TOKEN environment variable is set
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        sys.exit(1)
    
    # Check if the JWT_SECRET environment variable is set
    if not os.getenv("JWT_SECRET"):
        logger.error("JWT_SECRET environment variable is not set")
        sys.exit(1)
    
    # Import and run the Telegram bot
    try:
        from telegram_bot.main import main as run_bot
        logger.info("Starting the Telegram bot...")
        run_bot()
    except Exception as e:
        logger.error(f"Error running the Telegram bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 