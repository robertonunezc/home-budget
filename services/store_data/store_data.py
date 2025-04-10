
import boto3
from abc import ABC, abstractmethod
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
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('spends-app-data')

    def save(self, data):
        self.table.put_item(Item=data)  
    
    def get(self, data):
        response = self.table.get_item(Key=data)
        return response.get('Item')
    
    def delete(self, data):
        self.table.delete_item(Key=data)