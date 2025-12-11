"""
Receipt repository implementation with support for DynamoDB and PostgreSQL.
Handles all database operations for Receipt entities.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from repositories.base_repository import BaseRepository
from entities.receipt import Receipt, ReceiptItem
from services.store_data.store_data import StoreDataInterface


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ReceiptRepository(BaseRepository[Receipt]):
    """
    Repository for Receipt entities. Handles all database interactions
    while keeping business logic in the Receipt entity.
    """
    
    def __init__(self, store_service: StoreDataInterface, table_name: str = 'receipts'):
        """
        Initialize the receipt repository.
        
        Args:
            store_service: The data store service (DynamoDB or PostgreSQL)
            table_name: The name of the table (default: 'receipts')
        """
        super().__init__(table_name)
        self.store_service = store_service
    
    def save(self, entity: Receipt) -> Receipt:
        """
        Save or update a receipt in the database.
        
        Args:
            entity: The Receipt to save
            
        Returns:
            The saved Receipt
            
        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        if not entity.receipt_id:
            raise ValueError("Receipt ID is required")
        if not entity.user_id:
            raise ValueError("User ID is required")
        if not entity.image_url:
            raise ValueError("Image URL is required")
        
        # Convert entity to dictionary for storage
        data_to_store = self._to_dict(entity)
        
        logger.info(f"Saving receipt {entity.receipt_id} to database")
        
        # Save to database
        self.store_service.save(table_name=self.table_name, data=data_to_store)
        
        logger.info(f"Successfully saved receipt {entity.receipt_id}")
        
        return entity
    
    def find_by_id(self, receipt_id: str) -> Optional[Receipt]:
        """
        Find a receipt by its ID.
        
        Args:
            receipt_id: The receipt ID
            
        Returns:
            The Receipt if found, None otherwise
        """
        try:
            logger.info(f"Finding receipt by ID: {receipt_id}")
            data = self.store_service.get({'receipt_id': receipt_id})
            
            if data:
                return self._to_entity(data)
            
            logger.info(f"Receipt {receipt_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error finding receipt {receipt_id}: {str(e)}")
            raise
    
    def find_by_user_id(self, user_id: str, limit: Optional[int] = None) -> List[Receipt]:
        """
        Find all receipts for a specific user.
        
        Args:
            user_id: The user ID
            limit: Optional maximum number of results
            
        Returns:
            List of receipts for the user
        """
        return self.find_all(filters={'user_id': user_id}, limit=limit)
    
    def find_all(self, filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[Receipt]:
        """
        Find all receipts matching the given filters.
        
        Args:
            filters: Optional dictionary of field-value pairs to filter by
            limit: Optional maximum number of results to return
            
        Returns:
            List of receipts matching the filters
        """
        try:
            logger.info(f"Finding receipts with filters: {filters}, limit: {limit}")
            
            # Note: This is a simplified implementation
            # In a production environment, you'd implement proper querying
            # with pagination support for both DynamoDB and PostgreSQL
            
            # For now, return empty list as full scan would need more implementation
            logger.warning("find_all requires custom implementation per store type")
            return []
        except Exception as e:
            logger.error(f"Error finding receipts: {str(e)}")
            raise
    
    def delete(self, receipt_id: str) -> bool:
        """
        Delete a receipt by its ID.
        
        Args:
            receipt_id: The receipt ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            logger.info(f"Deleting receipt {receipt_id}")
            self.store_service.delete({'receipt_id': receipt_id})
            logger.info(f"Successfully deleted receipt {receipt_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting receipt {receipt_id}: {str(e)}")
            raise
    
    def exists(self, receipt_id: str) -> bool:
        """
        Check if a receipt exists by its ID.
        
        Args:
            receipt_id: The receipt ID
            
        Returns:
            True if exists, False otherwise
        """
        receipt = self.find_by_id(receipt_id)
        return receipt is not None
    
    def update(self, receipt_id: str, **kwargs) -> Optional[Receipt]:
        """
        Update a receipt with the given fields.
        
        Args:
            receipt_id: The receipt ID
            **kwargs: Fields to update
            
        Returns:
            The updated Receipt if found, None otherwise
        """
        receipt = self.find_by_id(receipt_id)
        
        if not receipt:
            logger.warning(f"Cannot update: Receipt {receipt_id} not found")
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(receipt, key):
                setattr(receipt, key, value)
        
        # Update timestamp
        receipt.updated_at = datetime.now()
        
        # Save and return
        return self.save(receipt)
    
    def _to_entity(self, data: Dict[str, Any]) -> Receipt:
        """
        Convert database data to Receipt entity.
        
        Args:
            data: Dictionary from database
            
        Returns:
            Receipt entity
        """
        # Convert ISO format strings back to datetime objects
        for field in ['purchase_date', 'created_at', 'updated_at']:
            if field in data and data[field] and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except (ValueError, AttributeError):
                    pass
        
        # Convert total_amount string back to Decimal if needed
        if 'total_amount' in data and isinstance(data['total_amount'], str):
            data['total_amount'] = Decimal(data['total_amount'])
        
        # Convert items dict to ReceiptItem objects if needed
        if 'items' in data and data['items']:
            if isinstance(data['items'], list) and data['items']:
                if not isinstance(data['items'][0], ReceiptItem):
                    data['items'] = [ReceiptItem(**item) if isinstance(item, dict) else item 
                                    for item in data['items']]
        
        return Receipt(**data)
    
    def _to_dict(self, entity: Receipt) -> Dict[str, Any]:
        """
        Convert Receipt entity to dictionary for database storage.
        
        Args:
            entity: The Receipt entity
            
        Returns:
            Dictionary suitable for database storage
        """
        data = entity.model_dump()
        
        # Convert datetime objects to ISO format strings
        for field in ['purchase_date', 'created_at', 'updated_at']:
            if field in data and data[field]:
                if hasattr(data[field], 'isoformat'):
                    data[field] = data[field].isoformat()
        
        # Convert total_amount to string for DynamoDB compatibility
        if 'total_amount' in data and data['total_amount'] is not None:
            data['total_amount'] = str(data['total_amount'])
        
        # Remove table_name from data if present (it's a class attribute, not data)
        data.pop('table_name', None)
        
        return data
