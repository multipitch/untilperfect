import numpy
import pulp


class LpVariableArray:
    """Multidimensional decision variable array."""

    def __init__(
        self, name, dimensions, low_bound=None, up_bound=None, cat=None, e=None
    ):
        self.name = name
        try:
            iter(dimensions)
            self.dimensions = dimensions
        except TypeError:
            self.dimensions = (dimensions,)
        self.low_bound = low_bound
        self.up_bound = up_bound
        self.cat = cat
        self.e = e
        self.variables = self._build_variables_array()
        self.values = None

    def __getitem__(self, index):
        return self.variables[index]

    def _define_variable(self, *index):
        """Defines an individual decision variable."""
        name = "_".join(map(str, (self.name, *index)))
        return pulp.LpVariable(
            name, self.low_bound, self.up_bound, self.cat, self.e
        )

    def _build_variables_array(self):
        """Builds a multidimensional array of decision variables."""
        f = numpy.vectorize(self._define_variable)
        return numpy.fromfunction(f, self.dimensions, dtype="int")

    def evaluate(self):
        """Evaluates decision variable values."""
        f = numpy.vectorize(lambda i: pulp.value(i))
        self.values = f(self.variables)
