from itertools import chain
from enum import Enum, auto


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


class Colour(Enum):
    """
    Colour for red-black tree balancing
    """
    RED = auto()
    BLACK = auto()
    NONE = auto()


class Direction(Enum):
    """
    Direction in search tree
    """
    LEFT = auto()
    RIGHT = auto()


class Node:
    """
    Binary Search Tree node for Points or Line Segments
    I use the red-black tree strategy for balancing out the binary tree
    """
    def __init__(self, value, colour, parent, left=None, right=None):
        """
        :param: value - Point or LineSegment
        :param: parent
        :param: left_child
        :param: right_child
        :param: colour - Colour for Red Black Tree
        """
        self.value = value
        self.parent = parent
        self.left_child = left
        self.right_child = right
        self.colour = colour

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


class BST:
    """
    Self-Balancing Red Black Tree for storing the status and event lists
    Adapted from:
    https://github.com/stanislavkozlovski/Red-Black-Tree/blob/master/rb_tree.py
    """
    LEAF = Node(None, Colour.NONE, None)

    def __init__(self):
        """
        :param: root - root of the BST
        """
        self.root = None
        self.rotations = {
            Direction.LEFT: self._left_rotate,
            Direction.RIGHT: self._right_rotate
        }

    def insert(self, value) -> None:
        """
        Insert a value into the BST
        """
        if not self.root:
            self.root = Node(value,
                             Colour.BLACK,
                             parent=None,
                             left=self.LEAF,
                             right=self.LEAF)
            return

        # Find insert location
        insert_loc, direction = self.find_insertion(self.root, value)
        if direction is None:
            raise Exception("{} already exists in the tree!".format(str(value)))

        node = Node(value,
                    Colour.RED,
                    insert_loc,
                    left=self.LEAF,
                    right=self.LEAF)
        if direction == Direction.LEFT:
            insert_loc.left_child = node
        else:
            insert_loc.right_child = node

        self._balance(node)

    def find_insertion(self, node, value):
        """
        Find location to insert :param: value in tree rooted at :param: node
        """
        if value == node.value:
            return None, None
        elif node.value < value:
            if node.right_child.colour == Colour.NONE:
                return node, Direction.RIGHT
            return self.find_insertion(node.right_child, value)
        if node.left_child.colour == Colour.NONE:
            return node, Direction.LEFT
        return self.find_insertion(node.left_child, value)

    def _balance(self, node) -> None:
        """
        Balance the tree after :param: node has been inserted
        """
        parent = node.parent
        value = node.value

        # Check if tree is already balanced
        if parent is None or parent.parent is None or \
           (node.colour != Colour.RED or parent.colour != Colour.RED):
            return

        # Compute direction for rotation
        grandparent = parent.parent
        node_dir = Direction.LEFT if parent.value > value \
            else Direction.RIGHT
        parent_dir = Direction.LEFT if grandparent.value > parent.value \
            else Direction.RIGHT
        uncle = grandparent.right_child if parent_dir == Direction.LEFT \
            else grandparent.left_child
        directions = (node_dir, parent_dir)

        # Perform appropriate rotations
        if uncle == self.LEAF or uncle.colour == Colour.BLACK:
            if directions == (Direction.LEFT, Direction.LEFT):
                self._right_rotate(node, parent, grandparent, recolour=True)
            elif directions == (Direction.LEFT, Direction.RIGHT):
                self._right_rotate(None, node, parent)
                self._left_rotate(parent, node, grandparent, recolour=True)
            elif directions == (Direction.RIGHT, Direction.LEFT):
                self._left_rotate(None, node, parent)
                self._right_rotate(parent, node, grandparent, recolour=True)
            elif directions == (Direction.RIGHT, Direction.RIGHT):
                self._left_rotate(node, parent, grandparent, recolour=True)
            else:
                return
        # Recolour from the grandparent
        else:
            self._recolour(grandparent)
        return

    def _update_parent(self, node, parent_old_child, new_parent):
        """
        Update the parent of :param: node with :param: new_parent
        """
        node.parent = new_parent
        if new_parent:
            if new_parent.value > parent_old_child.value:
                new_parent.left_child = node
            else:
                new_parent.right_child = node
        else:
            self.root = node
        return

    def _left_rotate(self, node, parent, grandparent, recolour=False):
        """
        Rotate left about :param: node with parent :param: parent,
        grandparent :param: grandparent.
        :param: recolour (False)
        """
        grand_grandparent = grandparent.parent
        self._update_parent(parent, grandparent, grand_grandparent)
        old_left = parent.left_child
        parent.left_child = grandparent
        grandparent.parent = parent

        grandparent.right_child = old_left
        old_left.parent = grandparent

        if recolour:
            parent.colour = Colour.BLACK
            node.colour = Colour.RED
            grandparent.colour = Colour.RED

        return

    def _right_rotate(self, node, parent, grandparent, recolour=False):
        """
        Rotate right about :param: node with parent :param: parent,
        grandparent :param: grandparent.
        :param: recolour (False)
        """
        grand_grandparent = grandparent.parent
        self._update_parent(parent, grandparent, grand_grandparent)
        old_right = parent.right_child
        parent.right_child = grandparent
        grandparent.parent = parent

        grandparent.left_child = old_right
        old_right.parent = grandparent

        if recolour:
            parent.colour = Colour.BLACK
            node.colour = Colour.RED
            grandparent.colour = Colour.RED

        return

    def _recolour(self, node):
        """
        Recolour :param: node
        """
        node.right_child.colour = Colour.BLACK
        node.left_child.colour = Colour.BLACK
        if node != self.root:
            node.colour = Colour.RED
        self._balance(node)
        return

    def delete(self, value) -> None:
        """
        Delete node with :param: value in the tree
        """
        node = self.search(self.root, value)
        if node is None:
            raise Exception("{} is not in the tree".format(str(value)))

        if node.num_children() == 2:
            minimum = self._inorder_successor(node)
            node.value = minimum.value
            node = minimum

        self._delete_at_node(node)

    def _inorder_successor(self, node):
        """
        Get the inorder successor of :param: node
        """
        right_node = node.right_child
        left_node = right_node.left_child
        if left_node == self.LEAF:
            return right_node
        while left_node != self.LEAF:
            left_node = left_node.left_child
        return left_node

    def _delete_at_node(self, node) -> None:
        """
        Delete :param: node. This node always must have < 2 children
        """
        left_child = node.left_child
        right_child = node.right_child
        not_nil_child = left_child if left_child != self.LEAF else right_child

        if node == self.root:
            if not_nil_child != self.LEAF:
                self.root = not_nil_child
                self.root.parent = None
                self.root.colour = Colour.BLACK
            else:
                self.root = None
        elif node.colour == Colour.RED:
            if not node.has_children():
                self._remove_leaf(node)
            else:
                raise Exception("Unexpected behaviour!")
        else:
            if right_child.has_children() or left_child.has_children():
                raise Exception("Invalid black height!")
            if not_nil_child.colour == Colour.RED:
                # Unlink red child
                node.value = not_nil_child.value
                node.left_child = not_nil_child.left_child
                node.right_child = not_nil_child.right_child
            elif not_nil_child.colour == Colour.BLACK:
                self._remove_black_node(node)
            else:
                self._remove_leaf(node)
        return

    def _remove_leaf(self, node):
        """
        Delete leaf node :param: node
        """
        if node.value >= node.parent.value:
            node.parent.right_child = self.LEAF
        else:
            node.parent.left_child = self.LEAF
        return

    def _remove_black_node(self, node):
        """
        Remove black node :param: node
        """
        self.__case_1(node)
        self._remove_leaf(node)

    def __case_1(self, node):
        """
        Case 1 is when there's a double black node on the root
        """
        if self.root == node:
            node.colour = Colour.BLACK
            return
        self.__case_2(node)

    def __case_2(self, node):
        """
        Case 2 applies when
            the parent is BLACK
            the sibling is RED
            the sibling's children are BLACK or NIL
        """
        parent = node.parent
        sibling, direction = self._get_sibling(node)

        if sibling.colour == Colour.RED and \
           parent.colour == Colour.BLACK and \
           sibling.left_child.colour != Colour.RED and \
               sibling.right_child.colour != Colour.RED:
            self.rotations[direction](None, sibling, parent)
            parent.colour = Colour.RED
            sibling.colour = Colour.BLACK
            return self.__case_1(node)
        self.__case_3(node)

    def __case_3(self, node):
        """
        Case 3 deletion is when:
            the parent is BLACK
            the sibling is BLACK
            the sibling's children are BLACK
        """
        parent = node.parent
        sibling, _ = self._get_sibling(node)
        if sibling.colour == Colour.BLACK and \
           parent.colour == Colour.BLACK and \
           sibling.left_child.colour != Colour.RED and \
               sibling.right_child.colour != Colour.RED:
            sibling.colour = Colour.RED
            return self.__case_1(parent)

        self.__case_4(node)

    def __case_4(self, node):
        """
        If the parent is red and the sibling is black with no red children,
        simply swap their colours
        """
        parent = node.parent
        if parent.colour == Colour.RED:
            sibling, direction = self._get_sibling(node)
            if sibling.colour == Colour.BLACK and \
               sibling.left_child.colour != Colour.RED and \
                   sibling.right_child.colour != Colour.RED:
                parent.colour, sibling.colour = sibling.colour, parent.colour
                return
        self.__case_5(node)

    def __case_5(self, node):
        """
        Case 5 is a rotation that changes the circumstances so that we can do a case 6
        """
        sibling, direction = self._get_sibling(node)
        closer_node = sibling.right_child if direction == Direction.LEFT \
            else sibling.left_child
        outer_node = sibling.left_child if direction == Direction.LEFT \
            else sibling.right_child
        if closer_node.colour == Colour.RED and \
           outer_node.colour != Colour.RED and \
               sibling.colour == Colour.BLACK:
            self.rotations[direction](None, closer_node, sibling)
            closer_node.colour = Colour.BLACK
            sibling.colour = Colour.RED

        self.__case_6(node)

    def __case_6(self, node):
        """
        Case 6 requires
            SIBLING to be BLACK
            OUTER NODE to be RED
        """
        sibling, direction = self._get_sibling(node)
        outer_node = sibling.left_child if direction == Direction.LEFT \
            else sibling.right_child

        if sibling.colour == Colour.BLACK and \
           outer_node.colour == Colour.RED:
            parent_colour = sibling.parent.colour
            self.rotations[direction](None, sibling, sibling.parent)
            # new parent is sibling
            sibling.colour = parent_colour
            sibling.right_child.colour = Colour.BLACK
            sibling.left_child.colour = Colour.BLACK
            return

        raise Exception('We should have ended here, something is wrong')

    def _get_sibling(self, node):
        """
        Returns the sibling of :param: node and the side it is on
        """
        parent = node.parent
        if node.value >= parent.value:
            sibling = parent.left_child
            direction = Direction.LEFT
        else:
            sibling = parent.right_child
            direction = Direction.RIGHT
        return sibling, direction

    def search(self, node, value):
        """
        Search for node with :param: value in tree rooted at :param: node
        """
        if node is None or node == self.LEAF:
            return None

        if value > node.value:
            return self.search(node.right_child, value)
        elif value < node.value:
            return self.search(node.left_child, value)
        return node

    def _print_helper(self, node: Node, indent: str, loc: int):
        """
        Recursive function to print subtree rooted at :param: node
        :param: indent
        :param: loc (int) (1 -> root, 2 -> left, 3 -> right)
        """
        if bool(node):
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
    # import random
    # for _ in range(300):
    #     bst = BST()
    #     values = []
    #     for _ in range(20):
    #         v = random.randint(0, 50)
    #         values.append(v)
    #         print("Inserting", v)
    #         bst.insert(v)
    #     bst.print()
    #     for _ in range(10):
    #         i = random.randint(0, 19)
    #         print("Deleting", values[i])
    #         bst.delete(values[i])
    #     bst.print()
    bst = BST()
    bst.insert(10)
    bst.insert(9)
    bst.insert(8)
    bst.insert(7)
    bst.print()
    bst.delete(7)
    bst.print()
