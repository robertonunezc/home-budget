"""
Base repository interface and abstract class for data access layer.
This module defines the contract for repository implementations.
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Dict, Any

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """
    Interface for repository pattern. All repositories must implement these methods.
    """
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """
        Save or update an entity in the database.
        
        Args:
            entity: The entity to save
            
        Returns:
            The saved entity
        """
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """
        Find an entity by its ID.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_all(self, filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[T]:
        """
        Find all entities matching the given filters.
        
        Args:
            filters: Optional dictionary of field-value pairs to filter by
            limit: Optional maximum number of results to return
            
        Returns:
            List of entities matching the filters
        """
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """
        Delete an entity by its ID.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def exists(self, entity_id: str) -> bool:
        """
        Check if an entity exists by its ID.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            True if exists, False otherwise
        """
        pass


class BaseRepository(IRepository[T], ABC):
    """
    Abstract base repository with common functionality.
    Concrete repositories should extend this class.
    """
    
    def __init__(self, table_name: str):
        """
        Initialize the repository.
        
        Args:
            table_name: The name of the database table
        """
        self.table_name = table_name
    
    @abstractmethod
    def _to_entity(self, data: Dict[str, Any]) -> T:
        """
        Convert database data to entity object.
        
        Args:
            data: Dictionary from database
            
        Returns:
            Entity object
        """
        pass
    
    @abstractmethod
    def _to_dict(self, entity: T) -> Dict[str, Any]:
        """
        Convert entity object to dictionary for database storage.
        
        Args:
            entity: The entity object
            
        Returns:
            Dictionary suitable for database storage
        """
        pass
