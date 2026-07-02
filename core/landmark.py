from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Landmark:

    marker_id: int
    corners: List[Tuple[int, int]]
    center: Tuple[int, int]
