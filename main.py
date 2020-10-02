import ast

from line_intersection.kernel import Point, LineSegment, BruteForce
from line_intersection.plane_sweep import PlaneSweep


def process_file(input_file: str, plane_sweep: bool = False):
    """
    Run brute force or plane sweep algorithm on the line segments defined
    in the file :param: input_file
    """
    with open(input_file, 'r') as in_file:
        raw = list(
            map(lambda x: x[:-1] if "\n" in x else x, in_file.readlines()))

    points = list(
        map(
            lambda x: (ast.literal_eval(x.split("--")[0]),
                       ast.literal_eval(x.split("--")[1])), raw))
    lines = list(
        map(
            lambda x: LineSegment(Point(x[0][0], x[0][1]),
                                  Point(x[1][0], x[1][1])), points))

    if plane_sweep:
        algorithm = PlaneSweep(lines)
    else:
        algorithm = BruteForce(lines)
    print("\n".join(list(map(str, algorithm.run()))))
    algorithm.visualize()


def process(plane_sweep: bool = False):
    """
    Run brute force or plane sweep algorithm on the line segments defined
    via insertion in GUI
    """
    if plane_sweep:
        algorithm = PlaneSweep([])
    else:
        algorithm = BruteForce([])
    algorithm.visualize()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        prog='main',
        description=
        "Compute line intersection using plane sweep and brute force")
    parser.add_argument(
        'input',
        metavar='path',
        nargs="?",
        default="",
        type=str,
        help="Path to input file containing a line segment in each line")
    parser.add_argument('--plane-sweep', action='store_true')
    args = parser.parse_args()
    if args.input:
        process_file(args.input, args.plane_sweep)
    else:
        process(args.plane_sweep)
