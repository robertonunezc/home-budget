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