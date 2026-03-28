from dataclasses import dataclass
from datetime import date, time
from typing import Optional

@dataclass
class Attendance:
    id: int
    card_uid: str
    student_number: str
    at_date: date
    time_in: time
    time_out: Optional[time] = None