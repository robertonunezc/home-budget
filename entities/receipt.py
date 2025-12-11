# Receipt entity to store the receipt information
# This is a pure business logic entity with no database dependencies
import uuid
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class ReceiptItem(BaseModel):
    """
    Represents a single item in a receipt.
    """
    name: str
    price: float
    quantity: Optional[int] = 1
    category: Optional[str] = 'other'
    

class Receipt(BaseModel):
    """
    Receipt entity representing a purchase receipt with items.
    Contains only business logic - no database operations.
    """
    receipt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    purchase_date: datetime = Field(default_factory=datetime.now)
    total_amount: Decimal = Decimal(0.0)
    items: List[ReceiptItem] = Field(default_factory=list)
    image_url: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Business logic methods
    
    def add_item(self, item: ReceiptItem) -> None:
        """
        Add an item to the receipt and update the total.
        
        Args:
            item: The receipt item to add
        """
        self.items.append(item)
        self.calculate_total()
    
    def remove_item(self, item_name: str) -> bool:
        """
        Remove an item from the receipt by name.
        
        Args:
            item_name: The name of the item to remove
            
        Returns:
            True if item was removed, False if not found
        """
        initial_length = len(self.items)
        self.items = [item for item in self.items if item.name != item_name]
        
        if len(self.items) < initial_length:
            self.calculate_total()
            return True
        return False
    
    def calculate_total(self) -> Decimal:
        """
        Calculate and update the total amount from all items.
        
        Returns:
            The calculated total
        """
        total = Decimal(0)
        for item in self.items:
            total += Decimal(str(item.price)) * item.quantity
        
        self.total_amount = total
        return total
    
    def update_fields(self, **kwargs) -> None:
        """
        Update receipt fields.
        
        Args:
            **kwargs: Fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Always update the timestamp when fields change
        self.updated_at = datetime.now()
    
    def is_valid(self) -> bool:
        """
        Validate that the receipt has all required fields.
        
        Returns:
            True if valid, False otherwise
        """
        return bool(self.receipt_id and self.user_id and self.image_url)
    
    def get_items_by_category(self, category: str) -> List[ReceiptItem]:
        """
        Get all items in a specific category.
        
        Args:
            category: The category to filter by
            
        Returns:
            List of items in the category
        """
        return [item for item in self.items if item.category == category]
    
    def get_summary(self) -> dict:
        """
        Get a summary of the receipt.
        
        Returns:
            Dictionary with receipt summary information
        """
        return {
            'receipt_id': self.receipt_id,
            'user_id': self.user_id,
            'purchase_date': self.purchase_date,
            'total_amount': float(self.total_amount),
            'item_count': len(self.items),
            'categories': list(set(item.category for item in self.items))
        }