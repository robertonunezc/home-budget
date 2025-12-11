"""
Example usage of the Repository Pattern implementation.

This script demonstrates how to use the repository pattern to:
- Create and save receipts
- Find receipts by ID and user ID
- Update receipts
- Use business logic methods
- Switch between database backends
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from repositories.repository_factory import RepositoryFactory
from services.store_data.store_data import ServiceType
from entities.receipt import Receipt, ReceiptItem
from datetime import datetime
from decimal import Decimal


def example_basic_crud():
    """Example: Basic CRUD operations"""
    print("\n=== Example 1: Basic CRUD Operations ===\n")
    
    # Create repository (using PostgreSQL)
    repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
    
    # Create a new receipt
    receipt = Receipt(
        user_id="user_12345",
        image_url="https://s3.amazonaws.com/my-bucket/receipt_001.jpg"
    )
    
    print(f"Created receipt with ID: {receipt.receipt_id}")
    
    # Save the receipt
    saved_receipt = repo.save(receipt)
    print(f"Saved receipt to database")
    
    # Find by ID
    found_receipt = repo.find_by_id(receipt.receipt_id)
    if found_receipt:
        print(f"Found receipt: {found_receipt.receipt_id}")
    
    # Check if exists
    exists = repo.exists(receipt.receipt_id)
    print(f"Receipt exists: {exists}")
    
    # Delete receipt (commented out to keep the example safe)
    # repo.delete(receipt.receipt_id)
    # print(f"Deleted receipt")


def example_business_logic():
    """Example: Using business logic methods"""
    print("\n=== Example 2: Business Logic Methods ===\n")
    
    # Create receipt
    receipt = Receipt(
        user_id="user_67890",
        image_url="https://s3.amazonaws.com/my-bucket/receipt_002.jpg"
    )
    
    # Add items using business logic
    receipt.add_item(ReceiptItem(
        name="Coffee",
        price=4.50,
        quantity=2,
        category="beverages"
    ))
    
    receipt.add_item(ReceiptItem(
        name="Croissant",
        price=3.25,
        quantity=1,
        category="bakery"
    ))
    
    receipt.add_item(ReceiptItem(
        name="Orange Juice",
        price=5.00,
        quantity=1,
        category="beverages"
    ))
    
    # Calculate total
    total = receipt.calculate_total()
    print(f"Receipt total: ${total}")
    print(f"Number of items: {len(receipt.items)}")
    
    # Get items by category
    beverages = receipt.get_items_by_category("beverages")
    print(f"Beverage items: {len(beverages)}")
    for item in beverages:
        print(f"  - {item.name}: ${item.price}")
    
    # Get receipt summary
    summary = receipt.get_summary()
    print(f"\nReceipt Summary:")
    print(f"  Receipt ID: {summary['receipt_id']}")
    print(f"  User ID: {summary['user_id']}")
    print(f"  Total: ${summary['total_amount']}")
    print(f"  Items: {summary['item_count']}")
    print(f"  Categories: {', '.join(summary['categories'])}")
    
    # Validate before saving
    if receipt.is_valid():
        print("\nReceipt is valid and ready to save")
    
    # Save using repository
    repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
    repo.save(receipt)
    print(f"Receipt saved to database")


def example_update_receipt():
    """Example: Updating a receipt"""
    print("\n=== Example 3: Updating Receipt ===\n")
    
    repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
    
    # Create and save initial receipt
    receipt = Receipt(
        user_id="user_update_test",
        image_url="https://s3.amazonaws.com/my-bucket/receipt_003.jpg"
    )
    repo.save(receipt)
    print(f"Created receipt: {receipt.receipt_id}")
    
    # Update using repository method
    updated_receipt = repo.update(
        receipt.receipt_id,
        total_amount=Decimal("99.99"),
        purchase_date=datetime.now()
    )
    
    if updated_receipt:
        print(f"Updated receipt total to: ${updated_receipt.total_amount}")
    
    # Alternative: Update using business logic
    receipt.update_fields(
        purchase_date=datetime.now(),
        total_amount=Decimal("150.00")
    )
    repo.save(receipt)
    print(f"Updated receipt using business logic")


def example_find_by_user():
    """Example: Finding receipts by user"""
    print("\n=== Example 4: Find Receipts by User ===\n")
    
    repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
    
    # Find all receipts for a user
    user_id = "user_12345"
    receipts = repo.find_by_user_id(user_id, limit=10)
    
    print(f"Found {len(receipts)} receipts for user {user_id}")
    for receipt in receipts:
        print(f"  Receipt {receipt.receipt_id}: ${receipt.total_amount}")


def example_different_backends():
    """Example: Using different database backends"""
    print("\n=== Example 5: Different Database Backends ===\n")
    
    # PostgreSQL repository
    postgres_repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
    print("Created PostgreSQL repository")
    
    # DynamoDB repository
    dynamodb_repo = RepositoryFactory.create_receipt_repository(ServiceType.DYNAMODB)
    print("Created DynamoDB repository")
    
    # Both repositories have the same interface
    receipt = Receipt(
        user_id="multi_backend_user",
        image_url="https://s3.amazonaws.com/my-bucket/receipt_multi.jpg"
    )
    
    # Save to PostgreSQL
    postgres_repo.save(receipt)
    print(f"Saved to PostgreSQL: {receipt.receipt_id}")
    
    # Can also save to DynamoDB (same receipt, same interface)
    # dynamodb_repo.save(receipt)
    # print(f"Saved to DynamoDB: {receipt.receipt_id}")


def example_complete_workflow():
    """Example: Complete workflow like in Telegram bot"""
    print("\n=== Example 6: Complete Workflow ===\n")
    
    repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
    
    # Step 1: Create initial receipt with image
    receipt = Receipt(
        user_id="telegram_user_123",
        image_url="https://s3.amazonaws.com/my-bucket/telegram_receipt.jpg"
    )
    repo.save(receipt)
    print(f"Step 1: Created receipt {receipt.receipt_id}")
    
    # Step 2: Extract items from GPT (simulated)
    extracted_items = [
        {"name": "COFFEE", "price": 6.32, "quantity": 1, "category": "beverages"},
        {"name": "BANANAS", "price": 1.78, "quantity": 3, "category": "produce"},
        {"name": "CORN TORT", "price": 1.98, "quantity": 1, "category": "grocery"},
    ]
    
    # Step 3: Add items to receipt
    for item_data in extracted_items:
        item = ReceiptItem(
            name=item_data["name"],
            price=item_data["price"],
            quantity=item_data["quantity"],
            category=item_data["category"]
        )
        receipt.add_item(item)
    
    # Step 4: Calculate total
    total = receipt.calculate_total()
    print(f"Step 2: Added {len(receipt.items)} items, total: ${total}")
    
    # Step 5: Update with purchase date
    receipt.update_fields(
        purchase_date=datetime.now()
    )
    
    # Step 6: Save updated receipt
    repo.save(receipt)
    print(f"Step 3: Updated and saved receipt")
    
    # Step 7: Retrieve and verify
    verified_receipt = repo.find_by_id(receipt.receipt_id)
    if verified_receipt:
        print(f"\nVerification:")
        print(f"  Receipt ID: {verified_receipt.receipt_id}")
        print(f"  User: {verified_receipt.user_id}")
        print(f"  Total: ${verified_receipt.total_amount}")
        print(f"  Items: {len(verified_receipt.items)}")
        print(f"  Purchase Date: {verified_receipt.purchase_date}")


if __name__ == "__main__":
    print("=" * 60)
    print("Repository Pattern Examples")
    print("=" * 60)
    
    try:
        # Run examples (comment out ones you don't want to run)
        example_basic_crud()
        example_business_logic()
        example_update_receipt()
        example_find_by_user()
        example_different_backends()
        example_complete_workflow()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        import traceback
        traceback.print_exc()
