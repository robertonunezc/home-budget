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
                data[field] = data[field].isoformat()
        return data
    
    @staticmethod
    def from_dict(data: dict):
        # Convert ISO format strings back to datetime objects
        for field in ['purchase_date', 'created_at', 'updated_at']:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        return Receipt(**data)
    
    def save(self):
         # Validate required fields
        if not self.receipt_id:
            raise ValueError("Receipt ID is required")
        if not self.user_id:
            raise ValueError("User ID is required")
        if not self.image_url:
            raise ValueError("Image URL is required")
        
        # Ensure all datetime fields are strings
        for field in ['purchase_date', 'created_at', 'updated_at']:
            if field in self and not isinstance(self[field], str):
                self[field] = self[field].isoformat()
        
        # Ensure total_amount is a string (DynamoDB requirement for Decimal)
        if self.total_amount:
            self.total_amount = str(self.total_amount)
        
        store_data_service = StoreDataServiceFactory.create()
        store_data_service.save(table_name=self.table_name, data=self.to_dict())
        return self