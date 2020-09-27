from itertools import chain
from enum import Enum, auto

def points(lines: list) -> list:
    """
    Return the points from the list of lines
    """
    return list(set(chain.from_iterable(
        [[line.lower,line.upper] for line in lines])))

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
        print("\n".join(
            map(str, self._lines)))
        # Print intersection points but filter empty points out
        print("Intersection Points:")
        print("\n".join(
            map(str, filter(
                lambda x: not x, self._int_points))))

class Colour(Enum):
    """
    Colour for red-black tree balancing
    """
    RED = auto()
    BLACK = auto()

class Node:
    """
    Binary Search Tree node for Points or Line Segments
    I use the red-black tree strategy for balancing out the binary tree
    """

    def __init__(self, value):
        """
        :param: value - Point or LineSegment
        :param: parent
        :param: left_child
        :param: right_child
        :param: colour - Colour for Red Black Tree
        """
        self.value = value
        self.parent = None
        self.left_child = None
        self.right_child = None
        self.colour = Colour.RED

    def __bool__(self) -> bool:
        """
        Overrides the boolean representation
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
        node = Node(value)
        parent = None
        current = self.root

        # Search for location to insert node
        while current is not None:
            parent = current
            if node.value < current.value:
                current = current.left_child
            else:
                current = current.right_child

        # Add in node
        node.parent = parent
        if parent is None:
            self.root = node
        elif node.value < parent.value:
            parent.left_child = node
        else:
            parent.right_child = node

        # Balance the tree post insertion
        if node.parent is None:
            node.colour = Colour.BLACK
            return

        if node.parent.parent is None:
            return

        self.insert_balance(node)
        return

    def insert_balance(self, node) -> None:
        """
        Balance the tree after :param: node has been inserted
        """
        if node is None or node.parent is None:
            return
        elif node.parent.colour == Colour.RED:
            # Find uncle
            if node.parent == node.parent.parent.right_child:
                which_uncle = "L"
                uncle = node.parent.parent.left_child
            else:
                uncle = node.parent.parent.right_child
                which_uncle = "R"
            # Recolour vertices or rotate based on colour of uncle
            node.parent.colour = Colour.BLACK
            node.parent.parent.colour = Colour.RED
            if uncle is not None and uncle.colour == Colour.RED:
                uncle.colour = Colour.BLACK
            else:
                if which_uncle == "L":
                    print(node == node.parent)
                    if node == node.parent.left_child:
                        node = node.parent
                        self.right_rotate(node)
                    self.left_rotate(node.parent.parent)
                else:
                    if node == node.parent.right_child:
                        node = node.parent
                        self.left_rotate(node)
                    self.right_rotate(node.parent.parent)

            # Recursively balance grandparent
            if node != self.root:
                self.insert_balance(node.parent.parent)

        # Colour the root black and finish
        self.root.colour = Colour.BLACK
        return

    def _replace(self, x: Node, y: Node) -> None:
        """
        Replace :param: x with :param: y in the tree
        """
        if x.parent is None:
            self.root = y
        elif x == x.parent.left_child:
            x.parent.left_child = y
        else:
            x.parent.right_child = y
        if y is not None:
            y.parent = x.parent

    def minimum(self, node):
        """
        Find minimmum node in tree rooted at :param: node
        """
        while node.left_child is not None:
            node = node.left_child
        return node

    def delete(self, value) -> None:
        """
        Delete node with :param: value in the tree
        """
        return self.delete_at_node(self.root, value)

    def delete_at_node(self, node, value) -> None:
        """
        Delete node with :param: value in the tree rooted at :param: node
        """
        match = None
        # Search for the value
        while node is not None:
            if node.value == value:
                match = node

            if node.value <= value:
                node = node.right_child
            else:
                node = node.left_child

        if match is None:
            print("No match found for {}".format(str(value)))
            return

        # Recolour and replace nodes as required
        deleted = match
        colour = deleted.colour
        if match.left_child is None:
            rot = match.right_child
            self._replace(match, match.right_child)
        elif match.right_child is None:
            rot = match.left_child
            self._replace(match, match.left_child)
        else:
            deleted = self.minimum(match.right_child)
            colour = deleted.colour
            rot = deleted.right_child
            if deleted.parent == match:
                rot.parent = deleted
            else:
                self._replace(deleted, deleted.right_child)
                deleted.right_child = match.right_child
                deleted.right_child.parent = deleted

            self._replace(match, deleted)
            deleted.left_child = match.left_child
            deleted.left_child.parent = deleted
            deleted.colour = match.colour

        # Balance tree if original node was black
        if colour == Colour.BLACK:
            self.delete_balance(rot)

    def delete_balance(self, node):
        """
        Balance tree at :param: node after deletion
        """
        if node != self.root and node.colour == Colour.BLACK:
            # Find Sibling
            if node == node.parent.left_child:
                which_child = "L"
                sibling = node.parent.right_child
            else:
                which_child = "R"
                sibling = node.parent.left_child

            # Rotate and recolour
            if sibling.colour == Colour.RED:
                sibling.colour = Colour.BLACK
                node.parent.colour = Colour.RED
                if which_child == "L":
                    self.left_rotate(node.parent)
                    sibling = node.parent.right_child
                else:
                    self.right_rotate(node.parent)
                    sibling = node.parent.left_child

            # Check colours of siblings and recursively balance
            if sibling.left_child.colour == Colour.BLACK and \
               sibling.right_child.colour == Colour.BLACK:
                sibling.colour = Colour.RED
                self.delete_balance(node.parent)
            else:
                if which_child == "L" and \
                   sibling.right_child.colour == Colour.BLACK:
                    sibling.left_child.colour == Colour.BLACK
                    sibling.Colour = Colour.RED
                    self.right_rotate(sibling)
                    # Switch Sibling
                    sibling = node.parent.right_child
                elif which_child == "R" and \
                     sibling.left_child.colour == Colour.BLACK:
                    sibling.right_child.colour = Colour.BLACK
                    sibling.Colour = Colour.RED
                    self.left_rotate(sibling)
                    # Switch Sibling
                    sibling = node.parent.left_child

                sibling.colour = node.parent.colour
                node.parent.colour = Colour.BLACK
                if which_child == "L":
                    sibling.right_child.colour = Colour.BLACK
                    self.left_rotate(node.parent)
                else:
                    sibling.left_child.colour = Colour.BLACK
                    self.right_rotate(node.parent)
                self.delete_balance(self.root)

        # Colour root black and finish
        node.colour = Colour.BLACK
        return

    def left_rotate(self, node):
        """
        Rotate left about :param: node
        """
        temp = node.right_child
        node.right_child = temp.left_child
        if temp.left_child is not None:
            temp.left_child.parent = node

        temp.parent = node.parent
        if node.parent is None:
            self.root = temp
        elif node == node.parent.left_child:
            node.parent.left_child = temp
        else:
            node.parent.right_child = temp

        temp.left_child = node
        node.parent = temp

    def right_rotate(self, node):
        """
        Rotate right about :param: node
        """
        temp = node.left_child
        node.left_child = temp.right_child
        if temp.right_child is not None:
            temp.right_child.parent = node

        temp.parent = node.parent
        if node.parent is None:
            self.root = temp
        elif node == node.parent.right_child:
            node.parent.right_child = temp
        else:
            node.parent.left_child = temp

        temp.right_child = node
        node.parent = temp

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
            print(node, node.colour)
            self._print_helper(node.left_child, indent, 3)
            self._print_helper(node.right_child, indent, 2)

    def print(self):
        """
        Print BST
        """
        self._print_helper(self.root, "", 1)

if __name__ == "__main__":
    bst = BST()
    bst.insert(10)
    bst.insert(12)
    bst.insert(13)
    # bst.insert(7)
    # bst.insert(6)
    # bst.insert(11)
    # bst.print()
    # bst.delete(7)
    bst.print()
