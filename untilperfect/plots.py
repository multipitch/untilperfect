"""
plots.py

This module contains functions to plot results.
"""

import shutil

import matplotlib.cm
import matplotlib.patches
import matplotlib.pyplot
import numpy
import pylatexenc.latexencode


# Global settings for matplotlib
def matplotlib_init():
    """Change some matplotlib settings."""
    usetex = True if shutil.which("tex") else False
    matplotlib.pyplot.rc("text", usetex=usetex)
    matplotlib.pyplot.rc("font", family="serif")
    matplotlib.rcParams["hatch.linewidth"] = 0.5


def single_cycle_plot(problem, filename=None):
    """
    Generate a single-cycle steady-state equipment occupancy plot.

    Parameters
    ----------
    problem: untilperfect.Problem
    filename: str or None, optional
        If a filename string is specified, saves plot to file,
        otherwise opens plot in a tk window.
    """
    matplotlib_init()
    N = problem.N
    ct = problem.parameters.cycle_time

    colors = list(matplotlib.cm.tab20(numpy.linspace(0, 1, N)))

    used_slots = set(problem.prep_slots)
    nslots = len(used_slots)
    sorted_slots = sorted(problem.p_to_m, key=problem.p_to_m.get)
    slot_ranks = {}
    for j, i in enumerate(sorted_slots):
        slot_ranks[i] = j
    sorted_prep_names = [problem.p_to_m[i] for i in sorted_slots]
    prep_index = [slot_ranks[i] for i in problem.prep_slots]
    bar_height = 0.6
    figsize = (6.875, 0.25 * (N + nslots + 6.5))
    fig, ax = matplotlib.pyplot.subplots(figsize=figsize)

    # Buffer Hold Vessel Bars
    hold_xranges = []
    hold_yranges = []
    for n in range(N):
        hold_xranges.append(
            (
                cyclic_xranges(
                    problem.hold_start_times[n],
                    problem.hold_total_durations[n],
                    ct,
                )
            )
        )
        hold_yranges.append((N + 1 - (n + 0.5 * bar_height), bar_height))
    for n in range(N):
        ax.broken_barh(
            hold_xranges[n], hold_yranges[n], facecolors=colors[n], zorder=3
        )

    # Buffer Prep Vessel Bars
    prep_xranges = []
    prep_yranges = []
    for n in range(N):
        prep_xranges.append(
            cyclic_xranges(
                problem.prep_start_times[n],
                problem.prep_total_durations[n],
                ct,
            )
        )
        ystart = N + nslots + 2 - (prep_index[n] + 0.5 * bar_height)
        prep_yranges.append((ystart, bar_height))
    for n in range(N):
        ax.broken_barh(
            prep_xranges[n], prep_yranges[n], facecolors=colors[n], zorder=3
        )

    # Tx Bars
    for n in range(N):
        t_tx = problem.parameters.transfer_duration
        xranges = cyclic_xranges(problem.transfer_start_times[n], t_tx, ct)
        ystart = N + nslots + 2 - (prep_index[n] + 0.5 * bar_height)
        yranges = [
            (ystart, bar_height),
            (N + 1 - (n + 0.5 * bar_height), bar_height),
        ]
        for yrange in yranges:
            ax.broken_barh(
                xranges,
                yrange,
                facecolors=colors[n],
                hatch="////",
                edgecolors="black",
                linewidth=0.5,
                zorder=3,
            )

    # Use Bars
    for n in range(N):
        xranges = cyclic_xranges(
            problem.buffers.relative_use_start_times[n],
            problem.buffers.use_durations[n],
            ct,
        )
        ystart = N + nslots + 2 - (prep_index[n] + 0.5 * bar_height)
        yrange = (N + 1 - (n + 0.5 * bar_height), bar_height)
        ax.broken_barh(
            xranges,
            yrange,
            facecolors=colors[n],
            hatch="\\\\\\\\",
            edgecolors="black",
            linewidth=0.5,
            zorder=3,
        )

    # Procedure Outlines
    for n in range(N):
        ax.broken_barh(
            hold_xranges[n],
            hold_yranges[n],
            facecolors="none",
            edgecolors="black",
            linewidth=1,
            zorder=4,
        )
        ax.broken_barh(
            prep_xranges[n],
            prep_yranges[n],
            facecolors="none",
            edgecolors="black",
            linewidth=1,
            zorder=4,
        )

    # Axes and Labels
    ax.grid(axis="x", linestyle="solid", linewidth=1, zorder=0)
    ax.grid(axis="y", linestyle="dashed", linewidth=1, zorder=0)
    ax.set_xlabel("time (h)")
    ax.set_ylabel("Vessels")
    ax.set_yticks(
        [n + 2 for n in range(N)]  ###
        + [i + 2 for i in range(N + 1, N + nslots + 2)]
    )  ###
    ax.set_xticks([8 * t for t in range(int(ct / 8) + 1)])
    prep_labels = []
    for i in sorted_prep_names:
        prep_label = "{} Prep ".format(problem.vessels.names[i])
        prep_labels.append(label_style(prep_label))
    hold_labels = []
    for n in problem.buffers.names:
        hold_label = "{} Hold".format(n)
        hold_labels.append(label_style(hold_label))
    ax.set_yticklabels(hold_labels[::-1] + prep_labels[::-1])
    ax.set_xlim(0, ct)
    ax.set_ylim(0, N + nslots + 2.5)  ###
    proc = matplotlib.patches.Rectangle(
        (0, 0), 1, 1, fc="white", ec="black", lw=1
    )
    op = matplotlib.patches.Rectangle(
        (0, 0), 1, 1, fc="white", ec="black", lw=0.5
    )
    tx = matplotlib.patches.Rectangle(
        (0, 0), 1, 1, fc="white", ec="black", lw=0.5, hatch="////"
    )
    use = matplotlib.patches.Rectangle(
        (0, 0), 1, 1, fc="white", ec="black", lw=0.5, hatch="\\\\\\\\"
    )
    ax.legend(
        [proc, op, tx, use],
        ["procedure", "operation", "transfer", "use"],
        loc=8,
        ncol=4,
        mode="expand",
    )
    matplotlib.pyplot.title("Steady-State Equipment Occupancy")

    # Write to file or plot to screen
    fig.tight_layout()
    if filename:
        matplotlib.pyplot.savefig(filename)
        matplotlib.pyplot.close("all")
    else:
        matplotlib.pyplot.show()


def label_style(label):
    """
    Wrapper to encode labels in latex format if this setting is active.

    Parameters
    ----------
    label: str

    Returns
    -------
    str
    """
    if matplotlib.pyplot.rcParams["text.usetex"]:
        return pylatexenc.latexencode.utf8tolatex(label)
    else:
        return label


def cyclic_xranges(start_time, duration, cycle_time):
    """
    Where a range crosses the cycle time boundary, split into 2 ranges.

    Parameters
    ----------
    start_time: float
    duration: float
    cycle_time: float

    Returns
    -------
    list
        List of operation time ranges.
    """
    if 0 <= start_time < cycle_time:
        if start_time + duration > cycle_time:
            return [
                (0, duration - (cycle_time - start_time)),
                (start_time, cycle_time - start_time),
            ]
        return [(start_time, duration)]
    raise ValueError("start time out of range")
