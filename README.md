# Spends App

A FastAPI application for managing expenses and uploading files to S3, with a Telegram bot for easy interaction.

## Features

- FastAPI backend for file uploads and authentication
- Telegram bot for uploading photos and managing authentication
- JWT-based authentication
- S3 storage for uploaded files

## Setup

1. Make sure you have the required environment variables set in your `.env` file:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `JWT_SECRET`: Secret key for JWT token generation and verification
   - `AWS_ACCESS_KEY_ID`: Your AWS access key ID
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
   - `AWS_REGION`: Your AWS region
   - `AWS_BUCKET_NAME`: Your AWS S3 bucket name

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

You can run the API using the `run_api.py` script:

```bash
./run_api.py
```

The API will be available at http://localhost:8000.

## API Endpoints

- `GET /`: Root endpoint
- `POST /upload`: Upload a file to S3 (requires authentication)
- `GET /me`: Get the current user's information (requires authentication)

## Running the Telegram Bot

You can run the Telegram bot using the `run_telegram_bot.py` script:

```bash
./run_telegram_bot.py
```

## Telegram Bot Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/generate_token` - Generate a JWT token
- `/verify_token YOUR_TOKEN` - Verify a JWT token

## Authentication

The application uses JWT tokens for authentication. You can generate a token using the Telegram bot's `/generate_token` command and use it to authenticate requests to the API by including it in the `Authorization` header:

```
Authorization: Bearer YOUR_TOKEN
```

## Testing

You can run the tests using the `run_tests.py` script:

```bash
./run_tests.py
```

Or using pytest directly:

```bash
pytest
``` 