from dataclasses import dataclass
from typing import Tuple


@dataclass
class AlarmEvent:

    label: str
    confidence: float
    center: Tuple[int, int]
    timestamp: float
    message: str
