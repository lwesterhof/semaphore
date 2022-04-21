.DEFAULT_GOAL := help
.PHONY: clean flake8 mypy build install

PYTHON          := python
FLAKE8          := flake8
MYPY            := mypy
PIP             := pip

clean:
	rm -rf build
	rm -rf dist
	rm -rf .mypy_cache
	rm -rf semaphore.egg-info
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find examples/tmp/ -name "*.png" -exec rm {} \;
	find examples/tmp/ -name "*.jpg" -exec rm {} \;

flake8:
	$(PYTHON) -m $(FLAKE8) --statistics

mypy:
	$(PYTHON) -m $(MYPY) semaphore examples

build:
	$(PYTHON) -m $(PIP) install .
	$(PYTHON) setup.py sdist bdist_wheel

install:
	$(PYTHON) -m $(PIP) install dist/semaphore-*.tar.gz

help:
	@echo "Available targets:"
	@echo "- clean       Clean up the source directory"
	@echo "- flake8      Check code style with flake8"
	@echo "- mypy        Check static typing with Mypy"
	@echo "- build       Build package"
	@echo "- install     Install package"
	@echo
	@echo "Available variables:"
	@echo "- PYTHON      default: $(PYTHON)"
	@echo "- FLAKE8      default: $(FLAKE8)"
	@echo "- MYPY        default: $(MYPY)"
	@echo "- PIP         default: $(PIP)"
