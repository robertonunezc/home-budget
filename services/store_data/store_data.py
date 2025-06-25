import boto3
from abc import ABC, abstractmethod
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
class StoreDataInterface(ABC):
    @abstractmethod
    def save(self, table_name: str, data: dict):
        pass

    @abstractmethod
    def get(self, data):
        pass

    @abstractmethod
    def delete(self, data):
        pass
    

class StoreDataServiceFactory:
    _instance = None
    
    @staticmethod
    def create()->StoreDataInterface:
        if StoreDataServiceFactory._instance is None:
            StoreDataServiceFactory._instance = DynamoDBStoreDataService()
        return StoreDataServiceFactory._instance
    

class DynamoDBStoreDataService(StoreDataInterface):
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DynamoDBStoreDataService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if DynamoDBStoreDataService._initialized:
            return
            
        try:
            self.dynamodb = boto3.resource('dynamodb',
                                           aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                           aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                                           region_name=os.getenv('AWS_REGION'))
            DynamoDBStoreDataService._initialized = True
            logger.info("DynamoDB connection initialized (singleton)")
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB connection: {str(e)}")
            raise

    def save(self, table_name:str, data:dict):
        try:
            self.table = self.dynamodb.Table(table_name)
            item_data = data
            logger.info(f"Attempting to save data to DynamoDB: {item_data}")
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