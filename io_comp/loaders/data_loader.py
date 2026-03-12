from io_comp.interfaces import IDataLoader
from typing import List
from io_comp.models import Event


class DataLoader(IDataLoader):
    """
    Base implementation of IDataLoader interface.
    
    This class inherits from the abstract interface and provides
    common functionality for all data loader implementations.
    """
    
    def load_events(self, source: str) -> List[Event]:
        """Must be implemented by concrete subclasses."""
        raise NotImplementedError("Subclasses must implement load_events")
    
    def _get_default_source(self) -> str:
        """Must be implemented by concrete subclasses."""
        raise NotImplementedError("Subclasses must implement _get_default_source")
