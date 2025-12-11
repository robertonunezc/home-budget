import boto3
from abc import ABC, abstractmethod
import logging
import os
from enum import Enum
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
    
class ServiceType(Enum):
    DYNAMODB = 'dynamodb'
    POSTGRES = 'postgres'
class StoreDataServiceFactory:
    _instances = {}
    
    @staticmethod
    def create(service_type: ServiceType = ServiceType.DYNAMODB) -> StoreDataInterface:
        service_type_value = service_type.value.lower()
        
        if service_type_value not in StoreDataServiceFactory._instances:
            if service_type_value == ServiceType.DYNAMODB.value:
                StoreDataServiceFactory._instances[service_type_value] = DynamoDBStoreDataService()
            elif service_type_value == ServiceType.POSTGRES.value:
                StoreDataServiceFactory._instances[service_type_value] = PostgresStoreDataService()
            else:
                raise ValueError(f"Unknown service type: {service_type_value}. Use ServiceType.DYNAMODB or ServiceType.POSTGRES.")
        
        return StoreDataServiceFactory._instances[service_type_value]
    

class PostgresStoreDataService(StoreDataInterface):
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgresStoreDataService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if PostgresStoreDataService._initialized:
            return
            
        try:
            import psycopg2

            self.connection = psycopg2.connect(
                dbname=os.getenv('POSTGRES_DB'),
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD'),
                host=os.getenv('POSTGRES_HOST'),
                port=os.getenv('POSTGRES_PORT')
            )
            self.cursor = self.connection.cursor()
            PostgresStoreDataService._initialized = True
            logger.info("PostgreSQL connection initialized (singleton)")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection: {str(e)}")
            raise

    def save(self, table_name: str, data: dict):
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            values = tuple(data.values())
            
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            logger.info(f"Attempting to save data to PostgreSQL: {data}")
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
            logger.info(f"Successfully saved data to PostgreSQL")
            return data
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to save data to PostgreSQL: {str(e)}")
            raise
    
    def get(self, data: dict):
        try:
            # Assuming data is a dict with column-value pairs for WHERE clause
            conditions = ' AND '.join([f"{key} = %s" for key in data.keys()])
            values = tuple(data.values())
            
            query = f"SELECT * FROM table_name WHERE {conditions}"
            self.cursor.execute(query, values)
            
            columns = [desc[0] for desc in self.cursor.description]
            row = self.cursor.fetchone()
            
            if row:
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve data from PostgreSQL: {str(e)}")
            raise
    
    def delete(self, data: dict):
        try:
            conditions = ' AND '.join([f"{key} = %s" for key in data.keys()])
            values = tuple(data.values())
            
            query = f"DELETE FROM table_name WHERE {conditions}"
            logger.info(f"Attempting to delete data from PostgreSQL: {data}")
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
            logger.info(f"Successfully deleted data from PostgreSQL")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to delete data from PostgreSQL: {str(e)}")
            raise
        pass
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