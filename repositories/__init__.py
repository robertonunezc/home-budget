# Repositories module
"""
Repository pattern implementation for data access layer.

This module provides a clean separation between business logic (entities)
and data access (repositories). 

Usage:
    from repositories.repository_factory import RepositoryFactory
    from services.store_data.store_data import ServiceType
    
    # Create a receipt repository with PostgreSQL
    repo = RepositoryFactory.create_receipt_repository(ServiceType.POSTGRES)
    
    # Save a receipt
    receipt = Receipt(user_id="user123", image_url="https://...")
    repo.save(receipt)
    
    # Find by ID
    receipt = repo.find_by_id("receipt_id")
    
    # Update
    repo.update("receipt_id", total_amount=100.50)
"""

from repositories.base_repository import IRepository, BaseRepository
from repositories.receipt_repository import ReceiptRepository
from repositories.repository_factory import RepositoryFactory, RepositoryType

__all__ = [
    'IRepository',
    'BaseRepository',
    'ReceiptRepository',
    'RepositoryFactory',
    'RepositoryType',
]

