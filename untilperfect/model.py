"""
model.py

This module contains the definition of the buffer preparation vessel
assignment problem along with classes for Parameters, Buffers and
Vessels. It also contains a function for solving the problem.
"""


import numpy
import pulp

from untilperfect.pulptools import LpVariableArray
from untilperfect.plots import single_cycle_plot
from untilperfect.iotools import column_reader, get_config_section

# PROJECT TODOs:
# TODO: Incorporate type hinting to improve documentation
# TODO: Semantics around model vs model instance vs problem vs ...
# TODO: Unit tests
#
# FILE TODOs:
# TODO: Improve documentation!!!
# TODO: Repeater with increasing number of slots may be faster than
#       P = N
# TODO: CLI argument to allow interactive run with problem returned for
#       probing.


class Parameters:
    """Problem parameters.

    Parameters
    ----------
    data: str or dict
        Pass either a filename string or a dict of parameters to
        initialize a Parameters instance. The filename should be that
        of a valid parameters file; in ini format and with a
        [parameters] section.

    """

    # TODO: Use 'required=False' to disable constraints if parameters omitted
    def __init__(self, data):
        if isinstance(data, str):
            datadict = get_config_section(data, "parameters")
        elif isinstance(data, dict):
            datadict = data
        else:
            raise TypeError("data should be a filename string or a dict")
        self.cycle_time = self._get_parameter_data(
            "cycle_time", float, datadict, None, True
        )
        self.prep_pre_duration = self._get_parameter_data(
            "prep_pre_duration", float, datadict, None, True
        )
        self.prep_post_duration = self._get_parameter_data(
            "prep_post_duration", float, datadict, None, True
        )
        self.transfer_duration = self._get_parameter_data(
            "transfer_duration", float, datadict, None, True
        )
        self.hold_pre_duration = self._get_parameter_data(
            "hold_pre_duration", float, datadict, None, True
        )
        self.hold_post_duration = self._get_parameter_data(
            "hold_post_duration", float, datadict, None, True
        )
        self.hold_duration_min = self._get_parameter_data(
            "hold_duration_min", float, datadict, 0.0, False
        )
        self.hold_duration_max = self._get_parameter_data(
            "hold_duration_max", float, datadict, self.cycle_time, False
        )
        self.minimum_fill_ratio = self._get_parameter_data(
            "minimum_fill_ratio", float, datadict, 0.0, False
        )
        self.maximum_prep_utilization = self._get_parameter_data(
            "maximum_prep_utilization", float, datadict, 1.0, False
        )
        self.max_slots = self._get_parameter_data(
            "max_slots", int, datadict, 0, False
        )
        self.max_types = self._get_parameter_data(
            "max_types", int, datadict, 0, False
        )
        self.prep_total_duration = (
            self.prep_pre_duration
            + self.transfer_duration
            + self.prep_post_duration
        )

    @staticmethod
    def _get_parameter_data(
        pname, ptype, datadict, default=None, required=True
    ):
        """Populates parameter data from an input dict."""
        try:
            value = datadict[pname]
        except KeyError:
            if required:
                raise KeyError
            value = default
        return ptype(value)


class Data:
    """
    Parent class of 'Buffers' and 'Vessels'. If initialized with a
    'dict', reads data from the 'dict'. If initialized with a 'str',
    treats it as a filename and reads data from the file.

    Parameters
    ----------
    data: str or dict
        Pass either a filename string or a dict of parameters to
        initialize a Data class instance. The filename should be that
        of a valid data file (csv format).

    """

    # TODO: Improve parsing capabilities / error checks
    # TODO: Move parsing elsewhere, make this a dataclass?
    def __init__(self, data):
        if isinstance(data, str):
            self.input_dict = column_reader(data)
        elif isinstance(data, dict):
            self.input_dict = data
        else:
            raise TypeError("data should be a filename string or a dict")


class Vessels(Data):
    """
    Selection of preparation vessels available for use.

    Parameters
    ----------
    data: str or dict
        Pass either a filename string or a dict of parameters to
        initialize a Vessels class instance. The filename should be that
        of a valid data file (csv format).
    """

    def __init__(self, data):
        super().__init__(data)
        self.names = self.input_dict["names"]
        self.volumes = self.input_dict["volumes"]
        self.costs = self.input_dict["costs"]
        self.max_volume = max(self.volumes)
        self.min_volume = min(self.volumes)
        self.count = len(self.names)


class Buffers(Data):
    """
    Selection of buffers to be prepared.

    Parameters
    ----------
    data: str or dict
        Pass either a filename string or a dict of parameters to
        initialize a Data class instance. The filename should be that
        of a valid data file (csv format).
    """

    def __init__(self, data):
        super().__init__(data)
        self.names = self.input_dict["names"]
        self.volumes = self.input_dict["volumes"]
        self.absolute_use_start_times = self.input_dict["use_start_times"]
        self.use_durations = self.input_dict["use_durations"]
        self.relative_use_start_times = None
        self.count = len(self.names)

    def set_relative_use_start_times(self, cycle_time):
        """
        Calculates use start times relative to cycle.

        Parameters
        ----------
        cycle_time: float
            Process cycle time.
        """
        self.relative_use_start_times = [
            time % cycle_time for time in self.absolute_use_start_times
        ]


class BufferPrepProblem:
    """
    Determines the optium selection and assignment of prep vessels.

    Parameters
    ----------
    parameters: untilperfect.Parameters
    buffers: untilperfect.Buffers
    vessels: untilperfect.Vessels
    solver: None or pulp.LpSolver, optional
    """

    def __init__(self, parameters, buffers, vessels, solver=None):
        # initialize problem
        self.problem = pulp.LpProblem(sense=pulp.LpMinimize)
        self.solver = solver

        # acquire data
        self.parameters = parameters
        self.buffers = buffers
        self.vessels = vessels
        self.buffers.set_relative_use_start_times(self.parameters.cycle_time)

        # define dimensions
        self.M = self.vessels.count
        self.N = self.buffers.count
        if self.parameters.max_slots > 0:
            self.P = min(self.parameters.max_slots, self.N)
        else:
            self.P = self.N

        # define decision variables
        self.variables = set()
        self.b = self._new_variable("b", self.M, cat="Binary")
        self.q = self._new_variable("q", self.N, cat="Binary")
        self.r = self._new_variable("r", self.N, cat="Binary")
        self.s = self._new_variable("s", self.N, cat="Binary")
        self.u = self._new_variable("u", self.N, cat="Binary")
        self.v = self._new_variable("v", (self.N, self.N), cat="Binary")
        self.w = self._new_variable(
            "w", (self.N, self.N, self.P), cat="Binary"
        )
        self.x = self._new_variable("x", (self.N, self.P), cat="Binary")
        self.y = self._new_variable("y", (self.M, self.P), cat="Binary")
        self.z = self._new_variable(
            "z",
            (self.N,),
            self.parameters.hold_duration_min,
            self.parameters.hold_duration_max,
            "Continuous",
        )

        # initialize results
        # TODO: Are all of these necessary in the class?
        self.n_to_p = None
        self.p_to_m = None
        self.prep_slots = None
        self.prep_vessels = None
        self.prep_start_times = None
        self.hold_start_times = None
        self.transfer_start_times = None
        self.prep_total_durations = None
        self.hold_total_durations = None
        self.transfer_durations = None

        # define some objectives (but do not apply them)
        self.total_cost = sum(
            [
                self.vessels.costs[m] * self.y[m, p]
                for m in range(self.M)
                for p in range(self.P)
            ]
        )
        self.total_hold_time = sum([self.z[n] for n in range(self.N)])
        self.used_volume = sum(
            [
                self.vessels.volumes[m]
                * sum([self.y[m, p] for p in range(self.P)])
                for m in range(self.M)
            ]
        )

    def _new_variable(self, *args, **kwargs):
        """
        Define and register a new multidimensional decision variable.
        """
        variable = LpVariableArray(*args, **kwargs)
        self.variables.add(variable)
        return variable

    def _buffers_dedicated_to_slots(self):
        """
        Constraint: A given buffer must always be made in the same slot.
        """
        for n in range(self.N):
            self.problem += sum([self.x[n, p] for p in range(self.P)]) == 1

    def _max_one_vessel_per_slot(self):
        """
        Constraint: A maximum of one vessel instance may inhabit a slot.
        """
        for p in range(self.P):
            self.problem += sum([self.y[m, p] for m in range(self.M)]) <= 1

    def _vessels_adequately_sized(self):
        """Constraint: Prep vessels must'nt be too big nor too small."""
        bv = self.buffers.volumes
        vv = self.vessels.volumes
        max_vol = self.vessels.max_volume
        mfr = self.parameters.minimum_fill_ratio
        for n in range(self.N):
            for p in range(self.P):
                self.problem += bv[n] * self.x[n, p] <= (
                    sum([vv[m] * self.y[m, p] for m in range(self.M)])
                )
                self.problem += bv[n] + max_vol - max_vol * self.x[n, p] >= (
                    mfr * sum([vv[m] * self.y[m, p] for m in range(self.M)])
                )

    def _limit_max_utilization(self):
        """
        Constraint: Each prep vessel utilization must be below a limit.
        """
        for p in range(self.P):
            self.problem += (
                sum([self.x[n, p] for n in range(self.N)])
                * self.parameters.prep_total_duration
                <= self.parameters.cycle_time
                * self.parameters.maximum_prep_utilization
            )

    def _limit_vessel_types(self):
        """Constraint: Limit the number of vessel types (sizes) used."""
        if self.parameters.max_types:
            for m in range(self.M):
                self.problem += (
                    self.b[m]
                    >= sum(self.y[m, p] for p in range(self.P)) / self.P
                )
                self.problem += (
                    sum([self.b[m] for m in range(self.M)])
                    <= self.parameters.max_types
                )

    def _hold_scheduling(self):
        """Constraint: Buffer hold procedures mustn't clash."""
        for n in range(self.N):
            self.problem += self.z[n] <= (
                self.parameters.cycle_time
                - self.parameters.hold_pre_duration
                - self.parameters.transfer_duration
                - self.parameters.hold_post_duration
                - self.buffers.use_durations[n]
            )

    def _prep_scheduling(self):
        """Constraint: Buffer prep procedures mustn't clash."""
        ct = self.parameters.cycle_time
        t_use = self.buffers.relative_use_start_times
        t_prep = self.parameters.prep_total_duration
        for n in range(self.N):
            # For each pair of distinct buffers, for each slot,
            # indicate if both buffers are prepared in the given slot
            for k in range(n + 1, self.N):
                for p in range(self.P):
                    self.problem += (
                        self.x[n, p] + self.x[k, p] - self.w[n, k, p] <= 1
                    )
                    self.problem += (
                        self.x[n, p] + self.x[k, p] >= 2 * self.w[n, k, p]
                    )
            # For each buffer, indicate if relative use start time
            # minus hold time is negative (defining q)
            self.problem += ct * self.q[n] - self.z[n] >= -t_use[n]
            self.problem += ct * self.q[n] - self.z[n] <= -t_use[n] + ct
            # For each buffer, indicate if lower bound of free time
            # window is greater than the cycle time (defining r)
            self.problem += (
                ct * self.r[n] - ct * self.q[n] + self.z[n]
                <= t_prep + t_use[n]
            )
            self.problem += (
                ct * self.r[n] - ct * self.q[n] + self.z[n]
                >= t_prep + t_use[n] - ct
            )
            # For each buffer, indicate if upper bound of free time
            # window is less than zero (defining s)
            self.problem += (
                ct * self.q[n] + ct * self.s[n] - self.z[n]
                >= t_prep - t_use[n]
            )
            self.problem += (
                ct * self.q[n] + ct * self.s[n] - self.z[n]
                <= t_prep - t_use[n] + ct
            )
            # For each buffer, indicate if free time window crosses
            # cycle boundary (u = r or s)
            self.problem += self.r[n] + self.s[n] - self.u[n] >= 0
            self.problem += self.r[n] + self.s[n] - 2 * self.u[n] <= 0
        # Each prep vessel can only do one thing at a time
        big_m = 2 * ct
        for n in range(self.N):
            for k in range(n + 1, self.N):
                self.problem += (
                    ct * self.q[k]
                    - ct * self.q[n]
                    - self.z[k]
                    + self.z[n]
                    + big_m * self.u[n]
                    + big_m * self.v[n, k]
                    - big_m * sum([self.w[n, k, p] for p in range(self.P)])
                    >= t_use[n] - t_use[k] + t_prep - big_m
                )
                self.problem += (
                    ct * self.q[k]
                    - ct * self.q[n]
                    - self.z[k]
                    + self.z[n]
                    - big_m * self.u[n]
                    + big_m * self.v[n, k]
                    + big_m * sum([self.w[n, k, p] for p in range(self.P)])
                    <= t_use[n] - t_use[k] - t_prep + 2 * big_m
                )
                self.problem += (
                    ct * self.q[k]
                    - ct * self.q[n]
                    - self.z[k]
                    + self.z[n]
                    - big_m * self.u[n]
                    + ct * self.s[n]
                    - big_m * sum([self.w[n, k, p] for p in range(self.P)])
                    >= t_use[n] - t_use[k] + t_prep - 2 * big_m
                )
                self.problem += (
                    ct * self.q[k]
                    - ct * self.q[n]
                    - self.z[k]
                    + self.z[n]
                    + big_m * self.u[n]
                    - ct * self.r[n]
                    + big_m * sum([self.w[n, k, p] for p in range(self.P)])
                    <= t_use[n] - t_use[k] - t_prep + 2 * big_m
                )

    def basic(self, do_solve=True):
        """
        Solve basic problem (no scheduling) to minimize cost.

        Parameters
        ----------
        do_solve: bool, optional
            If set to True (default), solves the problem upon
            construcion. Set this parameter to false to defer solution
            (useful if other constraints are to be applied before
            solving).

        Returns
        -------
        int
            If `do_solve` is set to True, returns problem status (see
            pulp.LpStatus).

        """
        self.problem += self.total_cost
        self._buffers_dedicated_to_slots()
        self._max_one_vessel_per_slot()
        self._vessels_adequately_sized()
        self._limit_max_utilization()
        self._limit_vessel_types()
        if do_solve:
            return self.problem.solve(self.solver)

    def complete(self, do_solve=True):
        """
        Solve complete problem (includes scheduling) to minimize cost.

        Parameters
        ----------
        do_solve: bool, optional
            If set to True (default), solves the problem upon
            construcion. Set this parameter to false to defer solution
            (useful ff other constraints are to be applied before
            solving).

        Returns
        -------
        int
            If `do_solve` is set to True, returns problem status (see
            pulp.LpStatus).

        """
        self.basic(do_solve=False)
        self._hold_scheduling()
        self._prep_scheduling()
        if do_solve:
            return self.problem.solve(self.solver)

    def minimized_hold_time(self):
        """
        Solve complete problem to first minimize vessel cost, then
        minimize hold times subject to the minimum cost.

        Returns
        -------
        int
            If `do_solve` is set to True, returns problem status (see
            pulp.LpStatus).

        """
        self.complete(do_solve=False)
        objectives = [self.total_cost, self.total_hold_time]
        absolute_tols = None  # might need to add these if failing
        relative_tols = None  # might need to add these if failing
        status = self.problem.sequentialSolve(
            objectives, absolute_tols, relative_tols, self.solver
        )
        return status[-1]

    def minimized_used_volume(self):
        """
        Solve complete problem to first minimize vessel cost, then
        minimize used preparation volume, subject to minimum cost,
        finally, minimize hold times, subject to minimal cost and
        minimal used preparation volume.

        Returns
        -------
        int
            If `do_solve` is set to True, returns problem status (see
            pulp.LpStatus).

        """
        self.complete(do_solve=False)
        objectives = [self.total_cost, self.used_volume, self.total_hold_time]
        absolute_tols = None  # might need to add these if failing
        relative_tols = None  # might need to add these if failing
        status = self.problem.sequentialSolve(
            objectives, absolute_tols, relative_tols, self.solver
        )
        return status[-1]

    def evaluate(self):
        """Generate some useful data from a solved problem."""
        if self.problem.status != 1:
            raise ValueError("No optimum solution found.")
        for variable in self.variables:
            variable.evaluate()
        # TODO: If these are just needed for e.g. plotting, might not bother
        # calculating all of them here???
        # TODO: Optimize 4 lines below - can this be done more easily?
        self.n_to_p = dict(numpy.argwhere(self.x.values))
        self.p_to_m = dict(numpy.fliplr(numpy.argwhere(self.y.values)))
        self.prep_slots = numpy.array([self.n_to_p[i] for i in range(self.N)])
        self.prep_vessels = numpy.array(
            [self.p_to_m[i] for i in self.prep_slots]
        )
        self.prep_start_times = (
            numpy.asarray(self.buffers.relative_use_start_times)
            - self.z.values
            - self.parameters.transfer_duration
            - self.parameters.prep_pre_duration
        ) % self.parameters.cycle_time
        self.hold_start_times = (
            numpy.asarray(self.buffers.relative_use_start_times)
            - self.z.values
            - self.parameters.transfer_duration
            - self.parameters.hold_pre_duration
        ) % self.parameters.cycle_time
        self.transfer_start_times = (
            self.prep_start_times + self.parameters.prep_pre_duration
        ) % self.parameters.cycle_time
        self.prep_total_durations = numpy.full(
            self.N, self.parameters.prep_total_duration
        )
        self.hold_total_durations = (
            self.parameters.hold_pre_duration
            + self.parameters.transfer_duration
            + self.z.values
            + numpy.asarray(self.buffers.use_durations)
            + self.parameters.hold_post_duration
        )
        self.transfer_durations = numpy.full(
            self.N, self.parameters.transfer_duration
        )

    def write(self, filename="untilperfect.lp"):
        """Write problem to file in .LP format.

        Parameters
        ----------
        filename: str, optional
            Output file name.
        """
        self.problem.writeLP(filename)

    def plot(self, filename="single_cycle_plot.pdf"):
        """
        Create a single-cycle steady-state equipment occupancy plot.

        Parameters
        ----------
        filename: str, optional
            Plot file name.

        """
        single_cycle_plot(self, filename)


# TODO: Make this a class method of the problem?
# TODO: Solver settings versus problem parameters - another class for
# settings?
# TODO: Create a class for BufferPrepProblem types - need to rigorously
# define the difference between data, problem, instance, problem type etc
# and come up with a definitive naming convention.
# TODO: Installed settings vs local settings vs runtime settings
# (implement a hierarchy of parameters).
def solve(
    parameters_file="parameters.ini",
    buffers_file="buffers.csv",
    vessels_file="vessels.csv",
    problem_type=BufferPrepProblem.complete,
    solver=None,
    plot=True,
    write=True,
    cli=False,
):
    """
    Solve BufferPrepProblem.

    Parameters
    ----------
    parameters_file : str, optional
        Parameters filename.
    buffers_file : str, optional
        Buffers filename.
    vessels_file : str, optional
        Vessels filename.
    problem_type : optional
        Type of problem to solve.
    solver : optional
        Solver to use; see pulp.LpSolver
    plot : bool, optional
        Generate steady-state single-cylce equipent occupancy plot and
        save to file.
    write : bool, optional
        Write the problem to file in .lp format.
    cli : bool, optional
        Set to True to return problem status, returns problem object
        otherwise.

    Returns
    -------
    int or pulp.LpProblem
        If `cli=True`, returns status (int, see pulp.LpStatus), if
        `cli=False`, returns pulp.LpProblem instance.

    """
    parameters = Parameters(parameters_file)
    buffers = Buffers(buffers_file)
    vessels = Vessels(vessels_file)
    problem = BufferPrepProblem(parameters, buffers, vessels, solver)
    status = problem_type(problem)
    problem.evaluate()
    if plot:
        problem.plot()
    if write:
        problem.write()
    counts = dict(enumerate(problem.y.values.sum(axis=1)))
    print("\nPreparation Vessels Required:")
    for index, count in counts.items():
        if count > 0:
            print("{}x\t{}".format(int(count), problem.vessels.names[index]))
    print("\nTotal cost: {}".format(pulp.value(problem.total_cost)))
    print("Total hold time: {}".format(pulp.value(problem.total_hold_time)))
    print("Total used volume: {}\n".format(pulp.value(problem.used_volume)))
    if cli:
        return status
    else:
        return problem


if __name__ == "__main__":
    # solve()
    pass
