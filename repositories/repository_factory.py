"""
Repository factory for creating repository instances.
Provides a centralized way to create repositories with the correct storage backend.
"""
from enum import Enum
from typing import Dict, Type

from repositories.base_repository import IRepository
from repositories.receipt_repository import ReceiptRepository
from services.store_data.store_data import StoreDataServiceFactory, ServiceType


class RepositoryType(Enum):
    """Enum for repository types"""
    RECEIPT = 'receipt'


class RepositoryFactory:
    """
    Factory for creating repository instances.
    Uses singleton pattern to cache repository instances.
    """
    
    _instances: Dict[str, IRepository] = {}
    
    @staticmethod
    def create_receipt_repository(service_type: ServiceType = ServiceType.DYNAMODB) -> ReceiptRepository:
        """
        Create a ReceiptRepository instance.
        
        Args:
            service_type: The storage service type (DYNAMODB or POSTGRES)
            
        Returns:
            ReceiptRepository instance
        """
        cache_key = f"receipt_{service_type.value}"
        
        if cache_key not in RepositoryFactory._instances:
            # Get the appropriate storage service
            store_service = StoreDataServiceFactory.create(service_type)
            
            # Create the repository
            repository = ReceiptRepository(store_service)
            
            # Cache it
            RepositoryFactory._instances[cache_key] = repository
        
        return RepositoryFactory._instances[cache_key]
    
    @staticmethod
    def clear_cache():
        """Clear the repository cache. Useful for testing."""
        RepositoryFactory._instances.clear()
