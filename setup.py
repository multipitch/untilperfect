"""
setup.py

Setup
"""

import setuptools

with open("README.rst", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="untilperfect",
    version="0.0.1",
    author="Sean Tully",
    author_email="sean.tully@ucdconnect.ie",
    description=(
        "Solves the buffer preparation vessel sizing and assignment "
        "problem using mixed integer linear programming."
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    url="https://github.com/multipitch/untilperfect",
    packages=setuptools.find_packages(exclude=["untilperfect.stale"]),
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
    extras_require={"dev": ["black", "pylint", "sphinx", "numpydoc"]},
)
