import math
from enum import Enum, auto

import numpy as np

from line_intersection.utils import points, _Algorithm, Node


class Intersection(Enum):
    """
    Representation for type of line intersection
    """
    OVERLAP = auto()
    END_POINT = auto()
    NORMAL = auto()


class EventType(Enum):
    """
    Representation for type of event
    """
    LOWER = auto()
    UPPER = auto()
    INTERSECTION = auto()

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
        :param: eqn (slope, intercept)
        :param: event_type
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
        self.event_type = EventType.UPPER

    def __eq__(self, other) -> bool:
        """
        Overrides default equal to
        """
        if isinstance(other, LineSegment):
            return self.eqn == other.eqn
        return False

    def __bool__(self) -> bool:
        """
        Overrides default boolean representation
        """
        return self.lower is None or self.upper is None

    def __lt__(self, other) -> bool:
        """
        Overrides default lesser than for status list
        """
        if self.event_type == EventType.UPPER:
            return self.upper.x < other.upper.x
        return self.lower.x < other.lower.x

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

class Status:
    """
    Binary Search tree for status list
    """
    def __init__(self):
        """
        :param: root - root of the BST
        """
        self.root = None

    def insert(self, value) -> None:
        """
        Insert a value into the BST
        """
        if self.root is None:
            self.root = Node(value)
            return

        parent, direction = self.find_insertion(self.root, value)
        if parent is None:
            print("{} is already in the status!".format(str(value)))
            return
        if direction is 'L':
            parent.left_child = Node(value)
            return
        parent.right_child = Node(value)
        return

    def find_insertion(self, node, value):
        """
        Find location to insert :param: value in tree rooted at :param: node
        """
        if value == node.value:
            return None, None
        elif value < node.value:
            if node.left_child is None:
                return node, 'L'
            return self.find_insertion(node.left_child, value)
        if node.right_child is None:
            return node, 'R'
        return self.find_insertion(node.right_child, value)

    def delete(self, value) -> None:
        """
        Delete node with :param: value in the tree
        """
        self.root = self._delete_at_node(self.root, value)
        return

    def _delete_at_node(self, node, value) -> None:
        """
        Delete :param: from tree rooted at :param: node.
        """
        if node is None:
            return node

        if value < node.value:
            node.left_child = self._delete_at_node(node.left_child, value)
        elif value > node.value:
            node.right_child = self._delete_at_node(node.right_child, value)
        else:
            if node.left_child is None:
                return node.right_child
            elif node.right_child is None:
                return node.left_child

            minimum = self._inorder_successor(node)
            node.value = minimum.value
            node.right_child = self._delete_at_node(node.right_child, minimum.value)
        return node

    def _inorder_successor(self, node):
        """
        Get the inorder successor of :param: node
        """
        right_node = node.right_child
        left_node = right_node.left_child
        if left_node is None:
            return right_node
        while left_node is not None:
            left_node = left_node.left_child
        return left_node

    def search(self, value):
        """
        Search for node with :param: value
        """
        return self._search_helper(self.root, value)

    def _search_helper(self, node, value):
        """
        Search for node with :param: value in tree rooted at :param: node
        """
        if node is None:
            return None

        if value > node.value:
            return self._search_helper(node.right_child, value)
        elif value < node.value:
            return self._search_helper(node.left_child, value)
        return node

    def _print_helper(self, node: Node, indent: str, loc: int):
        """
        Recursive function to print subtree rooted at :param: node
        :param: indent
        :param: loc (int) (1 -> root, 2 -> left, 3 -> right)
        """
        if node is not None:
            print(indent, end="")
            if loc == 1:
                print("root: ", end="")
                indent += "\t"
            elif loc == 3:
                print("L----", end="")
                indent += "|\t"
            else:
                print("R----", end="")
                indent += "\t"
            print(node)
            self._print_helper(node.left_child, indent, 3)
            self._print_helper(node.right_child, indent, 2)

    def print(self):
        """
        Print BST
        """
        self._print_helper(self.root, "", 1)

if __name__ == "__main__":
    pts = [Point(1,2), Point(3,7), Point(2,4)]
    print(sorted(pts))
    l1 = LineSegment(Point(3, 7), Point(2, 1))
    l2 = LineSegment(Point(2, 2), Point(5, 5))
    l3 = LineSegment(Point(3, 2), Point(4, 6))
    l4 = LineSegment(Point(3, 7), Point(2, 2))
    l5 = LineSegment(Point(1, 0), Point(2, 1))
    status = Status()
    status.insert(l1)
    status.insert(l2)
    status.insert(l3)
    status.insert(l4)
    status.insert(l5)
    status.delete(l2)
    status.print()
