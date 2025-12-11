# Spends App - AI Coding Agent Instructions

## Architecture Overview

This is a receipt management system with three main interfaces:
1. **FastAPI REST API** (`main.py`) - HTTP endpoints for file uploads
2. **Telegram Bot** (`telegram_bot/main.py`) - Primary user interface for uploading receipt photos
3. **Shared Services** - Storage (S3/DynamoDB/Postgres), authentication (JWT), and OCR processing (OpenAI GPT-4 Vision)

**Key Data Flow**: User sends photo → Telegram bot → S3 upload → GPT-4 Vision OCR → Receipt entity → DynamoDB/Postgres

## Critical Setup Requirements

### Module Resolution
Always add parent directory to Python path in entry point scripts:
```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```
All service directories (`services/`, `entities/`) require `__init__.py` files to be valid Python packages.

### Environment Variables (.env required)
```bash
# AWS (S3 + DynamoDB)
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_BUCKET_NAME

# Telegram
TELEGRAM_BOT_TOKEN, ALLOWED_USERS (comma-separated user IDs)

# Auth
JWT_SECRET

# OpenAI (for OCR)
OPENAI_API_KEY

# Postgres (optional, DynamoDB is default)
POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
```

### IAM Permissions
AWS user needs: `s3:PutObject`, `s3:GetObject` on bucket, and full DynamoDB access on `receipts` table.

## Service Architecture Patterns

### Factory Pattern for Storage
```python
# Singleton factories with configurable backends
from services.store_data.store_data import StoreDataServiceFactory, ServiceType

# DynamoDB (default)
store = StoreDataServiceFactory.create()

# PostgreSQL
store = StoreDataServiceFactory.create(ServiceType.POSTGRES)
```

Both `StoreDataServiceFactory` and `UploadServiceFactory` use singleton pattern - instances are cached and reused.

### Entity Pattern: Receipt
`entities/receipt.py` uses Pydantic models with custom serialization:
- `to_dict()` converts datetime → ISO strings, Decimal → string for DynamoDB
- `save()` validates required fields and delegates to storage service
- `update(**kwargs)` modifies fields and auto-updates `updated_at` timestamp

## Running the Application

**Telegram Bot** (primary interface):
```bash
python3 ./telegram_bot/main.py
# or via wrapper: ./run_telegram_bot.py
```

**FastAPI** (secondary interface):
```bash
python3 main.py
# or via wrapper: ./run_api.py
```

**Local Services**:
```bash
docker-compose up -d  # Starts postgres + redis
```

**Tests**:
```bash
pytest tests/
```

## Telegram Bot Workflow

1. User sends photo → `upload_picture()` handler
2. Download photo to temp file → Upload to S3 (path: `uploads/tickets/{file_id}.jpg`)
3. Create Receipt entity with `user_id` and `image_url`, call `receipt.save()`
4. Extract text via `gpt_extract.extract_receipt_text()` (GPT-4 Vision API)
5. Parse JSON response → Update receipt with items, total, purchase date
6. Receipt items include: name, price, quantity, category (auto-categorized by GPT)

**User Authentication**: Currently commented out but checks `ALLOWED_USERS` env var.

## Key Conventions

- **Logging**: All services use Python `logging` module at INFO level
- **Error Handling**: Services log errors and re-raise; HTTP endpoints return HTTPException
- **Temp Files**: Use `tempfile.NamedTemporaryFile(delete=False)` and manual `os.unlink()` after processing
- **Datetime Handling**: Always use `datetime.now()` (not utcnow), serialize to ISO format for storage
- **S3 Paths**: Hardcoded prefix `uploads/tickets/` for all receipt images

## Testing

Tests use pytest. Example pattern from `tests/services/authentication/test_authenticate.py` (import and test JWT decode/encode).

Run via: `python3 run_tests.py` or `pytest tests/`

## Known Issues & Workarounds

- **DynamoDB Decimals**: Convert `Decimal` to `str` before saving to avoid serialization errors
- **OpenAI API**: Uses non-standard `client.responses.create()` method (check if this is correct API)
- **Postgres get/delete**: Methods have placeholder `table_name` in queries - needs table name parameter passed correctly

## Dependencies

Core: `fastapi`, `python-telegram-bot`, `boto3`, `openai`, `python-jose`, `psycopg2-binary`, `pydantic`

OCR libraries (multiple options): `pytesseract`, `opencv-python`, `paddleocr` (GPT-4 Vision is currently used)
