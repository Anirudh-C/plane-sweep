import os
# Disable pygame startup message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import math
from enum import Enum, auto
from itertools import cycle

from line_intersection.utils import points, _Algorithm, BST, PygameConfig

import pygame
import numpy as np


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

    def coords(self):
        """
        Computes co-ordinates for pygame
        """
        return (self.x, self.y)

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
        return str(self.lower) + "--" + str(self.upper)

    def __repr__(self) -> str:
        """
        Overrides representation in iterables
        """
        return str(self)

    def __contains__(self, point) -> bool:
        """
        Check if :param: point is in line
        """
        return min(self.lower.x, self.upper.x) <= point.x <= max(self.lower.x, self.upper.x) and \
            self.lower.y <= point.y <= self.upper.y

    def _prep_eqn(self) -> dict:
        """
        Pre-compute the slope and y intercept of the line
        """
        # Check for vertical lines
        if self.lower.x == self.upper.x:
            return (np.inf, np.inf)
        # Check for horizontal lines
        if self.lower.y == self.upper.y:
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
            if line.lower in self:
                return Point(line.lower.x, line.lower.y, Intersection.OVERLAP)
            if line.upper in self:
                return Point(line.upper.x, line.upper.y, Intersection.OVERLAP)

        # Check for horizontal lines
        if self.eqn[0] == line.eqn[0]:
            return Point(None, None)

        # Check for vertical lines
        if self.eqn[0] == np.inf and line.eqn[0] == np.inf:
            if line.upper in self:
                return Point(line.upper.x, line.upper.y, Intersection.OVERLAP)
            if line.lower in self:
                return Point(line.lower.x, line.lower.y, Intersection.OVERLAP)
            return Point(None, None)

        elif self.eqn[0] == np.inf:
            x = self.lower.x
            y = line.eqn[0] * x + line.eqn[1]
            point = Point(x, y)
            if point in line:
                return point
            return Point(None, None)
        elif line.eqn[0] == np.inf:
            x = line.lower.x
            y = self.eqn[0] * x + self.eqn[1]
            point = Point(x, y)
            if point in self:
                return point
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
        if int_point in self and int_point in line:
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
        self._comparisons = []
        for i in range(len(self._lines)):
            for j in range(len(self._lines)):
                if i != j:
                    point = self._lines[i].intersection(self._lines[j])
                    if point:
                        int_points.add(point)
                    self._comparisons.append({"index": (i, j), "point": point})
        self._int_points = list(int_points)
        return self._int_points

    def draw_comparison(self, surface, index):
        """
        Highlight the comparison at index
        """
        if index in range(len(self._comparisons)):
            # Refresh screen
            self.draw_base(surface)
            # Highlight lines being compared
            line_ids = self._comparisons[index]["index"]
            lines = [self._lines[line_ids[0]], self._lines[line_ids[1]]]
            self.draw_lines(surface, lines, colour=PygameConfig.HIGHLIGHT)
            # Highlight intersection if any
            if self._comparisons[index]["point"]:
                self.draw_points(surface, [self._comparisons[index]["point"]],
                                 colour=PygameConfig.HIGHLIGHT)
            # Keep track of already found intersection points
            self.draw_points(surface,
                             list(
                                 map(lambda x: x["point"],
                                     self._comparisons[:index])),
                             colour=PygameConfig.RED)
        elif index < 0:
            self.draw_base(surface)
        elif index >= len(self._comparisons):
            self.draw_base(surface)
            self.draw_points(surface, self._int_points, PygameConfig.RED)
        return

    def visualize(self):
        """
        Draw the lines and intersection points
        """
        # Initialize drawing surface
        pygame.init()
        SURF = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Brute Force Line Intersection")
        self.draw_base(SURF)
        font = pygame.font.Font(pygame.font.get_default_font(), 12)
        algo_text = font.render("Ran Brute-Force Algorithm!", True,
                                PygameConfig.BLACK)
        insertion_text = font.render("Inserting Line Segment", True,
                                     PygameConfig.BLACK)

        # Initializations for comparison traversal
        comparison_id = -1

        # Initializations for line insertion
        insertion = False
        points = []

        # Initializations for line deletion
        deletions = []

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        return

                    elif event.key == pygame.K_z:
                        if event.mod & pygame.KMOD_CTRL and self._lines:
                            deletions.append(self._lines.pop())
                            self.draw_base(SURF)

                    elif event.key == pygame.K_r:
                        if event.mod & pygame.KMOD_CTRL and deletions:
                            self._lines.append(deletions.pop())
                            self.draw_base(SURF)

                    elif event.key == pygame.K_s:
                        if event.mod & pygame.KMOD_CTRL and self._lines:
                            self.draw_base(SURF)
                            file_name = time.strftime(
                                "tests/test-%Y%m%d-%H%M.txt")
                            save_text = font.render(
                                "Saved Line Segments to {}".format(file_name),
                                True, PygameConfig.BLACK)
                            with open(file_name, "w") as out:
                                out.write("\n".join(list(map(str,
                                                             self._lines))))
                            SURF.blit(save_text, (30, 30))

                    elif event.key == pygame.K_ESCAPE:
                        comparison_id = -1
                        insertion = False
                        self.draw_base(SURF)

                    elif event.key == pygame.K_RETURN:
                        self.draw_base(SURF)
                        if len(self._lines) > self._num_lines:
                            self.run()
                            SURF.blit(algo_text, (30, 30))
                            self._num_lines = len(self._lines)
                        else:
                            self.draw_points(SURF, self._int_points,
                                             PygameConfig.RED)

                    elif event.key == pygame.K_BACKSPACE:
                        self.draw_base(SURF)

                elif event.type == pygame.MOUSEBUTTONDOWN and not insertion:
                    # Traverse the comparisons or flag for insertion
                    widget = self.check_widget(event.pos)

                    if widget == "left":
                        self.draw_comparison(SURF, comparison_id - 1)
                        if comparison_id >= 0:
                            comparison_id -= 1
                        else:
                            comparison_id = -1

                    elif widget == "right":
                        self.draw_comparison(SURF, comparison_id + 1)
                        if comparison_id <= len(self._comparisons) - 1:
                            comparison_id += 1
                        else:
                            comparison_id = len(self._comparisons)

                    elif widget == "add":
                        SURF.blit(insertion_text, (30, 30))
                        insertion = True

                elif event.type == pygame.MOUSEBUTTONDOWN and insertion:
                    points = self.handle_input(SURF, event, points)

                elif event.type == pygame.MOUSEMOTION and insertion:
                    mouse_position = pygame.mouse.get_pos()

                    if len(points) > 0:
                        self.draw_base(SURF)
                        SURF.blit(insertion_text, (30, 30))
                        pygame.draw.line(SURF, PygameConfig.BLACK,
                                         self.transform(points[0]),
                                         mouse_position, 2)
            pygame.display.update()
        return


if __name__ == "__main__":
    print("--Run main.py--")
    l1 = LineSegment(Point(-9, -2), Point(2, 6))
    l2 = LineSegment(Point(-7, 1), Point(3, 2))
    print(l1.intersection(l2))
