#I want to create a telegram bot that upload photos using the upload service and authenticate users

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from services.upload.upload import UploadServiceFactory
from services.authentication.authenticate import AuthenticationService
from jose import jwt
from datetime import datetime, timedelta
import os
import logging
import io
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        "/generate_token - Generate a JWT token\n"
        "/verify_token - Verify a JWT token\n\n"
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
async def upload_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Get the photo file
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
        
        # Create a BytesIO object to store the file
        file_data = io.BytesIO()
        
        # Download the photo file to the BytesIO object
        await photo_file.download_to_memory(out=file_data)
        
        # Reset the file pointer to the beginning
        file_data.seek(0)
        
        # Create a temporary file to store the photo
        # Get the original file extension from the file ID (e.g., .jpg, .png)
        file_extension = os.path.splitext(photo_file.file_path)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Write the BytesIO content to the temporary file
            temp_file.write(file_data.read())
            temp_file_path = temp_file.name
        
        # Upload the temporary file to S3
        file_name = f"{update.message.photo[-1].file_id}{file_extension}"
        url = upload_service.upload_file(temp_file_path,file_name)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        # Send the URL back to the user
        await update.message.reply_text(f"Photo uploaded successfully! 🎉\n\nURL: {url}")
    except Exception as e:
        logger.error(f"Error uploading photo: {e}")
        await update.message.reply_text(f"❌ Error uploading photo: {str(e)}")

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
    application.add_handler(MessageHandler(filters.PHOTO, upload_photo))
    
    # Start the bot
    logger.info("Starting the bot...")
    application.run_polling()

if __name__ == "__main__":
    main()