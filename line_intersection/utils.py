from itertools import chain

import line_intersection.kernel as kernel

import pygame


def points(lines: list) -> list:
    """
    Return the points from the list of lines
    """
    return list(
        set(chain.from_iterable([[line.lower, line.upper] for line in lines])))


class PygameConfig:
    """
    Config for pygame
    """
    WHITE = (248, 248, 242)
    BLACK = (40, 42, 54)
    GRAY = (220, 220, 220)
    RED = (255, 85, 85)
    HIGHLIGHT = (255, 184, 108)
    SWEEP = (189, 147, 249)


class _Algorithm:
    """
    Line Intersection algorithm representation
    """
    def __init__(self, lines: list):
        """
        :param: _lines
        :param: _num_lines
        :param: _int_points
        :param: _comparisons
        :param: _grid_size
        """
        self._lines = lines
        self._num_lines = len(lines)
        self._grid_size = 60

    def run(self):
        """
        Run the algorithm
        """
        pass

    def draw_grid(self, surface):
        """
        Draw the cartesian plane and setup the mapping
        for co-ordinates and pixels
        """
        surface.fill(PygameConfig.WHITE)
        self.width, self.height = surface.get_width(), surface.get_height()

        # Compute number of ticks
        self.x_ticks = self.width // self._grid_size
        self.y_ticks = self.height // self._grid_size

        # Instantiate font
        font = pygame.font.Font(pygame.font.get_default_font(), 12)

        for i in range(0, self.width, self._grid_size):
            pygame.draw.line(surface, PygameConfig.GRAY, (i, 0),
                             (i, self.height))
            # Draw x ticks
            pygame.draw.line(surface, PygameConfig.BLACK,
                             (i, self.height // 2 - 3),
                             (i, self.height // 2 + 3))

            # Define tick labels
            text = font.render(
                "{:d}".format(i // self._grid_size - self.x_ticks // 2), True,
                PygameConfig.BLACK)

            # Blit tick labels but change position of origin
            if i // self._grid_size == self.x_ticks // 2:
                surface.blit(text, (i + 3, self.height // 2 + 5))
            else:
                surface.blit(text, (i - 2, self.height // 2 + 5))

        for i in range(0, self.height, self._grid_size):
            pygame.draw.line(surface, PygameConfig.GRAY, (0, i),
                             (self.width, i))
            # Draw y ticks
            pygame.draw.line(surface, PygameConfig.BLACK,
                             (self.width // 2 - 3, i),
                             (self.width // 2 + 3, i))

            # Define tick labels
            text = font.render(
                "{:d}".format(self.y_ticks // 2 - i // self._grid_size), True,
                PygameConfig.BLACK)

            # Blit tick labels but don't blit origin
            if i // self._grid_size != self.y_ticks // 2:
                surface.blit(text, (self.width // 2 - 15, i - 5))

        # Draw x and y axes
        pygame.draw.line(surface, PygameConfig.BLACK, (self.width // 2, 0),
                         (self.width // 2, self.height))
        pygame.draw.line(surface, PygameConfig.BLACK, (0, self.height // 2),
                         (self.width, self.height // 2))
        del font

    def transform(self, point) -> tuple:
        """
        Transform point into pixel co-ordinates
        """
        x = int(self.width // 2 + point.x * self._grid_size)
        y = int(self.height // 2 - point.y * self._grid_size)
        return x, y

    def draw_points(self, surface, points, colour=PygameConfig.BLACK):
        """
        Draw a list of points
        """
        for point in points:
            if point:
                x, y = self.transform(point)
                pygame.draw.circle(surface, colour, (x, y), 5)
        return

    def draw_lines(self, surface, lines, colour=PygameConfig.BLACK):
        """
        Draw a list of lines
        """
        for line in lines:
            # Draw endpoints
            pygame.draw.circle(surface, colour, self.transform(line.upper), 3)
            pygame.draw.circle(surface, colour, self.transform(line.lower), 3)
            # Draw anti-aliased line
            pygame.draw.line(surface, colour, self.transform(line.upper),
                             self.transform(line.lower), 3)
        return

    def draw_widgets(self, surface):
        """
        Draw the forward and backward arrows
        """
        left = pygame.image.load("images/arrow.png")
        left.convert()
        left = pygame.transform.scale(left, (30, 30))
        right = pygame.transform.flip(left, True, False)
        surface.blit(left, (20, self.height - 50))
        surface.blit(right, (70, self.height - 50))

        add = pygame.image.load("images/add.jpg")
        add.convert()
        add = pygame.transform.scale(add, (30, 30))
        surface.blit(add, (self.width - 50, self.height - 50))
        return

    def check_widget(self, pos):
        """
        Given a click position identify the widget
        """
        if self.height - 50 <= pos[1] <= self.height - 20:
            if 20 <= pos[0] <= 50:
                return "left"
            elif 70 <= pos[0] <= 100:
                return "right"
            elif self.width - 50 <= pos[0] <= self.width - 20:
                return "add"
        return None

    def draw_base(self, surface):
        """
        Basic screen to draw
        """
        self.draw_grid(surface)
        self.draw_lines(surface, self._lines)
        self.draw_widgets(surface)
        return

    def make_point(self, pos):
        """
        Given an x,y pixel position create a point
        """
        return kernel.Point(
            round((pos[0] - self.width // 2) / self._grid_size),
            round((self.height // 2 - pos[1]) / self._grid_size))

    def handle_input(self, surface, event, points):
        """
        Handle the input event for line insertion
        """
        if len(points) == 0:
            points.append(self.make_point(event.pos))
            pygame.draw.circle(surface, PygameConfig.BLACK,
                               self.transform(points[0]), 3)
            return points
        points.append(self.make_point(event.pos))
        line = kernel.LineSegment(points[0], points[1])
        self._lines.append(line)
        pygame.draw.circle(surface, PygameConfig.BLACK,
                           self.transform(points[1]), 3)
        pygame.draw.aaline(surface, PygameConfig.BLACK,
                           self.transform(line.upper),
                           self.transform(line.lower))
        self.draw_base(surface)
        return []

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
    def __init__(self, value, balance=0):
        """
        :param: value - LineSegment
        :param: left
        :param: right
        :param: parent
        :param: balance
        :param: height
        """
        self.value = value
        self.left = None
        self.right = None
        self.parent = None
        self.balance = balance
        self.height = 1

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

    def __repr__(self) -> str:
        """
        Overrides the string representation in iterables
        """
        return str(self)


class BST:
    """
    AVL Tree implementation of a BST
    """
    def __init__(self, priority):
        """
        :param: root
        :param: _priority
        """
        self.root = None
        self._priority = priority

    def _get_height(self, root: Node) -> int:
        """
        Get height of :param: root
        """
        if not root:
            return 0
        return root.height

    def _get_balance(self, root: Node) -> int:
        """
        Get balance factor of :param: root
        """
        if not root:
            return 0
        return self._get_height(root.left) - self._get_height(root.right)

    def insert(self, value):
        """
        Insert :param: value into tree
        """
        self.root = self._insert(self.root, value)

    def _insert(self, root, value):
        """
        Insert :param: value into tree rooted at :param: root
        """
        if not root:
            return Node(value)

        if self._priority(value, root.value) < 0:
            left = self._insert(root.left, value)
            root.left = left
            left.parent = root
        elif self._priority(value, root.value) > 0:
            right = self._insert(root.right, value)
            root.right = right
            right.parent = root
        else:
            return root

        root.height = max(self._get_height(root.left),
                          self._get_height(root.right)) + 1
        root.balance = self._get_balance(root)
        return self.rebalance(root)

    def delete(self, value):
        """
        Delete :param: value from tree
        """
        self.root = self._delete(self.root, value)

    def _delete(self, root, value):
        """
        Delete :param: value from tree rooted at :param: root
        """
        if not root:
            return root

        elif self._priority(value, root.value) < 0:
            root.left = self._delete(root.left, value)

        elif self._priority(value, root.value) > 0:
            root.right = self._delete(root.right, value)

        else:
            if not root.left:
                temp = root.right
                root = None
                return temp

            elif not root.right:
                temp = root.left
                root = None
                return temp

            temp = self._min(root.right)
            root.value = temp.value
            root.right = self._delete(root.right, temp.value)

        if not root:
            return root

        root.height = 1 + max(self._get_height(root.left),
                              self._get_height(root.right))
        balance = self._get_balance(root)

        if balance > 1:
            if self._get_balance(root.left) < 0:
                root.left = self._left_rotate(root.left)
            return self._right_rotate(root)

        if balance < -1:
            if self._get_balance(root.right) > 0:
                root.right = self._right_rotate(root.right)
            return self._left_rotate(root)

        return root

    def min(self):
        """
        Minimum value in tree
        """
        return self._min(self.root).value

    def _min(self, root: Node) -> Node:
        """
        Find minimum value in tree rooted at :param: root
        """
        if not root or not root.left:
            return root
        return self._min(root.left)

    def max(self):
        """
        Maximum value in tree
        """
        return self._max(self.root).value

    def _max(self, root: Node) -> Node:
        """
        Find maximum value in tree rooted at :param: root
        """
        if not root or not root.right:
            return root
        return self._max(root.right)

    def pop(self):
        """
        Find the maximum value and delete it
        Used for event list
        """
        if self.root is None:
            return
        max_node = self._max(self.root)
        self.delete(max_node.value)
        return max_node.value

    def _predecessor(self, value) -> Node:
        """
        Find the predecessor of the node with :param: value
        """
        if self.root is None:
            return None
        node = self._search(self.root, value)
        if node.left is not None:
            return self._max(node.left)
        parent = node.parent
        while parent is not None:
            if node != parent.left:
                break
            node = parent
            parent = parent.parent
        return parent

    def _successor(self, value) -> Node:
        """
        Find the successor of the node with :param: value
        """
        if self.root is None:
            return None
        node = self._search(self.root, value)
        if node.right is not None:
            return self._min(node.right)
        parent = node.parent
        while parent is not None:
            if node != parent.right:
                break
            node = parent
            parent = parent.parent
        return parent

    def neighbours(self, value) -> tuple:
        """
        Find the neighbours of two line segments in the status list
        """
        pred = self._predecessor(value)
        succ = self._successor(value)
        if not pred and not succ:
            return None, None
        elif not pred:
            return None, succ.value
        elif not succ:
            return pred.value, succ
        return pred.value, succ.value

    def search(self, value):
        """
        Search for :param: value in tree
        """
        node = self._search(self.root, value)
        if node:
            return node.value
        return None

    def _search(self, root, value) -> Node:
        """
        Search for node with value :param: value in tree rooted
        at :param: root
        """
        if root is None:
            return
        if self._priority(value, root.value) < 0:
            return self._search(root.left, value)
        elif self._priority(value, root.value) > 0:
            return self._search(root.right, value)
        elif self._priority(value, root.value) == 0:
            return root
        print("{} not in tree!".format(str(value)))
        return

    def rebalance(self, root: Node) -> Node:
        """
        Rebalance the tree rooted at :param: root
        """
        if root.balance == 2:
            if root.left.balance < 0:
                root.left = self._left_rotate(root.left)
                return self._right_rotate(root)
            return self._right_rotate(root)
        elif root.balance == -2:
            if root.right.balance > 0:
                root.right = self._right_rotate(root.right)
                return self._left_rotate(root)
            return self._left_rotate(root)
        return root

    def _right_rotate(self, root: Node) -> Node:
        """
        Perform right rotation on the tree rooted at :param: root
        """
        pivot = root.left
        tmp = pivot.right

        pivot.right = root
        pivot.parent = root.parent
        root.parent = pivot

        root.left = tmp
        if tmp:
            tmp.parent = root

        if pivot.parent:
            if pivot.parent.left == root:
                pivot.parent.left = pivot
            else:
                pivot.parent.right = pivot

        root.height = max(self._get_height(root.left),
                          self._get_height(root.right)) + 1
        root.balance = self._get_balance(root)
        pivot.height = max(self._get_height(pivot.left),
                           self._get_height(pivot.right)) + 1
        pivot.balance = self._get_balance(pivot)
        return pivot

    def _left_rotate(self, root: Node) -> Node:
        """
        Perform left rotation on the tree rooted at :param: root
        """
        pivot = root.right
        tmp = pivot.left

        pivot.left = root
        pivot.parent = root.parent
        root.parent = pivot

        root.right = tmp
        if tmp:
            tmp.parent = root

        if pivot.parent:
            if pivot.parent.left == root:
                pivot.parent.left = pivot
            else:
                pivot.parent.right = pivot

        root.height = max(self._get_height(root.left),
                          self._get_height(root.right)) + 1
        root.balance = self._get_balance(root)
        pivot.height = max(self._get_height(pivot.left),
                           self._get_height(pivot.right)) + 1
        pivot.balance = self._get_balance(pivot)
        return pivot

    @staticmethod
    def populate(values: list, priority):
        """
        Insert the values in :param: values into the BST
        using the priority function :priority:
        """
        root = BST(priority)
        for val in values:
            root.insert(val)
        return root

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
            self._print_helper(node.left, indent, 3)
            self._print_helper(node.right, indent, 2)

    def print(self):
        """
        Print BST
        """
        if self.root is None:
            print("Empty tree!")
        else:
            self._print_helper(self.root, "", 1)


if __name__ == "__main__":
    print("--Run main.py--")
