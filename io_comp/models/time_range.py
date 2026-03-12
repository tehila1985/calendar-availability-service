from datetime import time, datetime, timedelta
from dataclasses import dataclass


@dataclass(frozen=True)
class TimeRange:
    """
    Immutable data entity representing a time range within a single day.
    
    Attributes:
        start: Start time of the range
        end: End time of the range
    """
    start: time
    end: time

    def __post_init__(self):
        if self.start >= self.end:
            raise ValueError(f"Start time must be before end time: {self.start} >= {self.end}")

    def duration_minutes(self) -> int:
        """Calculate the duration of this time range in minutes."""
        start_dt = datetime.combine(datetime.today(), self.start)
        end_dt = datetime.combine(datetime.today(), self.end)
        return int((end_dt - start_dt).total_seconds() / 60)

    def overlaps_with(self, other: 'TimeRange') -> bool:
        """Check if this time range overlaps with another."""
        return self.start < other.end and other.start < self.end

    def is_adjacent_to(self, other: 'TimeRange') -> bool:
        """Check if this time range is directly adjacent to another (no gap)."""
        return self.end == other.start or other.end == self.start

    def merge_with(self, other: 'TimeRange') -> 'TimeRange':
        """Merge this time range with another, returning a new TimeRange."""
        return TimeRange(
            start=min(self.start, other.start),
            end=max(self.end, other.end)
        )

    def __str__(self) -> str:
        return f"{self.start.strftime('%H:%M')} - {self.end.strftime('%H:%M')}"
