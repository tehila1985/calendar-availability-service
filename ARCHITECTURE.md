# Production-Ready Calendar Availability Solution

## 📁 Project Structure

```
io_comp/
├── models/                    # Data entities (Domain layer)
│   ├── __init__.py
│   ├── event.py              # Calendar event entity
│   └── time_range.py         # Time range with utility methods
│
├── loaders/                   # Data access layer
│   ├── __init__.py
│   ├── data_loader.py        # Abstract interface (Dependency Injection)
│   └── csv_data_loader.py    # CSV implementation
│
├── services/                  # Business logic layer
│   ├── __init__.py
│   └── availability_service.py  # Core algorithm
│
└── app.py                     # Application entry point

tests/
├── test_app.py               # Legacy tests
└── test_availability_service.py  # Comprehensive test suite
```

## 🏗️ Architecture & Design Patterns

### 1. Layered Architecture (Separation of Concerns)

**Models Layer** - Pure data entities
- `Event`: Immutable calendar event (person, subject, times)
- `TimeRange`: Immutable time range with utility methods
- No business logic, only data validation

**Loaders Layer** - Data access abstraction
- `DataLoader`: Abstract interface (ABC)
- `CSVDataLoader`: Concrete CSV implementation
- Easy to extend: add `JSONDataLoader`, `DatabaseLoader`, `APILoader`

**Services Layer** - Business logic
- `AvailabilityService`: Core scheduling algorithm
- Receives data through dependency injection
- No knowledge of data source

**Application Layer** - Entry point
- `app.py`: Wires dependencies together
- Public API for external consumers

### 2. SOLID Principles Applied

**Single Responsibility Principle (SRP)**
- Each class has ONE reason to change:
  - `Event`: Changes only if event structure changes
  - `CSVDataLoader`: Changes only if CSV format changes
  - `AvailabilityService`: Changes only if scheduling logic changes

**Open/Closed Principle (OCP)**
- Open for extension: Add new data sources by implementing `DataLoader`
- Closed for modification: Core logic doesn't change when adding sources

**Liskov Substitution Principle (LSP)**
- Any `DataLoader` implementation can replace another
- Service works with any loader without knowing the concrete type

**Interface Segregation Principle (ISP)**
- `DataLoader` interface is minimal and focused
- Clients only depend on methods they use

**Dependency Inversion Principle (DIP)**
- `AvailabilityService` depends on `DataLoader` abstraction, not concrete CSV loader
- High-level policy (scheduling) doesn't depend on low-level details (file I/O)

### 3. Dependency Injection

```python
# Bad: Hard-coded dependency
class AvailabilityService:
    def __init__(self):
        self.loader = CSVDataLoader('calendar.csv')  # ❌ Tight coupling

# Good: Injected dependency
class AvailabilityService:
    def __init__(self, data_loader: DataLoader):  # ✅ Loose coupling
        self.data_loader = data_loader
```

**Benefits:**
- Testability: Inject mock loaders in tests
- Flexibility: Swap data sources without changing service
- Maintainability: Clear dependencies

## 🧮 Algorithm: Interval Merging

### Overview
The solution uses an efficient **Interval Merging** algorithm to find available time slots.

### Steps

1. **Filter Events** - O(N)
   - Extract events for requested participants
   - Convert to `TimeRange` objects

2. **Sort by Start Time** - O(N log N)
   - Sort all busy ranges chronologically
   - This is the bottleneck but necessary for merging

3. **Merge Overlapping Ranges** - O(N)
   - Combine overlapping/adjacent busy blocks
   - Single pass through sorted list
   - Example: `[08:00-09:30, 09:00-09:40]` → `[08:00-09:40]`

4. **Find Gaps** - O(N)
   - Check gap before first event
   - Check gaps between consecutive events
   - Check gap after last event
   - Filter by minimum duration

### Complexity Analysis

**Time Complexity: O(N log N)**
- N = number of events for requested participants
- Dominated by sorting step
- All other operations are O(N)

**Space Complexity: O(N)**
- Store filtered events and merged ranges

### Why This Is Efficient

**Scalability:**
- 10 events: 10 * log(10) ≈ 33 operations
- 100 events: 100 * log(100) ≈ 664 operations
- 1000 events: 1000 * log(1000) ≈ 9,966 operations

**Real-world Performance:**
- Typical calendar: 5-20 events per person per day
- With 3 people and 15 events each: 45 * log(45) ≈ 247 operations
- Executes in microseconds on modern hardware

**Alternative Approaches (Worse):**
- Brute force: O(N²) - check every pair of events
- Minute-by-minute scan: O(720) for 12-hour day - wasteful for sparse calendars

## 🔧 Configuration

### Office Hours
Easily configurable in `AvailabilityService`:

```python
class AvailabilityService:
    OFFICE_START = time(7, 0)   # 07:00
    OFFICE_END = time(19, 0)    # 19:00
```

Change these constants to adjust for different time zones or work schedules.

## 🧪 Testing Strategy

### Test Coverage (7 comprehensive tests)

1. **test_overlapping_events_from_multiple_users**
   - Validates interval merging with complex overlaps
   - Tests: Alice (09:00-11:00), Bob (10:00-12:00), Alice (10:30-11:30)
   - Expected: Merged to single block 09:00-12:00

2. **test_no_availability_fully_booked**
   - Edge case: Person booked entire day (07:00-19:00)
   - Expected: No available slots

3. **test_gaps_at_day_boundaries**
   - Validates detection of gaps at start (07:00) and end (19:00)
   - Tests: Single event 10:00-12:00
   - Expected: Gaps before and after

4. **test_back_to_back_events_no_gap**
   - Tests merging of adjacent events (09:00-10:00, 10:00-11:00)
   - Expected: Treated as continuous busy block

5. **test_duration_filter**
   - Validates that only gaps >= requested duration are returned
   - Tests: 30-minute gaps with 60-minute request
   - Expected: Only large gaps returned

6. **test_empty_person_list_raises_error**
   - Input validation: Empty person list should raise ValueError

7. **test_no_events_entire_day_available**
   - Edge case: Person exists but has no events
   - Expected: Entire office hours available

### Running Tests

```bash
# Run all tests
python -m pytest tests/test_availability_service.py -v

# Run specific test
python -m pytest tests/test_availability_service.py::TestAvailabilityService::test_overlapping_events_from_multiple_users -v

# Run with coverage
python -m pytest tests/test_availability_service.py --cov=io_comp --cov-report=html
```

## 🚀 Usage

### Basic Usage

```python
from datetime import timedelta
from io_comp.loaders import CSVDataLoader
from io_comp.services import AvailabilityService

# Initialize with dependency injection
loader = CSVDataLoader('resources/calendar.csv')
service = AvailabilityService(loader)

# Find slots for specific people
slots = service.find_available_slots(['Alice', 'Jack'], timedelta(hours=1))

# Print results
for slot in slots:
    print(f"Available: {slot}")
```

### Dynamic People Detection

```python
# Get all people from calendar
all_people = service.get_all_people()
print(f"People: {', '.join(sorted(all_people))}")

# Find slots for everyone
slots = service.find_available_slots(list(all_people), timedelta(minutes=30))
```

### Custom Data Source

```python
from io_comp.loaders import DataLoader
from io_comp.models import Event

class DatabaseLoader(DataLoader):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def load_events(self):
        # Load from database
        rows = self.db.query("SELECT * FROM events")
        return [Event(r.person, r.subject, r.start, r.end) for r in rows]

# Use with service
loader = DatabaseLoader(my_db_connection)
service = AvailabilityService(loader)
```

## 📊 Output Format

```
People in calendar: Alice, Bob, Jack
Meeting duration: 1:00:00

Available slots for all people:
Starting Time of available slots: 07:00 - 08:00
Starting Time of available slots: 11:30 - 13:00
Starting Time of available slots: 15:00 - 16:00
Starting Time of available slots: 17:00 - 19:00
```

## 🛡️ Error Handling

### Input Validation
- Empty person list → `ValueError`
- Invalid duration → `ValueError`
- Invalid time format in CSV → `ValueError` with row number
- Missing CSV file → `FileNotFoundError`

### Data Validation
- Event start >= end → `ValueError` (in Event.__post_init__)
- TimeRange start >= end → `ValueError` (in TimeRange.__post_init__)

## 🔄 Extensibility Examples

### Add JSON Support
```python
class JSONDataLoader(DataLoader):
    def load_events(self):
        with open(self.file_path) as f:
            data = json.load(f)
        return [Event(**item) for item in data]
```

### Add Multi-Day Support
```python
@dataclass
class Event:
    person: str
    subject: str
    start_datetime: datetime  # Changed from time
    end_datetime: datetime
```

### Add Priority Scheduling
```python
class PriorityAvailabilityService(AvailabilityService):
    def find_available_slots(self, person_list, duration, priority='high'):
        slots = super().find_available_slots(person_list, duration)
        return self._filter_by_priority(slots, priority)
```

## 📝 Key Design Decisions

1. **Immutable Entities**: `Event` and `TimeRange` are frozen dataclasses
   - Thread-safe
   - Prevents accidental mutations
   - Clear data flow

2. **Type Hints**: Strict typing throughout
   - Better IDE support
   - Catches errors at development time
   - Self-documenting code

3. **No Global State**: All dependencies injected
   - Testable
   - Predictable
   - No hidden dependencies

4. **Single Day Constraint**: Events use `time` not `datetime`
   - Simplifies logic as per requirements
   - Easy to extend to multi-day later

5. **Office Hours as Constants**: Configurable but not parameterized
   - Keeps API simple
   - Easy to change for different organizations
   - Could be moved to config file if needed

## 🎯 Interview Talking Points

1. **Why Interval Merging?**
   - O(N log N) is optimal for this problem
   - Sorting is unavoidable to detect overlaps efficiently
   - Alternative approaches are O(N²) or wasteful

2. **Why Dependency Injection?**
   - Testability: Mock data sources in tests
   - Flexibility: Swap CSV for database without changing logic
   - SOLID: Dependency Inversion Principle

3. **Why Immutable Entities?**
   - Thread-safety for concurrent requests
   - Prevents bugs from accidental mutations
   - Functional programming benefits

4. **Scalability Considerations**
   - Current: O(N log N) handles thousands of events easily
   - Future: Could add caching for repeated queries
   - Future: Could add indexing for large datasets

5. **Production Readiness**
   - Comprehensive error handling
   - Type safety
   - Extensive test coverage
   - Clear documentation
   - Modular architecture for maintenance
