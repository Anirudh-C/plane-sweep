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

    def __init__(self, x: float, y: float,
                 intersection: Intersection = None):
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
        return self.x is None or self.y is None

    def __eq__(self, other) -> bool:
        """
        Overrides default equal to
        """
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return False

    def __lt__(self, other) -> bool:
        """
        Overrides default lesser than for event queue
        """
        return self.y < other.y

    def __le__(self, other) -> bool:
        """
        Overrides default lesser than or equal to for event queue
        """
        return self.y <= other.y

    def __gt__(self, other) -> bool:
        """
        Overrides default greater than for event queue
        """
        return self.y > other.y

    def __ge__(self, other) -> bool:
        """
        Overrides default greater than or equal to for event queue
        """
        return self.y >= other.y

    def __hash__(self) -> int:
        """
        Overrides hash to put Point in immutable types
        """
        return hash((self.x, self.y))

    def __str__(self) -> str:
        """
        Overrides string representation
        """
        if self.intersection is not None:
            return str((self.x, self.y, self.intersection))
        return str((self.x,self.y))

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
        if isinstance(other, LineSegment):
            return self.lower == other.lower and self.upper == other.upper
        return False

    def __bool__(self) -> bool:
        """
        Overrides default boolean representation
        """
        return self.lower == self.upper

    def __lt__(self, other) -> bool:
        """
        Overrides default lesser than for status list
        """
        if self.lower.x < other.lower.x:
            return True
        elif self.lower.x > other.lower.x:
            return False
        else:
            if self.upper.x < other.upper.x:
                return True
            else:
                return False

    def __le__(self, other) -> bool:
        """
        Overrides default lesser than or equal to for status list
        """
        return self < other or self == other

    def __gt__(self, other) -> bool:
        """
        Overrides default greater than for status list
        """
        return other < self

    def __ge__(self, other) -> bool:
        """
        Overrides default greater than or equal to for status list
        """
        return self > other or self == other

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

    def _prep_eqn(self) -> dict:
        """
        Pre-compute the slope and y intercept of the line
        """
        if self.lower.x == self.upper.x:
            return (np.inf, -self.lower.x)
        elif self.lower.y == self.upper.y:
            return (0, self.lower.y)
        slope = (self.upper.y - self.lower.y)/(self.upper.x - self.lower.x)
        intercept = (self.lower.y * self.upper.x - self.upper.y * self.lower.x)\
            / (self.upper.x - self.lower.x)
        return (slope, intercept)

    def intersection(self, line) -> Point:
        """
        Compute an intersection point with another line segment
        :param: line - LineSegment object
        :return: Point
        """
        if self.eqn == line.eqn:
            return Point(self.lower.x, self.lower.y, Intersection.OVERLAP)
        elif self.eqn[0] == line.eqn[0]:
            return Point(None,None)
        # Compute intersection point
        x = (self.eqn[1] - line.eqn[1]) \
            / (line.eqn[0] - self.eqn[0])
        y = \
            (self.eqn[1] * line.eqn[0]
             - line.eqn[1] * self.eqn[0]) \
            / (line.eqn[0] - self.eqn[0])
        int_point = Point(x,y)
        if int_point in points([self,line]):
            int_point.intersection = Intersection.END_POINT
        else:
            int_point.intersection = Intersection.NORMAL
        return int_point


class BruteForce(_Algorithm):
    """
    Brute-force line intersection algorithm
    """
    def __init__(self, lines: list):
        """
        :param: _lines
        :param: _int_points
        """
        super().__init__(lines)

    def run(self) -> list:
        """
        Run brute force algorithm to compute intersection points.
        Keep track of each comparison and the point added to it.
        """
        int_points = set()
        self._comparisons = []
        for i in range(len(self._lines)):
            for j in range(len(self._lines)):
                if i != j:
                    point = self._lines[i].intersection(self._lines[j])
                    int_points.add(point)
                    self._comparisons.append(
                        {
                            "index": (i,j),
                            "point": point
                        })
        self._int_points = list(int_points)
        return self._int_points

if __name__ == "__main__":
    l1 = LineSegment(Point(3, 7), Point(2, 1))
    l2 = LineSegment(Point(2, 2), Point(5, 5))
    l3 = LineSegment(Point(3, 2), Point(4, 6))
    l4 = LineSegment(Point(3, 7), Point(2,2))
    l5 = LineSegment(Point(1, 0), Point(2, 1))
    brute = BruteForce([l1,l2,l3,l4,l5])
    brute.run()
    brute.print()
    bst = BST()
    bst.insert(l1)
    bst.insert(l2)
    bst.insert(l3)
    bst.print()
    bst.delete(l2)
    bst.print()
