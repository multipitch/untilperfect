# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.0.2] - 2019-03-26
### Added 
- Explanatory comments in pylintrc.
- Code for explanatory plot reinstated from
  https://github.com/multipitch/dissertation.

### Changed
- Rewrite of README.rst
- setup.py and doc/conf.py reads version from __init__.py so version has a
  single source.
- Extensive rewrite of documentation.

### Fixed
- Fixed typo in cli.py.
- Preventedattempts to plot when basic problem is run.

### Removed
- Use of numpydoc in documentation - reverted to sphinx.ext.napoleon.
- Excluded doc/conf.py from linting with pylint.
- Removed disabling of TODO warnings in pylintrc

## [0.0.1] - 2019-03-18
### Added
- Initial commit.

### Changed

### Deprecated

### Removed

### Fixed

### Security