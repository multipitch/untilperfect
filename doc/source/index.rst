untilperfect
============

Introduction
------------

The unt\ **ilp**\ erfect application solves the buffer preparation
vessel sizing and assignment problem using mixed **i**\ nteger
**l**\ inear **p**\ rogramming.

The source repo is at https://github.com/multipitch/untilperfect.

Builds are hosted at https://pypi.org/project/untilperfect/.

Documentation is hosted at https://untilperfect.readthedocs.io/.

This project was forked from https://github.com/multipitch/dissertation.
The dissertation repo was created for my masters dissertation on the
subject towards an MSc in Business Analytics from University College
Dublin; further development has been forked here so that the
dissertation repo remains frozen.

Install via pip:
::

    $ pip install untilperfect

Provides the `untilperfect` CLI command
::

    $ untilperfect --help
    usage: model.py [-h] [-b BUFFERS] [-n] [-p PARAMETERS] [-f PATH] [-s SOLVER]
                    [-t PROBLEM_TYPE] [-v VESSELS] [-w]

    Solves the buffer preparation assignment and selection problem.

    optional arguments:
    -h, --help            show this help message and exit
    -b BUFFERS, --buffers BUFFERS
                          buffers filename (default: 'buffers.csv')
    -n, --no-plot         do not generate plot
    -p PARAMETERS, --parameters PARAMETERS
                          parameters filename (default: 'parameters.ini')
    -f PATH, --path PATH  file path (default: <current working directory>)
    -s SOLVER, --solver SOLVER
                          solver to be used (default: 'COIN_CMD')
    -t PROBLEM_TYPE, --problem-type PROBLEM_TYPE
                          specify model to solve (default: 'complete'), other
                          model options are 'basic', 'minimized_hold_time',
                          'mimimized_used_volume'
    -v VESSELS, --vessels VESSELS
                          vessel filename (default: vessels.csv)
    -w, --write           write problem to file in .lp format

Distributed under the MIT License.

© Sean Tully 2018-2019.

Contents
--------

.. toctree::
   :maxdepth: 2
   
   problem
   untilperfect


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
