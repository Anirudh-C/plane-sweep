from queue import Queue
import time
from enum import Enum, auto

from line_intersection.kernel import Point, Intersection, LineSegment, BST
from line_intersection.utils import _Algorithm, PygameConfig

import pygame


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
        self._int_points = set()
        self._comparisons = []
        self._sweep = 0
        self._int_sweep = (None, None)
        if self._lines:
            self._initialize()

    def _initialize(self):
        """
        Initialize all the relevant artefacts for plane sweep
        """
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
            return p1[0].x - p2[0].x
        elif p1[0].y < p2[0].y:
            return -1
        elif p1[0].y > p2[0].y:
            return 1
        return 0

    def _check_int_event(self, l1: LineSegment, l2: LineSegment) -> bool:
        """
        Sanity check to reverse priority when an intersection point
        is an event point
        """
        if self._int_sweep[0] and self._int_sweep[1]:
            if self._int_sweep == (l1, l2):
                return True
            elif self._int_sweep == (l2, l1):
                return True
        return False

    def _segment_priority(self, l1: LineSegment, l2: LineSegment) -> int:
        """
        Priority function for line segments in status list
        """
        # If the same line segment is passed the priority is the same
        if l1 == l2:
            return 0
        # Check for horizontal lines
        if l1.eqn[0] == 0 and l2.eqn[0] == 0:
            return l1.lower.x - l2.lower.x

        elif l1.eqn[0] == 0:
            # Sanity check
            if l1.eqn[1] == self._sweep:
                int_point = (self._sweep - l2.eqn[1]) / l2.eqn[0]
                if l1.lower.x <= int_point:
                    priority = -1
                else:
                    priority = 1
                if self._check_int_event(l1, l2):
                    return -priority
                return priority
            return 0

        elif l2.eqn[0] == 0:
            # Sanity check
            if l2.eqn[1] == self._sweep:
                int_point = (self._sweep - l1.eqn[1]) / l1.eqn[0]
                if l2.lower.x <= int_point:
                    priority = -1
                else:
                    priority = 1
                # If we are at the intersection point event
                # then reverse the priority
                if self._check_int_event(l1, l2):
                    return -priority
                return priority
            return 0

        # Compute intersections with sweep line
        int_point1 = (self._sweep - l1.eqn[1]) / l1.eqn[0]
        int_point2 = (self._sweep - l2.eqn[1]) / l2.eqn[0]
        if int_point1 <= int_point2:
            priority = -1
        else:
            priority = 1
        # If we are at the intersection point event
        # then reverse the priority
        if self._check_int_event(l1, l2):
            return -priority
        return priority

    def _handle_upper_event(self, event):
        """
        Handle event points that are upper endpoints of line segments
        """
        self._sweep = event[0].y
        self._status.insert(event[2])
        left, right = self._status.neighbours(event[2])
        if left:
            int_left = event[2].intersection(left)
            if int_left:
                if int_left.intersection == Intersection.NORMAL and \
                   int_left not in self._int_points:
                    self._events.insert(
                        (int_left, EventType.INTERSECTION, (event[2], left)))
                self._int_points.add(int_left)
            self._comparisons.append({
                "index":
                (self._lines.index(event[2]), self._lines.index(left)),
                "point":
                int_left,
                "sweep":
                self._sweep
            })
        if right:
            int_right = event[2].intersection(right)
            if int_right:
                if int_right.intersection == Intersection.NORMAL and \
                   int_right not in self._int_points:
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

    def _handle_lower_event(self, event):
        """
        Handle event points that are lower endpoints of line segments
        """
        self._sweep = event[0].y
        left, right = self._status.neighbours(event[2])
        if left and right:
            int_point = left.intersection(right)
            if int_point:
                if int_point.intersection == Intersection.NORMAL and \
                   int_point not in self._int_points:
                    self._events.insert(
                        (int_point, EventType.INTERSECTION, (left, right)))
                self._int_points.add(int_point)
            self._comparisons.append({
                "index": (self._lines.index(left), self._lines.index(right)),
                "point":
                int_point,
                "sweep":
                self._sweep
            })
        self._status.delete(event[2])
        return

    def _handle_intersection(self, event):
        """
        Handle event points that are intersection points
        """
        self._sweep = event[0].y
        # Swap the order of the intersecting line segments
        self._status.delete(event[2][0])
        self._status.delete(event[2][1])
        self._int_sweep = event[2]
        self._status.insert(event[2][0])
        self._status.insert(event[2][1])
        # Compute new neighbours and check intersection
        neighbours = self._status.neighbours(event[2][0]), \
            self._status.neighbours(event[2][1])
        for i in range(2):
            for line in neighbours[i]:
                if line and line not in event[2]:
                    int_point = event[2][i].intersection(line)
                    if int_point:
                        self._int_points.add(int_point)
                        if int_point.intersection == Intersection.NORMAL and \
                           int_point not in self._int_points:
                            self._events.insert(
                                (int_point, EventType.INTERSECTION,
                                 (event[2][i], line)))
                    self._comparisons.append({
                        "index": (self._lines.index(event[2][i]),
                                  self._lines.index(line)),
                        "point":
                        int_point,
                        "sweep":
                        self._sweep
                    })
        self._int_sweep = None, None
        return

    def run(self) -> list:
        """
        Run plane sweep algorithm to compute the intersection points
        """
        event = self._events.pop()
        while event is not None:
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
