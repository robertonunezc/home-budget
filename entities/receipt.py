# Receipt entity to store the receipt information
import uuid
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from services.store_data.store_data import StoreDataServiceFactory
class ReceiptItem(BaseModel):
    name: str
    price: float
    quantity: Optional[int] = 1
    category: Optional[str] = 'other'

class Receipt(BaseModel):
    table_name: str = 'receipts'
    receipt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    purchase_date: datetime = Field(default_factory=datetime.now)
    total_amount: Decimal = Decimal(0.0)
    items: List[ReceiptItem] = Field(default_factory=list)
    image_url: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def to_dict(self):
        data = self.model_dump()
        # Convert datetime objects to ISO format strings
        for field in ['purchase_date', 'created_at', 'updated_at']:
            if field in data and data[field]:
                # Only convert if it's a datetime object, not if it's already a string
                if hasattr(data[field], 'isoformat'):
                    data[field] = data[field].isoformat()
        return data
    
    @staticmethod
    def from_dict(data: dict):
        # Convert ISO format strings back to datetime objects
        for field in ['purchase_date', 'created_at', 'updated_at']:
            if field in data and data[field]:
                # Only convert if it's a string, not if it's already a datetime object
                if isinstance(data[field], str):
                    try:
                        data[field] = datetime.fromisoformat(data[field])
                    except ValueError:
                        # If fromisoformat fails, try parsing with a different format
                        # This handles cases where the string might have a different format
                        pass
        return Receipt(**data)
    
    def save(self):
         # Validate required fields
        if not self.receipt_id:
            raise ValueError("Receipt ID is required")
        if not self.user_id:
            raise ValueError("User ID is required")
        if not self.image_url:
            raise ValueError("Image URL is required")
        
        # Prepare data for storage
        data_to_store = self.to_dict()
        
        # Convert total_amount to string for DynamoDB
        if 'total_amount' in data_to_store and data_to_store['total_amount'] is not None:
            data_to_store['total_amount'] = str(data_to_store['total_amount'])
        store_data_service = StoreDataServiceFactory.create()
        store_data_service.save(table_name=self.table_name, data=data_to_store)
        return self
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Update timestamps
        self.updated_at = datetime.now()
        
        # Save the updated receipt
        return self.save()