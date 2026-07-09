PYTHON ?= $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)
WALNUT := $(PYTHON) -m walnut.cli
ID ?= 3
TOPIC ?= arrays-and-hashing

.PHONY: setup install doctor topics list show pick test run verify unit smoke sync links notes tui

setup:
	./setup

install: setup

tui:
	$(WALNUT) tui

doctor:
	$(WALNUT) doctor

topics:
	$(WALNUT) topics

list:
	$(WALNUT) list $(TOPIC)

show:
	$(WALNUT) show $(ID)

pick:
	$(WALNUT) pick $(ID) --force

test:
	$(WALNUT) test $(ID) --perf

run:
	$(WALNUT) run $(ID) --perf

verify:
	$(WALNUT) verify --all

unit:
	$(PYTHON) -m unittest discover -s tests

smoke: unit verify doctor topics

sync:
	$(WALNUT) sync-roadmap

links:
	$(WALNUT) open-official $(ID) --site leetcode --print --plain
	$(WALNUT) open-official $(ID) --site neetcode --print --plain

notes:
	$(WALNUT) notes $(ID)
