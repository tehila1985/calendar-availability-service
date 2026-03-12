import csv
from datetime import time
from typing import List
from io_comp.models import Event
from .data_loader import DataLoader


class CSVDataLoader(DataLoader):
    """
    Concrete implementation of IDataLoader for CSV files.
    
    This class demonstrates the Dependency Inversion Principle:
    - High-level modules (AvailabilityService) depend on abstractions (IDataLoader)
    - Low-level modules (CSVDataLoader) also depend on the same abstractions
    - This allows easy replacement with JSONDataLoader, DatabaseLoader, etc.
    
    Expected CSV format: Person, Subject, StartTime, EndTime
    Example: Alice,"Morning meeting",08:00,09:30
    """

    def __init__(self, file_path: str):
        """
        Initialize the CSV loader with a file path.
        
        Args:
            file_path: Path to the CSV file containing calendar events
        """
        self.file_path = file_path

    def load_events(self, source: str) -> List[Event]:
        """
        Load events from CSV file.
        
        Args:
            source: Path to the CSV file (overrides default if provided)
        
        Returns:
            List of Event objects parsed from the CSV
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the CSV format is invalid
        """
        file_to_load = source if source else self.file_path
        events = []
        
        try:
            with open(file_to_load, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row_num, row in enumerate(reader, start=1):
                    try:
                        if len(row) != 4:
                            raise ValueError(f"Row {row_num}: Expected 4 columns, got {len(row)}")
                        
                        person = row[0].strip()
                        subject = row[1].strip().strip('"')
                        start_time = self._parse_time(row[2].strip())
                        end_time = self._parse_time(row[3].strip())
                        
                        events.append(Event(person, subject, start_time, end_time))
                    except Exception as e:
                        raise ValueError(f"Error parsing row {row_num}: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Calendar file not found: {file_to_load}")
        
        return events
    
    def _get_default_source(self) -> str:
        """
        Return the default CSV file path.
        
        Returns:
            Default file path for this loader
        """
        return self.file_path

    @staticmethod
    def _parse_time(time_str: str) -> time:
        """
        Parse time string in HH:MM format.
        
        Args:
            time_str: Time string like "08:00" or "14:30"
            
        Returns:
            datetime.time object
            
        Raises:
            ValueError: If time format is invalid
        """
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                raise ValueError(f"Invalid time format: {time_str}")
            
            hour, minute = int(parts[0]), int(parts[1])
            return time(hour, minute)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid time format '{time_str}': {e}")
