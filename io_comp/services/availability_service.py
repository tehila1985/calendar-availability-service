from datetime import time, timedelta
from typing import List, Set
from io_comp.models import Event, TimeRange
from io_comp.interfaces import IDataLoader
from .i_availability_service import IAvailabilityService


class AvailabilityService(IAvailabilityService):
    """
    Concrete implementation of IAvailabilityService using Interval Merging algorithm.
    
    This service demonstrates key SOLID principles:
    - Single Responsibility: Only handles availability logic
    - Open/Closed: Open for extension (new algorithms), closed for modification
    - Dependency Inversion: Depends on IDataLoader abstraction, not concrete implementation
    
    Benefits of Dependency Injection:
    - Testability: Can inject mock data loaders for unit tests
    - Flexibility: Can switch between CSV, JSON, database without changing this code
    - Scalability: Easy to add caching, logging, or other cross-cutting concerns
    
    Algorithm Complexity: O(N log N)
    - N is the number of events for the requested participants
    - Dominated by the sorting step
    - Merging and gap-finding are O(N)
    
    Why this is efficient:
    - For typical calendars with 10-50 events per person per day, N log N is negligible
    - Scales well: even with 1000 events, 1000 * log(1000) ≈ 10,000 operations
    - Linear scan after sorting ensures we only pass through the data once
    """

    # Office hours configuration - easily adjustable for different organizations
    OFFICE_START = time(7, 0)
    OFFICE_END = time(19, 0)

    def __init__(self, data_loader: IDataLoader):
        """
        Initialize the service with a data loader (Dependency Injection).
        
        This constructor accepts the INTERFACE (IDataLoader), not a concrete class.
        This is the Dependency Inversion Principle in action:
        - The service depends on an abstraction (IDataLoader)
        - It doesn't care if it's CSV, JSON, or database
        - Makes the code testable and flexible
        
        Args:
            data_loader: Implementation of IDataLoader interface to fetch events
        """
        self.data_loader: IDataLoader = data_loader
        self._events_cache: List[Event] = None
        self._source: str = None

    def find_available_slots(
        self, 
        person_list: List[str], 
        duration: timedelta
    ) -> List[TimeRange]:
        """
        Find all time slots where specified people are available to meet.
        
        Args:
            person_list: List of person names who must all be available
            duration: Minimum duration required for the meeting
            
        Returns:
            List of TimeRange objects representing available slots
            
        Raises:
            ValueError: If person_list is empty or duration is invalid
        """
        if not person_list:
            raise ValueError("Person list cannot be empty")
        
        if duration.total_seconds() <= 0:
            raise ValueError("Event duration must be positive")

        # Load events once and cache
        if self._events_cache is None:
            self._source = self.data_loader._get_default_source()
            self._events_cache = self.data_loader.load_events(self._source)

        # Step 1: Extract busy time ranges for requested participants
        busy_ranges = self._get_busy_ranges(person_list)

        # Step 2: Merge overlapping/adjacent busy ranges
        merged_ranges = self._merge_overlapping_ranges(busy_ranges)

        # Step 3: Find gaps that fit the requested duration
        available_slots = self._find_gaps(merged_ranges, duration)

        return available_slots

    def _get_busy_ranges(self, person_list: List[str]) -> List[TimeRange]:
        """
        Extract all busy time ranges for the specified people.
        
        This filters events to only those belonging to requested participants
        and converts them to TimeRange objects for easier manipulation.
        
        Args:
            person_list: List of person names to filter by
            
        Returns:
            List of TimeRange objects, sorted by start time
        """
        person_set: Set[str] = set(person_list)  # O(1) lookup
        busy_ranges: List[TimeRange] = []

        for event in self._events_cache:
            if event.person in person_set:
                busy_ranges.append(TimeRange(event.start_time, event.end_time))

        # Sort by start time - O(N log N) complexity
        # This is the bottleneck of the algorithm but necessary for merging
        busy_ranges.sort(key=lambda r: r.start)

        return busy_ranges

    def _merge_overlapping_ranges(self, ranges: List[TimeRange]) -> List[TimeRange]:
        """
        Merge overlapping or adjacent time ranges into consolidated blocks.
        
        Algorithm:
        1. Start with the first range as the current merged range
        2. For each subsequent range:
           - If it overlaps or is adjacent to current: extend current
           - Otherwise: save current and start a new merged range
        
        This is the key optimization that reduces complexity from O(N²) to O(N).
        
        Example:
            Input:  [08:00-09:30, 09:00-09:40, 13:00-14:00]
            Output: [08:00-09:40, 13:00-14:00]
        
        Args:
            ranges: Sorted list of TimeRange objects
            
        Returns:
            List of merged TimeRange objects with no overlaps
        """
        if not ranges:
            return []

        merged: List[TimeRange] = [ranges[0]]

        for current_range in ranges[1:]:
            last_merged = merged[-1]

            # Check if current range overlaps or is adjacent to the last merged range
            if current_range.start <= last_merged.end:
                # Merge by extending the end time to the maximum
                merged[-1] = TimeRange(
                    start=last_merged.start,
                    end=max(last_merged.end, current_range.end)
                )
            else:
                # No overlap - add as a new separate busy block
                merged.append(current_range)

        return merged

    def _find_gaps(
        self, 
        busy_ranges: List[TimeRange], 
        min_duration: timedelta
    ) -> List[TimeRange]:
        """
        Find all gaps between busy ranges that fit the minimum duration.
        
        Checks three types of gaps:
        1. Before first event (07:00 to first event start)
        2. Between consecutive events
        3. After last event (last event end to 19:00)
        
        Args:
            busy_ranges: Merged list of busy time ranges
            min_duration: Minimum duration required for a valid slot
            
        Returns:
            List of TimeRange objects representing available slots
        """
        available_slots: List[TimeRange] = []
        duration_minutes: int = int(min_duration.total_seconds() / 60)

        # Case 1: No busy ranges - entire office hours available
        if not busy_ranges:
            office_range = TimeRange(self.OFFICE_START, self.OFFICE_END)
            if office_range.duration_minutes() >= duration_minutes:
                available_slots.append(office_range)
            return available_slots

        # Case 2: Gap before first event
        if self.OFFICE_START < busy_ranges[0].start:
            first_gap = TimeRange(self.OFFICE_START, busy_ranges[0].start)
            if first_gap.duration_minutes() >= duration_minutes:
                available_slots.append(first_gap)

        # Case 3: Gaps between consecutive events
        for i in range(len(busy_ranges) - 1):
            if busy_ranges[i].end < busy_ranges[i + 1].start:
                gap = TimeRange(busy_ranges[i].end, busy_ranges[i + 1].start)
                if gap.duration_minutes() >= duration_minutes:
                    available_slots.append(gap)

        # Case 4: Gap after last event
        if busy_ranges[-1].end < self.OFFICE_END:
            last_gap = TimeRange(busy_ranges[-1].end, self.OFFICE_END)
            if last_gap.duration_minutes() >= duration_minutes:
                available_slots.append(last_gap)

        return available_slots

    def get_all_people(self) -> Set[str]:
        """
        Get all unique person names from the data source.
        
        Returns:
            Set of person names
        """
        return self.data_loader.get_all_people()
