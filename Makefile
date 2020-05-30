.DEFAULT_GOAL := help
.PHONY: clean pep257 pep8 mypy build install

PYTHON          := python
PEP257          := pep257
PEP8            := flake8
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

pep257:
	$(PEP257) semaphore examples

pep8:
	$(PEP8) --statistics

mypy:
	$(MYPY) semaphore examples

build:
	$(PYTHON) -m $(PIP) install -r requirements.txt
	$(PYTHON) setup.py sdist bdist_wheel

install:
	$(PYTHON) -m $(PIP) install dist/semaphore-*.tar.gz

help:
	@echo "Available targets:"
	@echo "- clean       Clean up the source directory"
	@echo "- pep257      Check docstring style with pep257"
	@echo "- pep8        Check code style with flake8"
	@echo "- mypy        Check static typing with Mypy"
	@echo "- build       Build package"
	@echo "- install     Install package"
	@echo
	@echo "Available variables:"
	@echo "- PEP257      default: $(PEP257)"
	@echo "- PEP8        default: $(PEP8)"
	@echo "- MYPY        default: $(MYPY)"
	@echo "- PIP         default: $(PIP)"
