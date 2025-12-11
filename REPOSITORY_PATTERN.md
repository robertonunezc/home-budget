# Repository Pattern Implementation

## Overview

This project now implements the **Repository Pattern** to separate business logic from database operations. The Receipt entity is now a pure business object with no database dependencies, while all data access is handled through repositories.

## Architecture

```
┌─────────────────────────────────────────────────┐
│           Presentation Layer                    │
│  (telegram_bot, FastAPI endpoints)              │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│         Business Logic Layer                    │
│    (entities/receipt.py - Receipt class)        │
│    • add_item()                                 │
│    • calculate_total()                          │
│    • is_valid()                                 │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│          Repository Layer                       │
│  (repositories/receipt_repository.py)           │
│    • save()                                     │
│    • find_by_id()                               │
│    • find_by_user_id()                          │
│    • delete()                                   │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│         Data Access Layer                       │
│  (services/store_data/store_data.py)            │
│    • DynamoDBStoreDataService                   │
│    • PostgresStoreDataService                   │
└─────────────────────────────────────────────────┘
```

## Key Components

### 1. Base Repository Interface (`repositories/base_repository.py`)

Defines the contract that all repositories must implement:

- `IRepository<T>`: Generic interface with CRUD operations
- `BaseRepository<T>`: Abstract base class with common functionality

### 2. Receipt Repository (`repositories/receipt_repository.py`)

Concrete implementation for Receipt entities:

```python
class ReceiptRepository(BaseRepository[Receipt]):
    def save(self, entity: Receipt) -> Receipt
    def find_by_id(self, receipt_id: str) -> Optional[Receipt]
    def find_by_user_id(self, user_id: str, limit: Optional[int]) -> List[Receipt]
    def find_all(self, filters: Dict, limit: Optional[int]) -> List[Receipt]
    def delete(self, receipt_id: str) -> bool
    def exists(self, receipt_id: str) -> bool
    def update(self, receipt_id: str, **kwargs) -> Optional[Receipt]
```

### 3. Repository Factory (`repositories/repository_factory.py`)

Centralized factory for creating repository instances:

```python
class RepositoryFactory:
    @staticmethod
    def create_receipt_repository(service_type: ServiceType) -> ReceiptRepository
```

### 4. Receipt Entity (`entities/receipt.py`)

Pure business logic with no database dependencies:

```python
class Receipt(BaseModel):
    # Business methods only
    def add_item(self, item: ReceiptItem) -> None
    def remove_item(self, item_name: str) -> bool
    def calculate_total(self) -> Decimal
    def update_fields(self, **kwargs) -> None
    def is_valid(self) -> bool
    def get_items_by_category(self, category: str) -> List[ReceiptItem]
    def get_summary(self) -> dict
```

## Usage Examples

### Basic CRUD Operations

```python
from repositories.repository_factory import RepositoryFactory
from services.store_data.store_data import ServiceType
from entities.receipt import Receipt, ReceiptItem

# Create repository instance
repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)

# Create a new receipt
receipt = Receipt(
    user_id="user123",
    image_url="https://s3.amazonaws.com/bucket/receipt.jpg"
)

# Add items using business logic
receipt.add_item(ReceiptItem(
    name="Coffee",
    price=4.50,
    quantity=2,
    category="beverages"
))

# Calculate total
receipt.calculate_total()

# Save through repository
repo.save(receipt)

# Retrieve receipt
found_receipt = repo.find_by_id(receipt.receipt_id)

# Update receipt
updated_receipt = repo.update(
    receipt.receipt_id,
    total_amount=15.50
)

# Delete receipt
repo.delete(receipt.receipt_id)
```

### Finding Receipts by User

```python
# Get all receipts for a user (with optional limit)
user_receipts = repo.find_by_user_id("user123", limit=10)

for receipt in user_receipts:
    print(f"Receipt {receipt.receipt_id}: ${receipt.total_amount}")
```

### Using Business Logic Methods

```python
# Create receipt
receipt = Receipt(user_id="user123", image_url="https://...")

# Add items
receipt.add_item(ReceiptItem(name="Milk", price=3.99, category="dairy"))
receipt.add_item(ReceiptItem(name="Bread", price=2.49, category="bakery"))

# Calculate total automatically
total = receipt.calculate_total()  # Returns Decimal('6.48')

# Get items by category
dairy_items = receipt.get_items_by_category("dairy")

# Check validity
if receipt.is_valid():
    repo.save(receipt)

# Get summary
summary = receipt.get_summary()
# {
#     'receipt_id': '...',
#     'user_id': 'user123',
#     'total_amount': 6.48,
#     'item_count': 2,
#     'categories': ['dairy', 'bakery']
# }
```

### Switching Between Database Backends

```python
from services.store_data.store_data import ServiceType

# Use DynamoDB
dynamodb_repo = RepositoryFactory.create_receipt_repository(ServiceType.DYNAMODB)

# Use PostgreSQL
postgres_repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)

# Both have the same interface!
receipt = Receipt(user_id="user123", image_url="https://...")
dynamodb_repo.save(receipt)  # Saves to DynamoDB
postgres_repo.save(receipt)  # Saves to PostgreSQL
```

## Integration with Telegram Bot

The telegram bot now uses the repository pattern:

```python
# Initialize repository
receipt_repository = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)

# Create receipt
receipt = Receipt(user_id=user, image_url=url)
receipt_repository.save(receipt)

# Extract items from GPT
items = [...]  # parsed from GPT response

# Update using business logic
receipt.update_fields(
    purchase_date=datetime.now(),
    total_amount=float(receipt_data['total']),
    items=items
)

# Save updated receipt
receipt_repository.save(receipt)
```

## Benefits of This Implementation

### 1. Separation of Concerns
- **Entities**: Pure business logic, no database code
- **Repositories**: Handle all database operations
- **Services**: Provide infrastructure (S3, auth, etc.)

### 2. Testability
```python
# Easy to mock repositories in tests
class MockReceiptRepository:
    def save(self, entity):
        return entity

# Test business logic without database
receipt = Receipt(user_id="test", image_url="test.jpg")
receipt.add_item(ReceiptItem(name="Test", price=10.0))
assert receipt.calculate_total() == Decimal("10.0")
```

### 3. Flexibility
- Swap database backends without changing business logic
- Add new storage providers by implementing StoreDataInterface
- Cached repository instances for performance

### 4. Maintainability
- Clear boundaries between layers
- Single Responsibility Principle
- Easy to extend with new repository methods

## Migration from Old Code

### Before (Direct Database Access in Entity)
```python
class Receipt:
    def save(self):
        store_service = StoreDataServiceFactory.create()
        store_service.save(self.to_dict())
        
    def update(self, **kwargs):
        # ... update fields ...
        return self.save()
```

### After (Repository Pattern)
```python
# Entity has only business logic
class Receipt:
    def calculate_total(self) -> Decimal:
        # Business logic only
        pass

# Repository handles database
repo = RepositoryFactory.create_receipt_repository()
repo.save(receipt)
repo.update(receipt_id, total_amount=100)
```

## Adding New Repositories

To add a repository for a new entity:

1. **Create the entity** in `entities/` (pure business logic)
2. **Create repository** extending `BaseRepository<YourEntity>`
3. **Implement required methods**:
   - `save()`, `find_by_id()`, `delete()`, etc.
   - `_to_entity()` and `_to_dict()`
4. **Add factory method** to `RepositoryFactory`
5. **Update** `repositories/__init__.py`

Example:

```python
# entities/user.py
class User(BaseModel):
    user_id: str
    username: str
    email: str

# repositories/user_repository.py
class UserRepository(BaseRepository[User]):
    def _to_entity(self, data: Dict) -> User:
        return User(**data)
    
    def _to_dict(self, entity: User) -> Dict:
        return entity.model_dump()

# repositories/repository_factory.py
class RepositoryFactory:
    @staticmethod
    def create_user_repository(service_type: ServiceType) -> UserRepository:
        store_service = StoreDataServiceFactory.create(service_type)
        return UserRepository(store_service, table_name='users')
```

## Best Practices

1. **Never access database directly from entities**
2. **Always use repository methods for data operations**
3. **Keep business logic in entity methods**
4. **Use factory to create repositories** (ensures proper initialization)
5. **Validate in entities, not repositories** (use `is_valid()` before saving)
6. **Log operations in repositories** for debugging

## Testing

```python
# tests/repositories/test_receipt_repository.py
def test_save_receipt():
    repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
    receipt = Receipt(user_id="test", image_url="http://test.com/img.jpg")
    
    saved = repo.save(receipt)
    
    assert saved.receipt_id is not None
    assert repo.exists(saved.receipt_id)

def test_business_logic():
    receipt = Receipt(user_id="test", image_url="test.jpg")
    receipt.add_item(ReceiptItem(name="Item", price=10.0, quantity=2))
    
    total = receipt.calculate_total()
    
    assert total == Decimal("20.0")
    assert len(receipt.items) == 1
```

## Environment Configuration

The repository uses the same environment variables as before:

```bash
# Database selection (used when creating repository)
# POSTGRES or DYNAMODB

# PostgreSQL
POSTGRES_DB=your_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# DynamoDB
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

## Conclusion

The repository pattern provides a clean, maintainable architecture that separates business logic from data access. This makes the codebase easier to test, extend, and maintain while providing flexibility to switch between different database backends.
