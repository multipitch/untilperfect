"""
cli.py

Command line interface for untilperfect.
"""

import argparse
import os
import shutil

import pulp

from .model import BufferPrepProblem, solve


# TODO: Interactive mode with problem returned
# TODO: Improve documentation
# TODO: Consider using click instead of argparse
# TODO: Function to list installed solvers


def main():
    """Provides command line interface to untilperfect.

    Returns
    -------
    int
        Status. See pulp.LpStatus.
    """
    parser = argparse.ArgumentParser(
        prog="model.py",
        add_help=True,
        description=(
            "Solves the buffer preparation assignment and selection problem."
        ),
    )
    parser.add_argument(
        "-b",
        "--buffers",
        default="buffers.csv",
        type=str,
        help="buffers filename (default: 'buffers.csv')",
    )
    parser.add_argument(
        "-n", "--no-plot", action="store_true", help="do not generate plot"
    )
    parser.add_argument(
        "-p",
        "--parameters",
        default="parameters.ini",
        type=str,
        help="parameters filename (default: 'parameters.ini')",
    )
    parser.add_argument(
        "-f",
        "--path",
        default=".",
        type=str,
        help="file path (default: <current working directory>)",
    )
    if shutil.which("cbc"):
        default_solver = "COIN_CMD"
    else:
        default_solver = type(pulp.LpSolverDefault).__name__
    parser.add_argument(
        "-s",
        "--solver",
        default=default_solver,
        type=str,
        help=("solver to be used (default: '{}')".format(default_solver)),
    )
    parser.add_argument(
        "-t",
        "--problem-type",
        default="complete",
        type=str,
        help=(
            "specify model to solve (default: 'complete'), "
            "other model options are 'basic', 'minimized_hold_time', "
            "'mimimized_used_volume'"
        ),
    )
    parser.add_argument(
        "-v",
        "--vessels",
        default="vessels.csv",
        type=str,
        help="vessel filename (default: vessels.csv)",
    )
    parser.add_argument(
        "-w",
        "--write",
        action="store_true",
        help="write problem to file in .lp format",
    )
    args = parser.parse_args()
    path = os.path.abspath(os.path.expanduser(args.path))
    parameters_file = os.path.join(path, args.parameters)
    buffers_file = os.path.join(path, args.buffers)
    vessels_file = os.path.join(path, args.vessels)

    if not args.solver:  # use pulp's default
        solver = None
    elif args.solver.upper() == "PULP_CBC_CMD":
        solver = pulp.solvers.PULP_CBC_CMD(msg=1, threads=os.cpu_count())
    elif args.solver.upper() in ["GLPK", "GLPK_CMD"]:
        solver = pulp.solvers.GLPK(msg=1)
    elif args.solver.upper() in ["COIN", "COIN_CMD"]:
        solver = pulp.solvers.COIN_CMD(msg=1, threads=os.cpu_count())
    else:
        raise ValueError("{} is an unsupported solver.".format(args.solver))

    if args.problem_type is None or args.problem_type.lower() == "complete":
        problem_type = BufferPrepProblem.complete
    elif args.problem_type.lower() == "basic":
        problem_type = BufferPrepProblem.basic
    elif args.problem_type.lower() == "minimized_hold_time":
        problem_type = BufferPrepProblem.minimized_hold_time
        if args.solver and args.solver.upper() in ["GLPK", "GLPK_CMD"]:
            print(
                "Warning: The 'minimized_hold_time' model is not currently "
                "working with GLPK - try another solver.\n"
            )
    elif args.problem_type.lower() == "minimized_used_volume":
        problem_type = BufferPrepProblem.minimized_used_volume
        if args.solver and args.solver.upper() in ["GLPK", "GLPK_CMD"]:
            print(
                "Warning: The 'minimized_hold_time' model is not currently "
                "working with GLPK - try another solver.\n"
            )
    else:
        raise ValueError(
            "'{}' is an invalid problem type.  Valid types are "
            "'basic', 'complete', 'minimized_hold_time'.".format(
                args.problem_type
            )
        )

    plot = not args.no_plot
    write = args.write
    return solve(
        parameters_file,
        buffers_file,
        vessels_file,
        problem_type,
        solver,
        plot,
        write,
        cli=True,
    )


if __name__ == "__main__":
    main()
