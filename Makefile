PY ?= python
SRC_DIR := src

.PHONY: help install test build-index run

help:
	@printf '%s\n' 'Targets: install, test, build-index, run'

install:
	$(PY) -m pip install -r $(SRC_DIR)/requirements.txt

test:
	cd $(SRC_DIR) && $(PY) -m unittest discover -s tests

build-index:
	cd $(SRC_DIR) && $(PY) main.py build-index

run:
	cd $(SRC_DIR) && $(PY) main.py
