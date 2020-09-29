from itertools import chain

def points(lines: list) -> list:
    """
    Return the points from the list of lines
    """
    return list(
        set(chain.from_iterable([[line.lower, line.upper] for line in lines])))


class _Algorithm:
    """
    Line Intersection algorithm representation
    """
    def __init__(self, lines: list):
        """
        :param: _lines
        :param: _int_points
        :param: _comparisons
        """
        self._lines = lines

    def run(self):
        """
        Run the algorithm
        """
        pass

    def visualize(self):
        """
        Visualize the running of the algorithm
        """
        pass

    def print(self) -> None:
        """
        Print the lines and the intersection points
        """
        # Print Lines
        print("Lines:")
        print("\n".join(map(str, self._lines)))
        # Print intersection points but filter empty points out
        print("Intersection Points:")
        print("\n".join(map(str, filter(lambda x: not x, self._int_points))))


class Node:
    """
    Binary Search Tree node for Points or Line Segments
    """
    def __init__(self, value):
        """
        :param: value - LineSegment
        :param: left_child
        :param: right_child
        """
        self.value = value
        self.left_child = None
        self.right_child = None

    def num_children(self) -> int:
        """
        Number of child the node has
        """
        if self.value is None:
            return 0
        return bool(self.left_child) + bool(self.right_child)

    def has_children(self) -> bool:
        """
        True if the node has children
        """
        return bool(self.num_children())

    def __bool__(self) -> bool:
        """
        Overrides default boolean representation
        """
        return bool(self.value)

    def __eq__(self, other) -> bool:
        """
        Overrides equality
        """
        if isinstance(other, Node):
            return self.value == other.value
        return False

    def __str__(self) -> str:
        """
        Overrides the string representation
        """
        return str(self.value)

if __name__ == "__main__":
    pass
