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
from services.store_data.store_data import StoreDataInterface, DynamoDBStoreDataService, PostgresStoreDataService


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
        
        logger.info(f"Saving receipt {entity.receipt_id} to database")
        
        # Check if using PostgreSQL (which has separate tables for items)
        if isinstance(self.store_service, PostgresStoreDataService):
            self._save_postgres(entity)
        else:
            # DynamoDB stores items as embedded documents
            data_to_store = self._to_dict(entity)
            self.store_service.save(table_name=self.table_name, data=data_to_store)
        
        logger.info(f"Successfully saved receipt {entity.receipt_id}")
        
        return entity
    
    def _save_postgres(self, entity: Receipt) -> None:
        """
        Save receipt to PostgreSQL with separate items table.
        
        Args:
            entity: The Receipt to save
        """
        # Save receipt without items
        receipt_data = self._to_dict(entity, include_items=False)
        self.store_service.save(table_name=self.table_name, data=receipt_data)
        
        # Save items separately if any exist
        if entity.items:
            self._save_receipt_items(entity.receipt_id, entity.items)
    
    def _save_receipt_items(self, receipt_id: str, items: List[ReceiptItem]) -> None:
        """
        Save receipt items to the receipt_items table.
        
        Args:
            receipt_id: The receipt ID
            items: List of receipt items
        """
        # First, delete existing items for this receipt (for update case)
        try:
            self.store_service.cursor.execute(
                "DELETE FROM receipt_items WHERE receipt_id = %s",
                (receipt_id,)
            )
        except Exception as e:
            logger.warning(f"Could not delete existing items: {e}")
        
        # Insert new items
        for item in items:
            item_data = {
                'receipt_id': receipt_id,
                'name': item.name,
                'price': float(item.price),
                'quantity': item.quantity,
                'category': item.category
            }
            self.store_service.save(table_name='receipt_items', data=item_data)
    
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
            data = self.store_service.get(self.table_name, {'receipt_id': receipt_id})
            
            if data:
                # If using PostgreSQL, load items separately
                if isinstance(self.store_service, PostgresStoreDataService):
                    items = self._load_receipt_items(receipt_id)
                    data['items'] = items
                
                return self._to_entity(data)
            
            logger.info(f"Receipt {receipt_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error finding receipt {receipt_id}: {str(e)}")
            raise
    
    def _load_receipt_items(self, receipt_id: str) -> List[Dict[str, Any]]:
        """
        Load receipt items from the receipt_items table.
        
        Args:
            receipt_id: The receipt ID
            
        Returns:
            List of item dictionaries
        """
        try:
            self.store_service.cursor.execute(
                "SELECT name, price, quantity, category FROM receipt_items WHERE receipt_id = %s",
                (receipt_id,)
            )
            
            columns = [desc[0] for desc in self.store_service.cursor.description]
            rows = self.store_service.cursor.fetchall()
            
            items = []
            for row in rows:
                item_dict = dict(zip(columns, row))
                items.append(item_dict)
            
            return items
        except Exception as e:
            logger.error(f"Error loading receipt items: {e}")
            return []
    
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
            
            # For PostgreSQL, items will be deleted automatically due to CASCADE
            self.store_service.delete(self.table_name, {'receipt_id': receipt_id})
            
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
        
        # Update fields in the entity
        for key, value in kwargs.items():
            if hasattr(receipt, key):
                setattr(receipt, key, value)
        
        # Update timestamp
        receipt.updated_at = datetime.now()
        kwargs['updated_at'] = receipt.updated_at
        
        logger.info(f"Updating receipt {receipt_id} with fields: {list(kwargs.keys())}")
        
        # Check if using PostgreSQL (which has separate tables for items)
        if isinstance(self.store_service, PostgresStoreDataService):
            # Update receipt without items
            receipt_data_to_update = {}
            for key, value in kwargs.items():
                if key != 'items':  # items are handled separately
                    if key == 'total_amount':
                        receipt_data_to_update[key] = str(value) if value is not None else '0.0'
                    elif key in ['purchase_date', 'created_at', 'updated_at']:
                        if hasattr(value, 'isoformat'):
                            receipt_data_to_update[key] = value.isoformat()
                        else:
                            receipt_data_to_update[key] = value
                    elif key == 'status':
                        # Convert enum to string
                        receipt_data_to_update[key] = value.value if hasattr(value, 'value') else str(value)
                    else:
                        receipt_data_to_update[key] = value
            
            # Update the receipt table
            if receipt_data_to_update:
                self.store_service.update(
                    table_name=self.table_name,
                    key={'receipt_id': receipt_id},
                    data=receipt_data_to_update
                )
            
            # Update items if provided
            if 'items' in kwargs and kwargs['items']:
                self._save_receipt_items(receipt_id, kwargs['items'])
        else:
            # DynamoDB: update with items embedded
            receipt_data = self._to_dict(receipt)
            # Remove receipt_id from data (it's the key)
            receipt_data_to_update = {k: v for k, v in receipt_data.items() if k != 'receipt_id'}
            
            self.store_service.update(
                table_name=self.table_name,
                key={'receipt_id': receipt_id},
                data=receipt_data_to_update
            )
        
        logger.info(f"Successfully updated receipt {receipt_id}")
        return receipt
    
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
        
        # Convert status string to ReceiptStatus enum if needed
        if 'status' in data and isinstance(data['status'], str):
            from entities.receipt import ReceiptStatus
            data['status'] = ReceiptStatus(data['status'])
        
        # Convert items dict to ReceiptItem objects if needed
        if 'items' in data and data['items']:
            if isinstance(data['items'], list) and data['items']:
                if not isinstance(data['items'][0], ReceiptItem):
                    data['items'] = [ReceiptItem(**item) if isinstance(item, dict) else item 
                                    for item in data['items']]
        
        return Receipt(**data)
    
    def _to_dict(self, entity: Receipt, include_items: bool = True) -> Dict[str, Any]:
        """
        Convert Receipt entity to dictionary for database storage.
        
        Args:
            entity: The Receipt entity
            include_items: Whether to include items (False for PostgreSQL receipts table)
            
        Returns:
            Dictionary suitable for database storage
        """
        # Get all model fields, excluding any that shouldn't be stored
        data = entity.model_dump(exclude={'table_name'} if hasattr(entity, 'table_name') else None)
        
        # Convert datetime objects to ISO format strings
        for field in ['purchase_date', 'created_at', 'updated_at']:
            if field in data and data[field]:
                if hasattr(data[field], 'isoformat'):
                    data[field] = data[field].isoformat()
        
        # Convert total_amount to string for DynamoDB compatibility
        if 'total_amount' in data and data['total_amount'] is not None:
            data['total_amount'] = str(data['total_amount'])
        
        # Define allowed fields based on whether items should be included
        if include_items:
            # DynamoDB: include items as embedded documents
            allowed_fields = {
                'receipt_id', 'user_id', 'purchase_date', 'total_amount',
                'items', 'image_url', 'status', 'created_at', 'updated_at'
            }
        else:
            # PostgreSQL: exclude items (they're in a separate table)
            allowed_fields = {
                'receipt_id', 'user_id', 'purchase_date', 'total_amount',
                'image_url', 'status', 'created_at', 'updated_at'
            }
        
        # Filter to only allowed fields
        data = {key: value for key, value in data.items() if key in allowed_fields}
        
        return data
