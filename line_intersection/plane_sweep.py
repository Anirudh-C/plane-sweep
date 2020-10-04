from queue import Queue
import time
from enum import Enum, auto

from line_intersection.kernel import Point, LineSegment, BST
from line_intersection.utils import _Algorithm, PygameConfig, Priority

import pygame
import numpy as np


class EventType(Enum):
    """
    Representation for event type
    """
    UPPER = auto()
    LOWER = auto()
    INTERSECTION = auto()


class PlaneSweep(_Algorithm):
    """
    Plane sweep line intersection algorithm
    """
    def __init__(self, lines: list):
        """
        :param: _lines
        :param: _int_points
        :param: _comparisons
        :param: _status
        :param: _events
        :param: _sweep
        :param: _int_sweep
        """
        super().__init__(lines)
        if self._lines:
            self._initialize()

    def _initialize(self) -> None:
        """
        Initialize all the relevant artefacts for plane sweep
        """
        self._comparisons = []
        self._int_points = set()
        self._sweep = 0
        self._current = None
        events = []
        for line in self._lines:
            events.append((line.upper, EventType.UPPER, line))
            events.append((line.lower, EventType.LOWER, line))
        self._events = BST.populate(events, self._point_priority)
        self._sweep = self._events.max()[0].y
        self._status = BST(self._segment_priority)

    def _point_priority(self, p1: tuple, p2: tuple) -> int:
        """
        Priority function for points in event queue
        """
        # Points at same y co-ordinate
        if p1[0].y == p2[0].y:
            # Order on x co-ordinate
            if p1[0].x < p2[0].x:
                return Priority.MORE
            elif p1[0].x > p2[0].x:
                return Priority.LESS
            return Priority.SAME_VAL
        elif p1[0].y < p2[0].y:
            return Priority.LESS
        return Priority.MORE

    def _sweep_intersection(self, line: LineSegment) -> Point:
        """
        Compute intersection point of :param: line and sweep line
        """
        if line.eqn[0] == np.inf:
            if line.upper.y == self._sweep:
                return line.upper
            elif line.lower.y == self._sweep:
                return line.lower
            return Point(line.lower.x, self._sweep)
        int_x = round((self._sweep - line.eqn[1]) / line.eqn[0], 6)
        return Point(int_x, self._sweep)

    def _segment_priority(self, l1: LineSegment, l2: LineSegment) -> Priority:
        """
        Priority function for line segments in status list
        """
        # If the same line segment is passed the priority is the same
        if l1 == l2:
            return Priority.SAME_VAL
        slopes = l1.eqn[0], l2.eqn[0]
        # Only handle general case
        if slopes[0] != 0 and slopes[1] != 0:
            int_point1 = self._sweep_intersection(l1)
            int_point2 = self._sweep_intersection(l2)
            if int_point1.x < int_point2.x:
                return Priority.LESS
            elif int_point1.x > int_point2.x:
                return Priority.MORE
            else:
                # l1 and l2 are intersecting at the sweep line
                if l1.lower.x < l2.lower.x:
                    return Priority.LESS
                elif l1.lower.x > l2.lower.x:
                    return Priority.MORE
                else:
                    raise Exception("General point assumption failed!")
        raise Exception("General point assumption failed!")

    def _handle_upper_event(self, event: tuple) -> None:
        """
        Handle event points that are upper endpoints of line segments
        """
        self._sweep = event[0].y
        self._status.insert(event[2])
        left, right = self._status.neighbours(event[2])
        if left:
            int_left = event[2].intersection(left)
            if int_left:
                self._events.insert(
                    (int_left, EventType.INTERSECTION, (left, event[2])))
                self._int_points.add(int_left)
            self._comparisons.append({
                "index":
                (self._lines.index(left), self._lines.index(event[2])),
                "point":
                int_left,
                "sweep":
                self._sweep
            })
        if right:
            int_right = event[2].intersection(right)
            if int_right:
                self._events.insert(
                    (int_right, EventType.INTERSECTION, (event[2], right)))
                self._int_points.add(int_right)
            self._comparisons.append({
                "index":
                (self._lines.index(event[2]), self._lines.index(right)),
                "point":
                int_right,
                "sweep":
                self._sweep
            })
        self._comparisons.append({
            "index":
            (self._lines.index(event[2]), self._lines.index(event[2])),
            "point":
            None,
            "sweep":
            self._sweep
        })
        return

    def _handle_lower_event(self, event: tuple) -> None:
        """
        Handle event points that are lower endpoints of line segments
        """
        self._sweep = event[0].y
        left, right = self._status.neighbours(event[2])
        self._status.delete(event[2])
        if left and right and left != right:
            int_point = left.intersection(right)
            if int_point:
                self._events.insert(
                    (int_point, EventType.INTERSECTION, (left, right)))
                self._int_points.add(int_point)
            self._comparisons.append({
                "index": (self._lines.index(left), self._lines.index(right)),
                "point":
                int_point,
                "sweep":
                event[0].y
            })
        self._comparisons.append({
            "index":
            (self._lines.index(event[2]), self._lines.index(event[2])),
            "point":
            None,
            "sweep":
            event[0].y
        })
        return

    def _handle_intersection(self, event: tuple) -> None:
        """
        Handle event points that are intersection points
        """
        # Swap the line segments
        self._status.swap(event[2][0], event[2][1])
        self._sweep = event[0].y

        # Compute neighbours
        left = [None] * 2
        right = [None] * 2
        for i in range(2):
            left[i], right[i] = self._status.neighbours(event[2][i])

        # Compute intersections
        for i in range(2):
            if left[i]:
                int_left = event[2][i].intersection(left[i])
                if int_left:
                    if int_left not in self._int_points:
                        self._events.insert((int_left, EventType.INTERSECTION,
                                             (left[i], event[2][i])))
                        self._int_points.add(int_left)
                self._comparisons.append({
                    "index": (self._lines.index(event[2][i]),
                              self._lines.index(left[i])),
                    "point":
                    int_left,
                    "sweep":
                    self._sweep
                })
            if right[i]:
                int_right = event[2][i].intersection(right[i])
                if int_right:
                    if int_right not in self._int_points:
                        self._events.insert((int_right, EventType.INTERSECTION,
                                             (event[2][i], right[i])))
                        self._int_points.add(int_right)
                self._comparisons.append({
                    "index": (self._lines.index(event[2][i]),
                              self._lines.index(right[i])),
                    "point":
                    int_right,
                    "sweep":
                    self._sweep
                })
        return

    def run(self) -> list:
        """
        Run plane sweep algorithm to compute the intersection points
        """
        event = self._events.pop()
        while event is not None:
            print(event)
            self._current = event
            if event[1] == EventType.LOWER:
                self._handle_lower_event(event)
            elif event[1] == EventType.UPPER:
                self._handle_upper_event(event)
            else:
                self._handle_intersection(event)
            event = self._events.pop()
        return self._int_points

    def draw_comparison(self, surface, index):
        """
        Highlight the comparison at index
        """
        if index in range(len(self._comparisons)):
            sweep = self._comparisons[index]["sweep"]
            # Refresh screen
            self.draw_base(surface)
            # Highlight lines being compared
            line_ids = self._comparisons[index]["index"]
            if line_ids[0] != line_ids[1]:
                lines = [self._lines[line_ids[0]], self._lines[line_ids[1]]]
                self.draw_lines(surface, lines, colour=PygameConfig.HIGHLIGHT)
            # Draw Sweep line
            pygame.draw.line(
                surface, PygameConfig.SWEEP,
                (0, self.height // 2 - sweep * self._grid_size),
                (self.width, self.height // 2 - sweep * self._grid_size), 2)
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
        pygame.display.set_caption("Plane Sweep Line Intersection")
        self.draw_base(SURF)
        font = pygame.font.Font(pygame.font.get_default_font(), 12)
        algo_text = font.render("Ran Plane Sweep Algorithm!", True,
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
                        insertion = False
                        if len(self._lines) > self._num_lines:
                            self._initialize()
                            self.run()
                            SURF.blit(algo_text, (30, 30))
                            self._num_lines = len(self._lines)
                        else:
                            self.draw_base(SURF)
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
