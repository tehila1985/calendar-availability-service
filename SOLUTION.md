# Calendar Availability Finder - Solution Documentation

## Architecture Overview

This solution follows SOLID principles with clear separation of concerns:

### Core Components

1. **CalendarEvent** (Entity Layer)
   - Represents a single calendar event
   - Immutable data structure with person, subject, start_time, and end_time

2. **CalendarLoader** (Data Layer)
   - Handles CSV parsing and data validation
   - Converts raw CSV data into CalendarEvent objects
   - Decoupled from business logic

3. **AvailabilityEngine** (Logic Layer)
   - Core algorithm for finding available time slots
   - Uses interval merging approach
   - Independent of data source

## Algorithm: Interval Merging

The solution uses an efficient interval merging algorithm:

1. **Filter**: Extract events for requested participants
2. **Sort**: Order events by start time
3. **Merge**: Combine overlapping/consecutive busy blocks
4. **Find Gaps**: Identify available slots between merged blocks

**Time Complexity**: O(n log n) due to sorting
**Space Complexity**: O(n) for storing events

## Key Design Decisions

### Office Hours Enforcement
- Day starts at 07:00 and ends at 19:00
- Slots are checked before first event, between events, and after last event

### Edge Cases Handled
- Empty participant list → returns empty list
- No events for participants → entire day available (if duration fits)
- Overlapping events → properly merged into single busy block
- Back-to-back events (e.g., 09:00-10:00, 10:00-11:00) → treated as continuous busy time
- Duration longer than any gap → no slots returned

### Time Slot Output
Returns start times of available slots (not ranges), as per the example output format.

## Running the Application

```bash
# From python-project directory
python -m io_comp.app
```

## Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/test_app.py -v
```

## Test Coverage

1. **test_standard_case_with_gaps**: Validates normal scenario with multiple gaps
2. **test_no_slots_available**: Ensures no false positives when fully booked
3. **test_overlapping_events**: Verifies correct merging of overlapping intervals

## Example Output

For Alice & Jack with 60-minute duration:
```
Available slots for Alice, Jack (duration: 1:00:00):
Starting Time of available slots: 07:00
Starting Time of available slots: 09:40
Starting Time of available slots: 14:00
Starting Time of available slots: 17:00
```

## Extensibility

The modular design allows easy extensions:
- Add different data sources (JSON, database) by implementing new loaders
- Support multi-day calendars by extending CalendarEvent
- Add priority-based scheduling by enhancing AvailabilityEngine
- Implement different algorithms without changing data layer
