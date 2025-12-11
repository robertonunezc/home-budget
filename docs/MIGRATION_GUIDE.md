# Migration Guide: Implementing Repository Pattern

## Quick Summary

The codebase has been refactored to implement the Repository Pattern, separating business logic from database operations.

## What Changed

### 1. Receipt Entity (`entities/receipt.py`)
**Before:**
```python
receipt = Receipt(user_id="user123", image_url="url")
receipt.save()  # Direct database access
receipt.update(total_amount=100)  # Save included
```

**After:**
```python
from repositories.repository_factory import RepositoryFactory
from services.store_data.store_data import ServiceType

repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
receipt = Receipt(user_id="user123", image_url="url")
repo.save(receipt)  # Database through repository

# For updates
receipt.update_fields(total_amount=100)
repo.save(receipt)  # Explicit save
```

### 2. New Components

#### Repositories Module
- `repositories/base_repository.py` - Base interfaces and abstract class
- `repositories/receipt_repository.py` - Receipt-specific implementation
- `repositories/repository_factory.py` - Factory for creating repositories

#### Repository Methods
- `save(entity)` - Create or update
- `find_by_id(id)` - Get by ID
- `find_by_user_id(user_id)` - Get user's receipts
- `delete(id)` - Delete by ID
- `exists(id)` - Check existence
- `update(id, **kwargs)` - Update fields

### 3. Receipt Entity Now Has Business Logic Only
- `add_item()` - Add receipt item
- `remove_item()` - Remove by name
- `calculate_total()` - Calculate total amount
- `update_fields()` - Update properties
- `is_valid()` - Validate receipt
- `get_items_by_category()` - Filter items
- `get_summary()` - Get summary dict

## Migration Steps

### For Existing Code That Uses Receipts

#### Step 1: Import Repository
```python
from repositories.repository_factory import RepositoryFactory
from services.store_data.store_data import ServiceType
```

#### Step 2: Create Repository Instance (Once)
```python
# At module level or in initialization
receipt_repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
```

#### Step 3: Replace Direct Saves
```python
# OLD
receipt = Receipt(...)
receipt.save()

# NEW
receipt = Receipt(...)
receipt_repo.save(receipt)
```

#### Step 4: Replace Updates
```python
# OLD
receipt.update(total_amount=100, items=[...])

# NEW
receipt.update_fields(total_amount=100, items=[...])
receipt_repo.save(receipt)
```

## Code Examples

### Complete Workflow (Telegram Bot Style)

```python
from repositories.repository_factory import RepositoryFactory
from services.store_data.store_data import ServiceType
from entities.receipt import Receipt, ReceiptItem

# Initialize repository (do this once)
repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)

# Create receipt
receipt = Receipt(user_id=user, image_url=url)
repo.save(receipt)

# Extract items from image (GPT/OCR)
items = []  # ... extracted from GPT

# Add items
for item_data in items:
    receipt.add_item(ReceiptItem(**item_data))

# Calculate total
receipt.calculate_total()

# Update additional fields
receipt.update_fields(purchase_date=datetime.now())

# Save changes
repo.save(receipt)
```

### Finding Receipts

```python
# Find by ID
receipt = repo.find_by_id("receipt_123")

# Find by user
user_receipts = repo.find_by_user_id("user_123", limit=10)

# Check existence
if repo.exists("receipt_123"):
    print("Receipt exists")

# Delete
repo.delete("receipt_123")
```

### Using Business Logic

```python
receipt = Receipt(user_id="user", image_url="url")

# Add items
receipt.add_item(ReceiptItem(name="Coffee", price=4.50, quantity=2))
receipt.add_item(ReceiptItem(name="Muffin", price=3.00, category="bakery"))

# Calculate total
total = receipt.calculate_total()  # Returns Decimal

# Get items by category
bakery_items = receipt.get_items_by_category("bakery")

# Get summary
summary = receipt.get_summary()

# Remove item
receipt.remove_item("Coffee")

# Validate before saving
if receipt.is_valid():
    repo.save(receipt)
```

## Files That Need Updates

If you have code that uses `Receipt.save()` or `Receipt.update()`, update it:

1. ✅ `telegram_bot/main.py` - Already updated
2. ✅ `entities/receipt.py` - Already updated
3. 🔍 Any custom scripts or endpoints using receipts

## Testing

Run the provided tests:
```bash
# Run repository tests
pytest tests/repositories/test_receipt_repository.py -v

# Run all tests
pytest tests/ -v
```

Run the examples:
```bash
python3 examples/repository_pattern_examples.py
```

## Benefits

1. **Separation of Concerns** - Business logic separate from database
2. **Testability** - Easy to mock repositories
3. **Flexibility** - Switch between PostgreSQL/DynamoDB easily
4. **Maintainability** - Clear boundaries between layers
5. **Reusability** - Repository methods can be reused

## Common Patterns

### Pattern 1: Create and Save
```python
receipt = Receipt(user_id="user", image_url="url")
repo.save(receipt)
```

### Pattern 2: Load, Modify, Save
```python
receipt = repo.find_by_id("receipt_id")
receipt.update_fields(total_amount=100)
repo.save(receipt)
```

### Pattern 3: Conditional Save
```python
receipt = Receipt(...)
receipt.add_item(ReceiptItem(...))
receipt.calculate_total()

if receipt.is_valid():
    repo.save(receipt)
```

### Pattern 4: Business Logic First
```python
receipt = Receipt(...)

# Use business methods
receipt.add_item(ReceiptItem(...))
receipt.calculate_total()
summary = receipt.get_summary()

# Then persist
repo.save(receipt)
```

## Troubleshooting

### Issue: "Receipt ID is required" error
**Solution:** The repository validates required fields. Ensure receipt has:
- `receipt_id` (auto-generated by default)
- `user_id`
- `image_url`

### Issue: Can't find repository module
**Solution:** Ensure Python path includes project root:
```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

### Issue: DynamoDB Decimal errors
**Solution:** Repository automatically converts `Decimal` to `str` for DynamoDB compatibility.

### Issue: Need to switch database
**Solution:** Change `ServiceType` when creating repository:
```python
# PostgreSQL
repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)

# DynamoDB
repo = RepositoryFactory.create_receipt_repository(ServiceType.DYNAMODB)
```

## Questions?

See the full documentation in `REPOSITORY_PATTERN.md` or check the examples in `examples/repository_pattern_examples.py`.
