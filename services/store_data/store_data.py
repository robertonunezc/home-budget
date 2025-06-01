import boto3
from abc import ABC, abstractmethod
from entities.receipt import Receipt
import logging
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
class StoreDataInterface(ABC):
    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def get(self, data):
        pass

    @abstractmethod
    def delete(self, data):
        pass
    

class StoreDataServiceFactory:
    @staticmethod
    def create()->StoreDataInterface:
        return DynamoDBStoreDataService()
    

class DynamoDBStoreDataService(StoreDataInterface):
    def __init__(self):
        try:
            self.dynamodb = boto3.resource('dynamodb',
                                           aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                           aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                                           region_name=os.getenv('AWS_REGION'))
            
            table_name = os.getenv('DYNAMODB_TABLE_NAME', 'receipts')
            logger.info(f"Attempting to connect to DynamoDB table: {table_name}")
            self.table = self.dynamodb.Table(table_name)
            # Verify table exists by describing it
            self.table.table_status
            logger.info(f"Successfully connected to DynamoDB table: {table_name}")
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB connection: {str(e)}")
            raise

    def save(self, data:Receipt):
        try:
            item_data = data.to_dict()
            logger.info(f"Attempting to save data to DynamoDB: {item_data}")
            
            # Validate required fields
            if not item_data.get('receipt_id'):
                raise ValueError("Receipt ID is required")
            if not item_data.get('user_id'):
                raise ValueError("User ID is required")
            if not item_data.get('image_url'):
                raise ValueError("Image URL is required")
            
            # Ensure all datetime fields are strings
            for field in ['purchase_date', 'created_at', 'updated_at']:
                if field in item_data and not isinstance(item_data[field], str):
                    item_data[field] = item_data[field].isoformat()
            
            # Ensure total_amount is a string (DynamoDB requirement for Decimal)
            if 'total_amount' in item_data:
                item_data['total_amount'] = str(item_data['total_amount'])
            logger.info(f"Inserting into table: {self.table.name} in region {self.dynamodb.meta.client.meta.region_name}")
           
            logger.info(f"Processed data for DynamoDB: {item_data}")
            self.table.put_item(Item=item_data)  
            logger.info(f"Successfully saved data to DynamoDB")
            return data
        except Exception as e:
            logger.error(f"Failed to save data to DynamoDB: {str(e)}")
            raise
    
    def get(self, data):
        response = self.table.get_item(Key=data)
        return response.get('Item')
    
    def delete(self, data):
        self.table.delete_item(Key=data)