from abc import ABC, abstractmethod
from typing import List, Set
from datetime import timedelta
from io_comp.models import TimeRange


class IAvailabilityService(ABC):
    """
    Abstract Base Class for finding available meeting time slots.
    
    Benefits:
    - Allows multiple scheduling algorithms to be implemented and swapped
    - Enables A/B testing of different availability strategies
    - Simplifies testing by allowing mock service implementations
    - Supports extension without modifying existing code (Open/Closed Principle)
    """
    
    @abstractmethod
    def find_available_slots(
        self, 
        person_list: List[str], 
        duration: timedelta
    ) -> List[TimeRange]:
        """
        Find all time slots where specified people are available.
        
        Args:
            person_list: List of person names who must all be available
            duration: Minimum duration required for the meeting
            
        Returns:
            List of TimeRange objects representing available slots
        """
        pass
    
    @abstractmethod
    def get_all_people(self) -> Set[str]:
        """
        Get all unique person names from the data source.
        
        Returns:
            Set of person names
        """
        pass
