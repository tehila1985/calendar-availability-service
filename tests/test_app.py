from datetime import time, timedelta
from io_comp.models import Event
from io_comp.services import AvailabilityService
from io_comp.loaders import DataLoader
from typing import List, Set


class MockDataLoader(DataLoader):
    def __init__(self, events: List[Event]):
        self.events = events
    
    def load_events(self) -> List[Event]:
        return self.events


def test_standard_case_with_gaps():
    events = [
        Event('Alice', 'Meeting', time(8, 0), time(9, 30)),
        Event('Alice', 'Lunch', time(13, 0), time(14, 0)),
        Event('Jack', 'Meeting', time(8, 0), time(8, 50)),
        Event('Jack', 'Call', time(9, 0), time(9, 40)),
        Event('Jack', 'Lunch', time(13, 0), time(14, 0)),
    ]
    loader = MockDataLoader(events)
    service = AvailabilityService(loader)
    slots = service.find_available_slots(['Alice', 'Jack'], timedelta(hours=1))
    
    assert time(7, 0) == slots[0].start
    assert time(9, 40) == slots[1].start
    assert time(14, 0) == slots[2].start


def test_no_slots_available():
    events = [
        Event('Alice', 'All Day', time(7, 0), time(19, 0)),
    ]
    loader = MockDataLoader(events)
    service = AvailabilityService(loader)
    slots = service.find_available_slots(['Alice'], timedelta(hours=1))
    
    assert len(slots) == 0


def test_overlapping_events():
    events = [
        Event('Alice', 'Meeting 1', time(9, 0), time(11, 0)),
        Event('Bob', 'Meeting 2', time(10, 0), time(12, 0)),
        Event('Alice', 'Meeting 3', time(10, 30), time(11, 30)),
    ]
    loader = MockDataLoader(events)
    service = AvailabilityService(loader)
    slots = service.find_available_slots(['Alice', 'Bob'], timedelta(hours=1))
    
    assert time(7, 0) == slots[0].start
    assert time(12, 0) == slots[1].start
