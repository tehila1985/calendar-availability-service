import unittest
from datetime import time, timedelta
from io_comp.models import Event, TimeRange
from io_comp.services import AvailabilityService
from io_comp.loaders import DataLoader
from typing import List, Set


class MockDataLoader(DataLoader):
    """Mock data loader for testing without file I/O."""
    
    def __init__(self, events: List[Event]):
        self.events = events
    
    def load_events(self) -> List[Event]:
        return self.events
    
    def get_all_people(self) -> Set[str]:
        return {event.person for event in self.events}


class TestAvailabilityService(unittest.TestCase):
    """Comprehensive test suite for AvailabilityService."""

    def test_overlapping_events_from_multiple_users(self):
        """
        Test that overlapping events from different users are properly merged.
        
        Scenario:
        - Alice: 09:00-11:00
        - Bob: 10:00-12:00
        - Alice: 10:30-11:30 (overlaps with her own event)
        
        Expected: Merged busy block 09:00-12:00, with gaps before and after
        """
        events = [
            Event('Alice', 'Meeting 1', time(9, 0), time(11, 0)),
            Event('Bob', 'Meeting 2', time(10, 0), time(12, 0)),
            Event('Alice', 'Meeting 3', time(10, 30), time(11, 30)),
        ]
        
        loader = MockDataLoader(events)
        service = AvailabilityService(loader)
        
        slots = service.find_available_slots(['Alice', 'Bob'], timedelta(hours=1))
        
        # Should have gap at start (07:00-09:00) and end (12:00-19:00)
        self.assertEqual(len(slots), 2)
        self.assertEqual(slots[0].start, time(7, 0))
        self.assertEqual(slots[0].end, time(9, 0))
        self.assertEqual(slots[1].start, time(12, 0))
        self.assertEqual(slots[1].end, time(19, 0))

    def test_no_availability_fully_booked(self):
        """
        Test scenario where person is completely booked for the day.
        
        Scenario:
        - Alice: 07:00-19:00 (entire office hours)
        
        Expected: No available slots
        """
        events = [
            Event('Alice', 'All Day Block', time(7, 0), time(19, 0)),
        ]
        
        loader = MockDataLoader(events)
        service = AvailabilityService(loader)
        
        slots = service.find_available_slots(['Alice'], timedelta(hours=1))
        
        self.assertEqual(len(slots), 0)

    def test_gaps_at_day_boundaries(self):
        """
        Test that gaps at the very start (07:00) and end (19:00) are detected.
        
        Scenario:
        - Alice: 10:00-12:00 (middle of day)
        
        Expected: Three gaps - before, after, and at boundaries
        """
        events = [
            Event('Alice', 'Mid-day meeting', time(10, 0), time(12, 0)),
        ]
        
        loader = MockDataLoader(events)
        service = AvailabilityService(loader)
        
        slots = service.find_available_slots(['Alice'], timedelta(hours=1))
        
        # Should have 3 slots: 07:00-10:00, 12:00-19:00
        self.assertEqual(len(slots), 2)
        
        # First slot starts at office start
        self.assertEqual(slots[0].start, time(7, 0))
        self.assertEqual(slots[0].end, time(10, 0))
        
        # Last slot ends at office end
        self.assertEqual(slots[1].start, time(12, 0))
        self.assertEqual(slots[1].end, time(19, 0))

    def test_back_to_back_events_no_gap(self):
        """
        Test that back-to-back events (09:00-10:00, 10:00-11:00) are merged.
        
        Scenario:
        - Alice: 09:00-10:00
        - Alice: 10:00-11:00 (immediately after)
        
        Expected: Treated as single busy block 09:00-11:00
        """
        events = [
            Event('Alice', 'Meeting 1', time(9, 0), time(10, 0)),
            Event('Alice', 'Meeting 2', time(10, 0), time(11, 0)),
        ]
        
        loader = MockDataLoader(events)
        service = AvailabilityService(loader)
        
        slots = service.find_available_slots(['Alice'], timedelta(hours=1))
        
        # Should have 2 slots: before and after the merged block
        self.assertEqual(len(slots), 2)
        self.assertEqual(slots[0].end, time(9, 0))  # Gap ends before merged block
        self.assertEqual(slots[1].start, time(11, 0))  # Gap starts after merged block

    def test_duration_filter(self):
        """
        Test that only gaps meeting minimum duration are returned.
        
        Scenario:
        - Alice: 09:00-09:30 (30 min gap before)
        - Alice: 10:00-11:00 (30 min gap between)
        - Request: 60 minute meeting
        
        Expected: Only gaps >= 60 minutes returned
        """
        events = [
            Event('Alice', 'Short meeting', time(9, 0), time(9, 30)),
            Event('Alice', 'Another meeting', time(10, 0), time(11, 0)),
        ]
        
        loader = MockDataLoader(events)
        service = AvailabilityService(loader)
        
        # Request 60 minute slot
        slots = service.find_available_slots(['Alice'], timedelta(hours=1))
        
        # Should only have slots at boundaries (07:00-09:00 and 11:00-19:00)
        # The 30-minute gap (09:30-10:00) should be excluded
        self.assertEqual(len(slots), 2)
        self.assertTrue(all(slot.duration_minutes() >= 60 for slot in slots))

    def test_empty_person_list_raises_error(self):
        """Test that empty person list raises ValueError."""
        loader = MockDataLoader([])
        service = AvailabilityService(loader)
        
        with self.assertRaises(ValueError):
            service.find_available_slots([], timedelta(hours=1))

    def test_no_events_entire_day_available(self):
        """
        Test that when person has no events, entire office hours are available.
        
        Scenario:
        - Alice exists but has no events
        
        Expected: Single slot covering 07:00-19:00
        """
        events = [
            Event('Bob', 'Bob meeting', time(10, 0), time(11, 0)),
        ]
        
        loader = MockDataLoader(events)
        service = AvailabilityService(loader)
        
        # Request for Alice who has no events
        slots = service.find_available_slots(['Alice'], timedelta(hours=1))
        
        # Entire day should be available
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0].start, time(7, 0))
        self.assertEqual(slots[0].end, time(19, 0))


if __name__ == '__main__':
    unittest.main()
