import math
from enum import Enum, auto

import numpy as np

from line_intersection.utils import points, _Algorithm, BST


class Intersection(Enum):
    """
    Representation for type of line intersection
    """
    OVERLAP = auto()
    END_POINT = auto()
    NORMAL = auto()


class Point:
    """
    Representation for a point in the x-y plane
    """
    def __init__(self, x: float, y: float, intersection: Intersection = None):
        """
        :param: x
        :param: y
        """
        self.x = x
        self.y = y
        self.intersection = intersection

    def __bool__(self) -> bool:
        """
        Overrides default boolean representation
        """
        return self.x is not None and self.y is not None

    def __eq__(self, other) -> bool:
        """
        Overrides default equal to
        """
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        """
        Overrides hash to put Point in immutable types
        """
        return hash((self.x, self.y))

    def __str__(self) -> str:
        """
        Overrides string representation
        """
        return str((self.x, self.y))

    def __repr__(self) -> str:
        """
        Overrides representation in iterables
        """
        return str(self)


class LineSegment:
    """
    Representation for a line segment in the x-y plane
    """
    def __init__(self, p1: Point, p2: Point):
        """
        :param: lower
        :param: upper
        :param: eqn (slope, intercept)
        """
        if p1.y < p2.y:
            self.lower = p1
            self.upper = p2
        elif p1.y > p2.y:
            self.lower = p2
            self.upper = p1
        else:
            if p1.x < p2.x:
                self.lower = p1
                self.upper = p2
            else:
                self.lower = p2
                self.upper = p1
        self.eqn = self._prep_eqn()

    def __eq__(self, other) -> bool:
        """
        Overrides default equal to
        """
        return self.lower == other.lower and \
                self.upper == other.upper

    def __bool__(self) -> bool:
        """
        Overrides default boolean representation
        """
        return bool(self.lower) and bool(self.upper)

    def __hash__(self) -> int:
        """
        Overrides hash to put Point in immutable types
        """
        return hash((self.lower, self.upper, self.eqn))

    def __str__(self) -> str:
        """
        Overrides the default string representation
        """
        return str(self.lower) + " -- " + str(self.upper)

    def __repr__(self) -> str:
        """
        Overrides representation in iterables
        """
        return str(self)

    def __contains__(self, point) -> bool:
        """
        Check if :param: point is in line
        """
        if point.y == self.eqn[0] * point.x + self.eqn[1]:
            return self.lower.x <= point.x <= self.upper.x
        return False

    def _prep_eqn(self) -> dict:
        """
        Pre-compute the slope and y intercept of the line
        """
        if self.lower.x == self.upper.x:
            return (np.inf, -self.lower.x)
        elif self.lower.y == self.upper.y:
            return (0, self.lower.y)
        slope = (self.upper.y - self.lower.y) / (self.upper.x - self.lower.x)
        intercept = (self.lower.y * self.upper.x - self.upper.y * self.lower.x)\
            / (self.upper.x - self.lower.x)
        return (slope, intercept)

    def intersection(self, line) -> Point:
        """
        Compute an intersection point with another line segment
        :param: line - LineSegment object
        :return: Point
        """
        # Check if line segments are overlapping
        if self.eqn == line.eqn:
            if line.upper in self:
                return Point(line.upper.x, line.upper.y, Intersection.OVERLAP)
            elif line.lower in self:
                return Point(line.lower.x, line.lower.y, Intersection.OVERLAP)
        elif self.eqn[0] == line.eqn[0]:
            return Point(None, None)

        # Compute intersection point
        x = (self.eqn[1] - line.eqn[1]) \
            / (line.eqn[0] - self.eqn[0])
        y = \
            (self.eqn[1] * line.eqn[0]
             - line.eqn[1] * self.eqn[0]) \
            / (line.eqn[0] - self.eqn[0])

        int_point = Point(x, y)
        if int_point in points([self, line]):
            int_point.intersection = Intersection.END_POINT
        else:
            int_point.intersection = Intersection.NORMAL
        # Check if the intersection actually lies on one of the line segments
        if int_point in self or int_point in line:
            return int_point
        return Point(None, None)


class BruteForce(_Algorithm):
    """
    Brute-force line intersection algorithm
    """
    def __init__(self, lines: list):
        """
        :param: _lines
        :param: _int_points
        :param: _comparisons
        """
        super().__init__(lines)
        self._comparisons = []

    def run(self) -> list:
        """
        Run brute force algorithm to compute intersection points.
        Keep track of each comparison and the point added to it.
        """
        int_points = set()
        for i in range(len(self._lines)):
            for j in range(len(self._lines)):
                if i != j:
                    point = self._lines[i].intersection(self._lines[j])
                    int_points.add(point)
                    self._comparisons.append({"index": (i, j), "point": point})
        self._int_points = list(int_points)
        return self._int_points


if __name__ == "__main__":
    print("--Run main.py--")
