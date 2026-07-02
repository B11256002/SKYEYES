from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Detection:

    label: str
    confidence: float
    corners: List[Tuple[int, int]]
    center: Tuple[int, int]
    timestamp: float

    inside_boundary: bool = False
    tracked_id: int = -1