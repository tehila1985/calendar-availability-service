from datetime import timedelta
from typing import List
from io_comp.models import TimeRange
from io_comp.interfaces import IDataLoader
from io_comp.services import IAvailabilityService
from io_comp.loaders import CSVDataLoader
from io_comp.services import AvailabilityService


def find_available_slots(
    person_list: List[str], 
    event_duration: timedelta,
    csv_file_path: str = 'resources/calendar.csv'
) -> List[TimeRange]:
    """
    Public API: Find available meeting slots for specified people.
    
    This function demonstrates Dependency Injection by wiring together:
    - Concrete data loader (CSVDataLoader)
    - Concrete service (AvailabilityService)
    - Both depend on abstractions (IDataLoader, IAvailabilityService)
    
    Args:
        person_list: List of person names who must all be available
        event_duration: Required meeting duration
        csv_file_path: Path to calendar CSV file (default: resources/calendar.csv)
        
    Returns:
        List of TimeRange objects representing available slots
    """
    # Dependency Injection: Create concrete loader and inject into service
    loader: IDataLoader = CSVDataLoader(csv_file_path)
    service: IAvailabilityService = AvailabilityService(loader)
    return service.find_available_slots(person_list, event_duration)


def main() -> None:
    """
    Main entry point demonstrating how to wire everything together.
    
    This is the Composition Root - where we:
    1. Create concrete implementations (CSVDataLoader)
    2. Inject dependencies (loader into service)
    3. Use only interfaces in the rest of the code
    
    Benefits:
    - Easy to swap CSVDataLoader with JSONDataLoader or DatabaseLoader
    - Easy to test by injecting mock implementations
    - Clear separation of concerns
    """
    csv_path: str = 'resources/calendar.csv'
    
    # Step 1: Create concrete data loader
    # This is the only place where we mention the concrete class
    loader: IDataLoader = CSVDataLoader(csv_path)
    
    # Step 2: Inject the loader into the service (Dependency Injection)
    # The service only knows about IDataLoader interface, not CSVDataLoader
    service: IAvailabilityService = AvailabilityService(loader)
    
    # Step 3: Use the service through its interface
    all_people: List[str] = sorted(service.get_all_people())
    duration: timedelta = timedelta(hours=1)
    
    print(f"\nPeople in calendar: {', '.join(all_people)}")
    print(f"Meeting duration: {duration}")
    
    # Find available slots for all people
    slots: List[TimeRange] = service.find_available_slots(all_people, duration)
    
    print(f"\nAvailable slots for all people:")
    if slots:
        for slot in slots:
            print(f"Starting Time of available slots: {slot}")
    else:
        print("No available slots found")


if __name__ == "__main__":
    main()
