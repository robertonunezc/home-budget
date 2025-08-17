#I want to create a telegram bot that upload photos using the upload service and authenticate users

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from services.upload.upload import UploadServiceFactory
from services.authentication.authenticate import AuthenticationService
from services.store_data.store_data import StoreDataServiceFactory
from entities.receipt import Receipt, ReceiptItem
from jose import jwt
from datetime import datetime, timedelta
from gpt_extract import extract_receipt_text
import os
import logging
import io
import tempfile
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_USERS = os.getenv("ALLOWED_USERS").split(",")

# Initialize the services
upload_service = UploadServiceFactory.create()
auth_service = AuthenticationService(secret_key=os.getenv("JWT_SECRET"))

# Define the start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Spends App Bot! 👋\n\n"
        "I can help you with:\n"
        "• Uploading photos to S3\n"
        "• Managing authentication\n\n"
        "Use /help to see all available commands."
    )

# Define the help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "You can also send me photos to upload them to S3."
    )

# Define the generate token handler
async def generate_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create a payload with user information
    user_id = update.effective_user.id
    username = update.effective_user.username or "unknown"
    
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
    }
    
    # Generate the token
    token = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")
    
    # Send the token to the user
    await update.message.reply_text(
        f"Here's your JWT token (valid for 7 days):\n\n`{token}`\n\n"
        "Keep this token secure and use it to authenticate your requests.",
        parse_mode="Markdown"
    )

# Define the verify token handler
async def verify_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the user provided a token
    if not context.args:
        await update.message.reply_text(
            "Please provide a token to verify.\n\n"
            "Usage: /verify_token YOUR_TOKEN"
        )
        return
    
    # Get the token from the command arguments
    token = context.args[0]
    
    try:
        # Verify the token
        payload = auth_service.authenticate(token)
        
        # Send the verification result to the user
        await update.message.reply_text(
            f"✅ Token is valid!\n\n"
            f"User ID: {payload.get('sub')}\n"
            f"Username: {payload.get('username')}\n"
            f"Expires: {datetime.fromtimestamp(payload.get('exp')).strftime('%Y-%m-%d %H:%M:%S')}"
        )
    except Exception as e:
        # Send the error message to the user
        await update.message.reply_text(f"❌ Token verification failed: {str(e)}")

# Define the upload handler
async def upload_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if not await authenticate_user(update, context):
    #     await update.message.reply_text("⛔You are not authorized to use this bot.")
    #     return
    try:
        # Get the photo file
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
        
        file_data = io.BytesIO()
        
        await photo_file.download_to_memory(out=file_data)
        
        file_data.seek(0)
        
        # Create a temporary file to store the photo
        # Get the original file extension from the file ID (e.g., .jpg, .png)
        file_extension = os.path.splitext(photo_file.file_path)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_data.read())
            temp_file_path = temp_file.name
        
        file_name = f"{update.message.photo[-1].file_id}{file_extension}"
        url = upload_service.upload_file(temp_file_path,file_name)
        # save the file info to the database
        if update.message:
            user = (
                update.message.from_user.username or
                update.message.from_user.first_name or
                f"user_{update.message.from_user.id}"
            )
        else:
            user = 'anonymous'
        
        # Create and save the receipt
        logger.info(f"Photo uploaded successfully! URL: {url}")
        receipt = Receipt(user_id=user, image_url=url)
        receipt.save()
        # extract text from the file
        file_full_path = os.path.join(os.getcwd(), temp_file_path)
        logger.info(f"Extracting text from the photo: {file_full_path}")
        extracted_receipt = extract_receipt_text(file_full_path)
        logger.info(f"Extracted from GPT: {extracted_receipt}")
        extracted_receipt = extracted_receipt.replace('```json', '').replace('```', '').strip()
        # update receipt info to the database
        receipt_formatted = json.loads(extracted_receipt)
        logger.info(f"JSON formatted extracted: {receipt_formatted}")

        """
            {
                "items": [
                    {
                    "name": "COFFEE",
                    "price": 6.32
                    },
                    {
                    "name": "BANANAS",
                    "quantity": "3.300 lb",
                    "unit_price": 0.54,
                    "price": 1.78
                    },
                    {
                    "name": "OM BN SZ MT",
                    "price": 2.84
                    },
                    {
                    "name": "CORN TORT",
                    "price": 1.98
                    },
                    {
                    "name": "CBT WCHXSH",
                    "price": 9.97
                    }
                ],
                "subtotal": 22.89,
                "total": 22.89,
                "debit_tend": 22.89,
                "change_due": 0.00
                }
        """
        items: list[ReceiptItem] = []
        if 'items' in receipt_formatted:
            for item in receipt_formatted['items']:
                item_name = item.get('name', 'Unknown Item')
                item_price = float(item.get('price', 0.0))
                item_quantity = int(item.get('quantity', 1)) if 'quantity' in item else 1
                item_category = item.get('category', 'other') if 'category' in item else 'other'
                
                items.append(ReceiptItem(name=item_name, price=item_price, quantity=item_quantity, category=item_category))
        else:
            logger.warning("No items found in the extracted receipt data.")
        
        receipt.update(
            purchase_date=datetime.now(),
            total_amount=float(receipt_formatted['total']) if 'total' in receipt_formatted else 0.0,  
            items=items, 
        )        
        # Delete the temporary file 
        os.unlink(temp_file_path)
        
        await update.message.reply_text(f"Photo uploaded successfully! 🎉\n\nURL: {url}")
        await update.message.reply_text("start extracting text from the photo")
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await update.message.reply_text(f"❌ Error processing photo: {str(e)}")

# Authenticate the user
async def authenticate_user(update: Update, context: ContextTypes.DEFAULT_TYPE)->bool:
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("You are not authorized to use this bot.")
        return False
    return True
    
    

# Define the main function
def main():
    # Initialize the application
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("generate_token", generate_token))
    application.add_handler(CommandHandler("verify_token", verify_token))
    
    # Add the upload handler
    application.add_handler(MessageHandler(filters.PHOTO, upload_picture))
    
    # Start the bot
    logger.info("Starting the bot...")
    application.run_polling()

if __name__ == "__main__":
    main()