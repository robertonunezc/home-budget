"""
Visual architecture diagram showing the repository pattern layers.
"""

ARCHITECTURE_DIAGRAM = """
╔══════════════════════════════════════════════════════════════════════════╗
║                        REPOSITORY PATTERN ARCHITECTURE                    ║
╚══════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   telegram_bot/main.py          main.py (FastAPI)                        │
│   ┌─────────────────┐           ┌─────────────────┐                     │
│   │ upload_picture  │           │ POST /upload    │                     │
│   │                 │           │                 │                     │
│   │ - Get photo     │           │ - Upload file   │                     │
│   │ - Upload to S3  │           │ - Authenticate  │                     │
│   │ - Create receipt│           │ - Return URL    │                     │
│   └────────┬────────┘           └────────┬────────┘                     │
│            │                              │                               │
└────────────┼──────────────────────────────┼───────────────────────────────┘
             │                              │
             ▼                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   entities/receipt.py                                                     │
│   ┌─────────────────────────────────────────────────────────────┐       │
│   │ class Receipt(BaseModel)                                     │       │
│   │                                                              │       │
│   │  Business Methods (No Database Logic):                      │       │
│   │  • add_item(item) → None                                    │       │
│   │  • remove_item(name) → bool                                 │       │
│   │  • calculate_total() → Decimal                              │       │
│   │  • update_fields(**kwargs) → None                           │       │
│   │  • is_valid() → bool                                        │       │
│   │  • get_items_by_category(category) → List[ReceiptItem]     │       │
│   │  • get_summary() → dict                                     │       │
│   └─────────────────────────────────────────────────────────────┘       │
│                                                                           │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       REPOSITORY LAYER                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   repositories/repository_factory.py                                      │
│   ┌─────────────────────────────────────────────────────────┐           │
│   │ RepositoryFactory                                        │           │
│   │  • create_receipt_repository(service_type) → Repository │           │
│   └─────────────────────────────────────────────────────────┘           │
│                          │                                                │
│                          ▼                                                │
│   repositories/receipt_repository.py                                      │
│   ┌─────────────────────────────────────────────────────────┐           │
│   │ class ReceiptRepository(BaseRepository[Receipt])         │           │
│   │                                                          │           │
│   │  Data Access Methods:                                   │           │
│   │  • save(entity: Receipt) → Receipt                      │           │
│   │  • find_by_id(id: str) → Optional[Receipt]             │           │
│   │  • find_by_user_id(user_id: str) → List[Receipt]       │           │
│   │  • find_all(filters, limit) → List[Receipt]            │           │
│   │  • delete(id: str) → bool                               │           │
│   │  • exists(id: str) → bool                               │           │
│   │  • update(id: str, **kwargs) → Optional[Receipt]       │           │
│   │                                                          │           │
│   │  Private Methods:                                        │           │
│   │  • _to_entity(data: dict) → Receipt                     │           │
│   │  • _to_dict(entity: Receipt) → dict                     │           │
│   └─────────────────────────────────────────────────────────┘           │
│                                                                           │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      DATA ACCESS LAYER                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   services/store_data/store_data.py                                       │
│   ┌──────────────────────────┐      ┌──────────────────────────┐        │
│   │ PostgresStoreDataService │      │ DynamoDBStoreDataService │        │
│   │                          │      │                          │        │
│   │ • save(table, data)      │      │ • save(table, data)      │        │
│   │ • get(data)              │      │ • get(data)              │        │
│   │ • delete(data)           │      │ • delete(data)           │        │
│   └────────┬─────────────────┘      └────────┬─────────────────┘        │
│            │                                  │                           │
└────────────┼──────────────────────────────────┼───────────────────────────┘
             │                                  │
             ▼                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE LAYER                                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   ┌──────────────────┐                    ┌──────────────────┐          │
│   │   PostgreSQL     │                    │    DynamoDB      │          │
│   │                  │                    │                  │          │
│   │  receipts table  │                    │  receipts table  │          │
│   └──────────────────┘                    └──────────────────┘          │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════╗
║                            DATA FLOW EXAMPLE                              ║
╚══════════════════════════════════════════════════════════════════════════╝

1. USER UPLOADS PHOTO (Telegram Bot)
   │
   ├─→ Telegram bot receives photo
   │
   ├─→ Upload to S3 (upload_service.upload_file())
   │
   ├─→ Create Receipt entity
   │   receipt = Receipt(user_id="user123", image_url="s3://...")
   │
   ├─→ Save through repository
   │   receipt_repository.save(receipt)
   │
   └─→ Receipt stored in database

2. EXTRACT TEXT FROM IMAGE (GPT-4 Vision)
   │
   ├─→ Call GPT API (extract_receipt_text())
   │
   ├─→ Parse JSON response
   │
   ├─→ Add items to receipt (business logic)
   │   for item_data in extracted_items:
   │       receipt.add_item(ReceiptItem(**item_data))
   │
   ├─→ Calculate total (business logic)
   │   receipt.calculate_total()
   │
   ├─→ Update fields (business logic)
   │   receipt.update_fields(purchase_date=datetime.now())
   │
   └─→ Save through repository
       receipt_repository.save(receipt)

3. RETRIEVE RECEIPT
   │
   ├─→ Find by ID
   │   receipt = receipt_repository.find_by_id("receipt_id")
   │
   ├─→ Use business methods
   │   summary = receipt.get_summary()
   │   beverages = receipt.get_items_by_category("beverages")
   │
   └─→ Return to user


╔══════════════════════════════════════════════════════════════════════════╗
║                        SEPARATION OF CONCERNS                             ║
╚══════════════════════════════════════════════════════════════════════════╝

┌────────────────────┬──────────────────────────────────────────────────────┐
│ Layer              │ Responsibility                                       │
├────────────────────┼──────────────────────────────────────────────────────┤
│ Presentation       │ • Handle HTTP requests / Telegram messages           │
│                    │ • User authentication                                │
│                    │ • File uploads                                       │
│                    │ • Response formatting                                │
├────────────────────┼──────────────────────────────────────────────────────┤
│ Business Logic     │ • Domain rules (calculate_total, validation)         │
│                    │ • Item management (add, remove)                      │
│                    │ • Data transformations                               │
│                    │ • NO database knowledge                              │
├────────────────────┼──────────────────────────────────────────────────────┤
│ Repository         │ • CRUD operations                                    │
│                    │ • Entity ↔ Database conversions                     │
│                    │ • Query logic                                        │
│                    │ • Data validation before save                        │
├────────────────────┼──────────────────────────────────────────────────────┤
│ Data Access        │ • Database connections                               │
│                    │ • SQL / NoSQL operations                             │
│                    │ • Transaction management                             │
│                    │ • Connection pooling                                 │
├────────────────────┼──────────────────────────────────────────────────────┤
│ Infrastructure     │ • Actual databases (PostgreSQL, DynamoDB)            │
│                    │ • Cloud services (S3, AWS)                           │
│                    │ • External APIs                                      │
└────────────────────┴──────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════╗
║                           KEY BENEFITS                                    ║
╚══════════════════════════════════════════════════════════════════════════╝

✓ Separation of Concerns
  └─→ Each layer has single responsibility

✓ Testability
  ├─→ Business logic testable without database
  ├─→ Repositories easily mocked
  └─→ Unit tests don't need database

✓ Flexibility
  ├─→ Switch between PostgreSQL ↔ DynamoDB
  ├─→ Add new storage backends easily
  └─→ Change database without touching business logic

✓ Maintainability
  ├─→ Clear boundaries between layers
  ├─→ Easy to locate issues
  └─→ Changes isolated to single layer

✓ Reusability
  ├─→ Repository methods used across app
  ├─→ Business logic reusable
  └─→ Single source of truth for data access
"""

if __name__ == "__main__":
    print(ARCHITECTURE_DIAGRAM)
