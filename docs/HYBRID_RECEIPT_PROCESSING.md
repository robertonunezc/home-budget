# Hybrid Receipt Processing Implementation

## Overview
Implemented a 3-state status tracking model for receipt processing that combines the benefits of immediate persistence with data quality guarantees.

## Changes Made

### 1. Receipt Entity (`entities/receipt.py`)
- **Added `ReceiptStatus` enum** with 4 states:
  - `PENDING`: Receipt uploaded, awaiting OCR extraction
  - `PROCESSING`: Currently extracting data via GPT-4 Vision
  - `COMPLETED`: Successfully processed with all data
  - `FAILED`: Extraction or processing failed
  
- **Added `status` field** to Receipt model with default value `ReceiptStatus.PENDING`

### 2. Receipt Repository (`repositories/receipt_repository.py`)
- **Updated `_to_dict()` method**: Added `status` to allowed fields for both DynamoDB and PostgreSQL
- **Updated `_to_entity()` method**: Added conversion of status string to `ReceiptStatus` enum when reading from database

### 3. Telegram Bot (`telegram_bot/main.py`)
- **Renamed function**: `upload_picture` → `process_receipt_upload` (more descriptive name)
- **Implemented 3-phase workflow**:

#### Phase 1: Immediate Upload & Persistence
```python
# Upload to S3
url = upload_service.upload_file(temp_file_path, file_name)

# Create receipt with PENDING status
receipt = Receipt(user_id=user, image_url=url, status=ReceiptStatus.PENDING)
receipt_repository.save(receipt)

# Notify user immediately
await update.message.reply_text("✅ Receipt uploaded successfully! Processing...")
```

#### Phase 2: Data Extraction
```python
# Update to PROCESSING status
receipt_repository.update(receipt.receipt_id, status=ReceiptStatus.PROCESSING)

# Extract data using GPT-4 Vision
extracted_receipt = extract_receipt_text(file_full_path)
receipt_formatted = json.loads(extracted_receipt)
```

#### Phase 3: Completion
```python
# Update with extracted data + COMPLETED status
receipt_repository.update(
    receipt.receipt_id,
    purchase_date=datetime.now(),
    total_amount=total_amount,
    items=items,
    status=ReceiptStatus.COMPLETED
)

# Notify user with results
await update.message.reply_text("🎉 Receipt processed successfully!")
```

- **Enhanced error handling**:
  - Separate exception handler for JSON parsing errors
  - Automatic status update to FAILED on errors
  - Proper temp file cleanup in finally block
  - Detailed error messages to user with receipt ID

### 4. Database Migration (`migrations/add_status_column.sql`)
- **Added status column** to receipts table
- **Added check constraint** to enforce valid status values
- **Created index** on status for query performance
- **Backward compatibility**: Updates existing receipts to 'completed' if they have data

## Benefits of This Approach

### ✅ User Experience
- **Immediate feedback**: User knows upload succeeded right away
- **Progress tracking**: User sees "Processing..." status
- **Clear outcomes**: Success message with summary or failure notification

### ✅ Data Quality
- **No incomplete records** without tracking (status field identifies them)
- **Audit trail**: Can query all pending/failed receipts
- **Retry capability**: Failed receipts can be reprocessed

### ✅ System Reliability
- **Graceful failure handling**: Errors don't lose data
- **Idempotent operations**: Can retry extraction without re-uploading
- **Clean separation**: Upload success ≠ processing success

### ✅ Future Enhancements Enabled
- **Async processing**: Can move extraction to background workers/queues
- **Manual review**: Can filter `status='failed'` for human intervention
- **Analytics**: Track success rates, processing times, common failures
- **Batch processing**: Reprocess all `status='failed'` receipts

## Usage Queries

### Find receipts needing attention
```sql
-- All pending receipts (might be stuck)
SELECT * FROM receipts WHERE status = 'pending';

-- All failed receipts (need manual review)
SELECT * FROM receipts WHERE status = 'failed';

-- Only completed receipts (for reports)
SELECT * FROM receipts WHERE status = 'completed';
```

### Reprocess failed receipt
```python
# Update status to pending to trigger reprocessing
receipt_repository.update(receipt_id, status=ReceiptStatus.PENDING)
```

## Running the Migration

```bash
# Apply the migration
docker exec -it spends-postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -f /migrations/add_status_column.sql
```

Or if migrations are mounted in docker-compose:
```bash
docker exec -it spends-postgres psql -U postgres -d spends_db -f /docker-entrypoint-initdb.d/add_status_column.sql
```

## Testing Checklist

- [ ] Upload a valid receipt → should show PENDING, then COMPLETED
- [ ] Upload an image with no text → should show FAILED with error
- [ ] Check database has status column with correct values
- [ ] Verify error messages include receipt ID for debugging
- [ ] Confirm temp files are cleaned up even on errors
- [ ] Test backward compatibility with existing receipts

## Key Differences from Previous Implementation

| Aspect | Before | After |
|--------|--------|-------|
| Function name | `upload_picture` | `process_receipt_upload` |
| Status tracking | None | 4-state enum |
| User feedback | After extraction | Immediate + after extraction |
| Error recovery | Lost on failure | Receipt persisted, can retry |
| Database writes | 2 (create + update) | 2-3 (create + processing + complete) |
| Failed receipts | No record | Marked as 'failed' in DB |
| Temp file cleanup | Basic | try/finally with logging |
