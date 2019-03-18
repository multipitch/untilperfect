untilperfect
====================================

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
.. image:: https://img.shields.io/badge/python-3.7-blue.svg
    :target: https://www.python.org/downloads/release/python-370/
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

The unt\ **ilp**\ erfect application solves the buffer preparation
vessel sizing and assignment problem using mixed **i**\ nteger
**l**\ inear **p**\ rogramming.

Forked from https://github.com/multipitch/dissertation.
The above repo was created for my masters dissertation on the subject
towards an MSc in Business Analytics from University College Dublin.
Further development has been forked here so that the dissertation repo
remains frozen.

Licensed under the MIT License. © Sean Tully 2018-2019.

Install from Wheel
------------------
Works on \*nix and Windows.
Requires python >=3.7.0
Other dependencies automatically installed.

First, generate a binary distribution (wheel) file.

::

    $ pip install untilperfect-*-py3-none-any.whl

Use
---
Run from the command line (displays help)
::

    $ untilperfect --help

Install from source
-------------------
For \*nix only.
Requires python, git, make.
Other dependencies automatically installed.
::

    $ mkdir -p ~/git/untilperfect
    $ git clone https://github.com/multipitch/untilperfect.git ~/git/untilperfect
    $ cd ~/git/untilperfect
    $ make install

Install from Source (developer)
-------------------------------

Install using pip in editable mode in a virtual environment.
For \*nix only.
Requires python, git, make, pyenv, virtualenv, virtualenvwrapper.
Other dependencies automatically installed.
::

    $ mkdir -p ~/git/untilperfect
    $ git clone https://github.com/multipitch/untilperfect.git ~/git/untilperfect
    $ pyenv install 3.7.0
    $ mkvirtualenv -a ~/git/untilperfect -p ~/.pyenv/versions/3.7.0/bin/python untilperfect
    $ make develop
