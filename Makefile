help:
	@echo "wheel       - Make wheel (binary distribution)"
	@echo "sdist       - Make source distribution"
	@echo "install     - Install using pip"
	@echo "clean       - Remove cached files"
	@echo "cleanall    - Remove cached files, build files and installation"
	@echo "develop     - Install in editable mode"

.PHONY: wheel
wheel: clean
	python setup.py bdist_wheel

.PHONY: sdist
sdist: clean
	python setup.py sdist

.PHONY: install
install: wheel
	pip install .

.PHONY: clean
clean:
	find . -name '*.pyc' -delete
	find ./examples/ -name '*.pdf' -delete
	find ./examples/ -name '*.lp' -delete
	find . -name '__pycache__' -type d | xargs rm -fr

.PHONY: cleanall
cleanall: clean
	pip uninstall -y untilperfect
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info

.PHONY: develop
develop: wheel
	pip install --editable .[dev]