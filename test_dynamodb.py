import boto3
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dynamodb_connection():
    try:
        # Load environment variables
        load_dotenv()
        
        # Get AWS credentials from environment
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION')
        table_name = os.getenv('DYNAMODB_TABLE_NAME', 'receipts')
        
        logger.info(f"Testing DynamoDB connection with:")
        logger.info(f"Region: {aws_region}")
        logger.info(f"Table: {table_name}")
        
        # Initialize DynamoDB client
        dynamodb = boto3.resource('dynamodb',
                                 aws_access_key_id=aws_access_key,
                                 aws_secret_access_key=aws_secret_key,
                                 region_name=aws_region)
        
        # Try to get table description
        table = dynamodb.Table(table_name)
        response = table.meta.client.describe_table(TableName=table_name)
        
        logger.info("Successfully connected to DynamoDB!")
        logger.info(f"Table status: {response['Table']['TableStatus']}")
        logger.info(f"Table ARN: {response['Table']['TableArn']}")
        
    except Exception as e:
        logger.error(f"Error connecting to DynamoDB: {str(e)}")
        raise

if __name__ == "__main__":
    test_dynamodb_connection() 