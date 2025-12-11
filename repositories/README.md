# Repositories Module

This module implements the Repository Pattern for data access in the Spends App.

## Quick Start

```python
from repositories.repository_factory import RepositoryFactory
from services.store_data.store_data import ServiceType
from entities.receipt import Receipt, ReceiptItem

# Create repository
repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)

# Create receipt
receipt = Receipt(user_id="user123", image_url="https://...")

# Add items
receipt.add_item(ReceiptItem(name="Coffee", price=4.50))
receipt.calculate_total()

# Save
repo.save(receipt)

# Find
found = repo.find_by_id(receipt.receipt_id)

# Update
repo.update(receipt.receipt_id, total_amount=100)

# Delete
repo.delete(receipt.receipt_id)
```

## Module Structure

```
repositories/
├── __init__.py              # Module exports
├── base_repository.py       # Base interfaces and abstract class
├── receipt_repository.py    # Receipt repository implementation
└── repository_factory.py    # Factory for creating repositories
```

## Classes

### IRepository<T>
Generic interface defining the contract for all repositories.

**Methods:**
- `save(entity: T) -> T`
- `find_by_id(entity_id: str) -> Optional[T]`
- `find_all(filters, limit) -> List[T]`
- `delete(entity_id: str) -> bool`
- `exists(entity_id: str) -> bool`

### BaseRepository<T>
Abstract base class with common functionality.

**Abstract Methods:**
- `_to_entity(data: Dict) -> T` - Convert dict to entity
- `_to_dict(entity: T) -> Dict` - Convert entity to dict

### ReceiptRepository
Concrete implementation for Receipt entities.

**Additional Methods:**
- `find_by_user_id(user_id: str, limit: int) -> List[Receipt]`
- `update(receipt_id: str, **kwargs) -> Optional[Receipt]`

**Features:**
- Automatic datetime conversion
- Decimal to string conversion for DynamoDB
- Data validation before save
- Error handling and logging

### RepositoryFactory
Factory for creating repository instances.

**Methods:**
- `create_receipt_repository(service_type: ServiceType) -> ReceiptRepository`
- `clear_cache()` - Clear cached instances (for testing)

**Features:**
- Singleton pattern for repositories
- Supports PostgreSQL and DynamoDB
- Cached instances for performance

## Usage Examples

### Basic CRUD

```python
repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)

# Create and save
receipt = Receipt(user_id="user", image_url="url")
repo.save(receipt)

# Find by ID
receipt = repo.find_by_id("receipt_id")

# Check existence
if repo.exists("receipt_id"):
    print("Receipt exists")

# Delete
repo.delete("receipt_id")
```

### Business Logic Integration

```python
# Create receipt
receipt = Receipt(user_id="user", image_url="url")

# Use business methods
receipt.add_item(ReceiptItem(name="Coffee", price=4.50, quantity=2))
receipt.add_item(ReceiptItem(name="Muffin", price=3.00))
receipt.calculate_total()  # Automatically calculates

# Validate and save
if receipt.is_valid():
    repo.save(receipt)
```

### Finding Receipts

```python
# By ID
receipt = repo.find_by_id("receipt_123")

# By user ID
user_receipts = repo.find_by_user_id("user_123", limit=10)

# Process results
for receipt in user_receipts:
    summary = receipt.get_summary()
    print(f"Receipt {summary['receipt_id']}: ${summary['total_amount']}")
```

### Updating Receipts

```python
# Method 1: Using repository update
repo.update("receipt_id", total_amount=100.50, purchase_date=datetime.now())

# Method 2: Using business logic
receipt = repo.find_by_id("receipt_id")
receipt.update_fields(total_amount=100.50)
receipt.add_item(ReceiptItem(name="New Item", price=10.00))
repo.save(receipt)
```

## Database Support

### PostgreSQL
- Full CRUD operations
- Transaction support
- Type conversions
- Error handling

### DynamoDB
- Full CRUD operations
- Automatic Decimal to string conversion
- NoSQL optimizations
- AWS credentials from environment

## Switching Backends

```python
# Use PostgreSQL
postgres_repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)

# Use DynamoDB
dynamodb_repo = RepositoryFactory.create_receipt_repository(ServiceType.DYNAMODB)

# Same interface for both!
receipt = Receipt(user_id="user", image_url="url")
postgres_repo.save(receipt)  # Saves to PostgreSQL
dynamodb_repo.save(receipt)  # Saves to DynamoDB
```

## Testing

```python
# Unit tests with mock
class MockStoreService:
    def save(self, table_name, data):
        return data
    def get(self, key):
        return None

repo = ReceiptRepository(MockStoreService())
receipt = Receipt(user_id="test", image_url="test.jpg")
repo.save(receipt)
```

Run tests:
```bash
pytest tests/repositories/test_receipt_repository.py -v
```

## Best Practices

1. **Always use factory to create repositories**
   ```python
   # Good
   repo = RepositoryFactory.create_receipt_repository()
   
   # Avoid
   store_service = StoreDataServiceFactory.create()
   repo = ReceiptRepository(store_service)  # Manual creation
   ```

2. **Validate before saving**
   ```python
   if receipt.is_valid():
       repo.save(receipt)
   ```

3. **Use business logic methods**
   ```python
   # Good - business logic in entity
   receipt.add_item(item)
   receipt.calculate_total()
   repo.save(receipt)
   
   # Avoid - manipulating data directly
   receipt.items.append(item)
   receipt.total_amount = sum(...)
   ```

4. **Handle not found cases**
   ```python
   receipt = repo.find_by_id("id")
   if receipt:
       # Process receipt
   else:
       # Handle not found
   ```

## Adding New Repositories

To add a repository for a new entity:

1. **Create entity** (pure business logic)
   ```python
   # entities/user.py
   class User(BaseModel):
       user_id: str
       username: str
   ```

2. **Create repository**
   ```python
   # repositories/user_repository.py
   class UserRepository(BaseRepository[User]):
       def _to_entity(self, data: Dict) -> User:
           return User(**data)
       
       def _to_dict(self, entity: User) -> Dict:
           return entity.model_dump()
   ```

3. **Add factory method**
   ```python
   # repositories/repository_factory.py
   @staticmethod
   def create_user_repository(service_type: ServiceType) -> UserRepository:
       store_service = StoreDataServiceFactory.create(service_type)
       return UserRepository(store_service, table_name='users')
   ```

4. **Update exports**
   ```python
   # repositories/__init__.py
   from repositories.user_repository import UserRepository
   __all__ = [..., 'UserRepository']
   ```

## Error Handling

The repository handles common errors:

- **ValueError**: Missing required fields
- **Database errors**: Logged and re-raised
- **Conversion errors**: Handled in `_to_entity()` and `_to_dict()`

```python
try:
    repo.save(receipt)
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Database error: {e}")
```

## Logging

All repository operations are logged:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Repository logs will show:
# - Save operations
# - Find operations
# - Delete operations
# - Errors
```

## Documentation

- **Full documentation**: See `REPOSITORY_PATTERN.md`
- **Migration guide**: See `MIGRATION_GUIDE.md`
- **Examples**: See `examples/repository_pattern_examples.py`
- **Architecture**: See `docs/architecture_diagram.py`

## Dependencies

- `pydantic` - Data validation
- `typing` - Type hints
- `datetime` - Timestamp handling
- `decimal` - Precise calculations
- `logging` - Operation logging
- `services.store_data` - Database services

## License

Part of the Spends App project.
