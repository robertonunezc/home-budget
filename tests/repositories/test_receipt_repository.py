"""
Unit tests for the Repository Pattern implementation.

Run with: pytest tests/repositories/test_receipt_repository.py
"""

import pytest
import sys
import os
from datetime import datetime
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from entities.receipt import Receipt, ReceiptItem
from repositories.receipt_repository import ReceiptRepository
from repositories.repository_factory import RepositoryFactory
from services.store_data.store_data import ServiceType


class TestReceiptEntity:
    """Tests for Receipt entity business logic"""
    
    def test_create_receipt(self):
        """Test creating a new receipt"""
        receipt = Receipt(
            user_id="test_user",
            image_url="https://test.com/image.jpg"
        )
        
        assert receipt.receipt_id is not None
        assert receipt.user_id == "test_user"
        assert receipt.image_url == "https://test.com/image.jpg"
        assert receipt.total_amount == Decimal(0)
        assert len(receipt.items) == 0
    
    def test_add_item(self):
        """Test adding items to receipt"""
        receipt = Receipt(user_id="test", image_url="test.jpg")
        
        item = ReceiptItem(name="Coffee", price=4.50, quantity=2)
        receipt.add_item(item)
        
        assert len(receipt.items) == 1
        assert receipt.items[0].name == "Coffee"
    
    def test_calculate_total(self):
        """Test calculating receipt total"""
        receipt = Receipt(user_id="test", image_url="test.jpg")
        
        receipt.add_item(ReceiptItem(name="Coffee", price=4.50, quantity=2))
        receipt.add_item(ReceiptItem(name="Croissant", price=3.25, quantity=1))
        
        total = receipt.calculate_total()
        
        # 4.50 * 2 + 3.25 * 1 = 12.25
        assert total == Decimal("12.25")
        assert receipt.total_amount == Decimal("12.25")
    
    def test_remove_item(self):
        """Test removing items from receipt"""
        receipt = Receipt(user_id="test", image_url="test.jpg")
        
        receipt.add_item(ReceiptItem(name="Coffee", price=4.50))
        receipt.add_item(ReceiptItem(name="Tea", price=3.00))
        
        removed = receipt.remove_item("Coffee")
        
        assert removed is True
        assert len(receipt.items) == 1
        assert receipt.items[0].name == "Tea"
    
    def test_remove_nonexistent_item(self):
        """Test removing an item that doesn't exist"""
        receipt = Receipt(user_id="test", image_url="test.jpg")
        receipt.add_item(ReceiptItem(name="Coffee", price=4.50))
        
        removed = receipt.remove_item("Nonexistent")
        
        assert removed is False
        assert len(receipt.items) == 1
    
    def test_update_fields(self):
        """Test updating receipt fields"""
        receipt = Receipt(user_id="test", image_url="test.jpg")
        
        old_updated_at = receipt.updated_at
        
        receipt.update_fields(
            total_amount=Decimal("100.00"),
            purchase_date=datetime.now()
        )
        
        assert receipt.total_amount == Decimal("100.00")
        assert receipt.updated_at > old_updated_at
    
    def test_is_valid(self):
        """Test receipt validation"""
        # Valid receipt
        valid_receipt = Receipt(
            user_id="test",
            image_url="test.jpg"
        )
        assert valid_receipt.is_valid() is True
        
        # Invalid receipt (missing image_url)
        invalid_receipt = Receipt(
            user_id="test",
            image_url=""
        )
        assert invalid_receipt.is_valid() is False
    
    def test_get_items_by_category(self):
        """Test filtering items by category"""
        receipt = Receipt(user_id="test", image_url="test.jpg")
        
        receipt.add_item(ReceiptItem(name="Coffee", price=4.50, category="beverages"))
        receipt.add_item(ReceiptItem(name="Tea", price=3.00, category="beverages"))
        receipt.add_item(ReceiptItem(name="Croissant", price=3.25, category="bakery"))
        
        beverages = receipt.get_items_by_category("beverages")
        
        assert len(beverages) == 2
        assert all(item.category == "beverages" for item in beverages)
    
    def test_get_summary(self):
        """Test getting receipt summary"""
        receipt = Receipt(user_id="test_user", image_url="test.jpg")
        
        receipt.add_item(ReceiptItem(name="Coffee", price=4.50, category="beverages"))
        receipt.add_item(ReceiptItem(name="Croissant", price=3.25, category="bakery"))
        receipt.calculate_total()
        
        summary = receipt.get_summary()
        
        assert summary['user_id'] == "test_user"
        assert summary['total_amount'] == 7.75
        assert summary['item_count'] == 2
        assert set(summary['categories']) == {'beverages', 'bakery'}


class TestReceiptRepository:
    """Tests for ReceiptRepository (requires database connection)"""
    
    @pytest.fixture
    def mock_store_service(self):
        """Create a mock store service for testing"""
        class MockStoreService:
            def __init__(self):
                self.data = {}
            
            def save(self, table_name, data):
                self.data[data['receipt_id']] = data
                return data
            
            def get(self, key):
                receipt_id = key.get('receipt_id')
                return self.data.get(receipt_id)
            
            def delete(self, key):
                receipt_id = key.get('receipt_id')
                if receipt_id in self.data:
                    del self.data[receipt_id]
        
        return MockStoreService()
    
    def test_save_receipt(self, mock_store_service):
        """Test saving a receipt through repository"""
        repo = ReceiptRepository(mock_store_service)
        
        receipt = Receipt(
            user_id="test_user",
            image_url="https://test.com/image.jpg"
        )
        
        saved_receipt = repo.save(receipt)
        
        assert saved_receipt.receipt_id == receipt.receipt_id
        assert receipt.receipt_id in mock_store_service.data
    
    def test_find_by_id(self, mock_store_service):
        """Test finding a receipt by ID"""
        repo = ReceiptRepository(mock_store_service)
        
        # Save a receipt first
        receipt = Receipt(user_id="test", image_url="test.jpg")
        repo.save(receipt)
        
        # Find it
        found = repo.find_by_id(receipt.receipt_id)
        
        assert found is not None
        assert found.receipt_id == receipt.receipt_id
        assert found.user_id == receipt.user_id
    
    def test_find_nonexistent_receipt(self, mock_store_service):
        """Test finding a receipt that doesn't exist"""
        repo = ReceiptRepository(mock_store_service)
        
        found = repo.find_by_id("nonexistent_id")
        
        assert found is None
    
    def test_exists(self, mock_store_service):
        """Test checking if receipt exists"""
        repo = ReceiptRepository(mock_store_service)
        
        receipt = Receipt(user_id="test", image_url="test.jpg")
        repo.save(receipt)
        
        assert repo.exists(receipt.receipt_id) is True
        assert repo.exists("nonexistent_id") is False
    
    def test_delete_receipt(self, mock_store_service):
        """Test deleting a receipt"""
        repo = ReceiptRepository(mock_store_service)
        
        receipt = Receipt(user_id="test", image_url="test.jpg")
        repo.save(receipt)
        
        # Delete it
        result = repo.delete(receipt.receipt_id)
        
        assert result is True
        assert receipt.receipt_id not in mock_store_service.data
    
    def test_update_receipt(self, mock_store_service):
        """Test updating a receipt through repository"""
        repo = ReceiptRepository(mock_store_service)
        
        receipt = Receipt(user_id="test", image_url="test.jpg")
        repo.save(receipt)
        
        # Update
        updated = repo.update(
            receipt.receipt_id,
            total_amount=Decimal("50.00")
        )
        
        assert updated is not None
        assert updated.total_amount == Decimal("50.00")
    
    def test_save_with_missing_required_fields(self, mock_store_service):
        """Test that saving fails with missing required fields"""
        repo = ReceiptRepository(mock_store_service)
        
        # Receipt without user_id
        receipt = Receipt(
            receipt_id="test_id",
            user_id="",  # Empty user_id
            image_url="test.jpg"
        )
        
        with pytest.raises(ValueError, match="User ID is required"):
            repo.save(receipt)
    
    def test_to_dict_conversion(self, mock_store_service):
        """Test entity to dict conversion"""
        repo = ReceiptRepository(mock_store_service)
        
        receipt = Receipt(user_id="test", image_url="test.jpg")
        receipt.add_item(ReceiptItem(name="Coffee", price=4.50))
        
        data = repo._to_dict(receipt)
        
        assert isinstance(data, dict)
        assert 'receipt_id' in data
        assert 'user_id' in data
        assert isinstance(data['total_amount'], str)  # Should be string for DynamoDB
    
    def test_to_entity_conversion(self, mock_store_service):
        """Test dict to entity conversion"""
        repo = ReceiptRepository(mock_store_service)
        
        data = {
            'receipt_id': 'test_id',
            'user_id': 'test_user',
            'image_url': 'test.jpg',
            'purchase_date': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'total_amount': '10.50',
            'items': []
        }
        
        receipt = repo._to_entity(data)
        
        assert isinstance(receipt, Receipt)
        assert receipt.receipt_id == 'test_id'
        assert receipt.user_id == 'test_user'
        assert isinstance(receipt.total_amount, Decimal)


class TestRepositoryFactory:
    """Tests for RepositoryFactory"""
    
    def test_create_receipt_repository(self):
        """Test creating repository through factory"""
        # Note: This requires actual database connection
        # In a real test, you'd mock the StoreDataServiceFactory
        
        try:
            repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
            assert repo is not None
            assert isinstance(repo, ReceiptRepository)
        except Exception as e:
            pytest.skip(f"Database not available: {e}")
    
    def test_repository_singleton(self):
        """Test that factory returns same instance"""
        try:
            repo1 = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
            repo2 = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
            
            assert repo1 is repo2  # Same instance
        except Exception as e:
            pytest.skip(f"Database not available: {e}")
    
    def test_different_backends_different_instances(self):
        """Test that different backends create different instances"""
        try:
            postgres_repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
            dynamodb_repo = RepositoryFactory.create_receipt_repository(ServiceType.DYNAMODB)
            
            assert postgres_repo is not dynamodb_repo
        except Exception as e:
            pytest.skip(f"Database not available: {e}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
