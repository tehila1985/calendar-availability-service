from datetime import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    """
    Immutable data entity representing a calendar event.
    
    Attributes:
        person: Name of the person who owns this event
        subject: Description of the event
        start_time: When the event starts (time only, no date)
        end_time: When the event ends (time only, no date)
    """
    person: str
    subject: str
    start_time: time
    end_time: time

    def __post_init__(self):
        if self.start_time >= self.end_time:
            raise ValueError(f"Event start time must be before end time: {self.start_time} >= {self.end_time}")
