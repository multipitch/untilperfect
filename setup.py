"""
setup.py

Setup
"""

import codecs
import os
import re
import setuptools

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Read file."""
    with codecs.open(os.path.join(HERE, *parts), "r") as file_path:
        return file_path.read()


def find_version(*file_paths):
    """Finds version from file."""
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


LONG_DESCRIPTION = read("README.rst")


setuptools.setup(
    name="untilperfect",
    version=find_version("untilperfect", "__init__.py"),
    author="Sean Tully",
    author_email="sean.tully@ucdconnect.ie",
    description=(
        "Solves the buffer preparation vessel sizing and assignment "
        "problem using mixed integer linear programming."
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    url="https://github.com/multipitch/untilperfect",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
    ],
    entry_points={"console_scripts": ["untilperfect = untilperfect.cli:main"]},
    install_requires=[
        "matplotlib>=3.0.1",
        "numpy>=1.15.4",
        "PuLP>=1.6.9",
        "pylatexenc>=1.3",
    ],
    extras_require={
        "dev": ["black", "pylint", "sphinx", "sphinxcontrib-svg2pdfconverter"]
    },
)
