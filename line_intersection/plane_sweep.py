from queue import Queue
from enum import Enum, auto

from line_intersection.kernel import Point, LineSegment, BST
from line_intersection.utils import _Algorithm

class EventType(Enum):
    UPPER = auto()
    LOWER = auto()
    INTERSECTION = auto()

class PlaneSweep(_Algorithm):
    """
    Plane sweep line intersection algorithm
    """

    def __init__(self, line: list):
        """
        :param: _lines
        :param: _int_points
        :param: _comparisons
        :param: _status
        :param: _events
        """
        super().__init__(lines)
        self._comparisons = []
        self._status = Status()
        self._events = Queue()

    def run(self) -> list:
        """
        Run plane sweep algorithm to compute the intersection points
        """
        # Initialize the event points
        for segment in self._lines:
            self._events.put(
