PYTHON = python
LINT_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

MAP ?= maps/challenger/01_the_impossible_dream.txt

.PHONY: all install run debug clean lint

all: run

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) main.py $(MAP)

debug:
	$(PYTHON) -m pdb main.py $(MAP)

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache *.pyc
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

lint:
	flake8 .
	mypy . $(LINT_FLAGS)