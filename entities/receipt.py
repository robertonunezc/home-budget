# Receipt entity to store the receipt information
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ReceiptItem(BaseModel):
    name: str
    price: float
    quantity: Optional[int] = 1

class Receipt(BaseModel):
    id: str
    user_id: str
    date: datetime
    total_amount: float
    items: List[ReceiptItem]
    image_url: str
    created_at: datetime
    updated_at: datetime