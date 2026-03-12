from abc import ABC, abstractmethod
from typing import List, Set
from datetime import timedelta
from io_comp.models import Event


class IDataLoader(ABC):
    """
    Abstract Base Class for loading calendar events from any data source.
    
    Benefits:
    - Decouples business logic from data source implementation
    - Enables easy switching between CSV, JSON, database, or API sources
    - Facilitates unit testing with mock implementations
    - Follows Dependency Inversion Principle (depend on abstractions, not concretions)
    """
    
    @abstractmethod
    def load_events(self, source: str) -> List[Event]:
        """
        Load all events from the specified data source.
        
        Args:
            source: Path or identifier for the data source (file path, URL, etc.)
            
        Returns:
            List of Event objects
        """
        pass
    
    def get_all_people(self) -> Set[str]:
        """
        Get all unique person names from loaded events.
        
        Returns:
            Set of person names
        """
        events = self.load_events(self._get_default_source())
        return {event.person for event in events}
    
    @abstractmethod
    def _get_default_source(self) -> str:
        """Return the default source path/identifier for this loader."""
        pass
