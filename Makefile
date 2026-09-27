# Flow repository convenience targets.
#
# The public CLI is ./flow. Keep this file as a thin wrapper so Make and the
# documented CLI cannot become independent build systems.

FLOW := ./flow

.PHONY: all help run compile mlir test test-stdlib repl install clean \
        sync-roadmap sync-roadmap-dry check-program

all: help

check-program:
	@if [ -z "$(PROGRAM)" ]; then \
		echo "PROGRAM is required, for example: make run PROGRAM=examples/basics/hello_world.flow" >&2; \
		exit 2; \
	fi

run: check-program
	$(FLOW) run "$(PROGRAM)"

compile: check-program
	$(FLOW) compile "$(PROGRAM)"

mlir: check-program
	$(FLOW) mlir "$(PROGRAM)"

# Use the repository compiler suite. --compiler selects the historical
# repository-wide test runner rather than project-mode testing.
test:
	$(FLOW) test --compiler --strict --tier2

# Kept as a compatibility alias. The canonical compiler suite already covers
# stdlib tests; maintain a single test contract rather than a second hand-made
# list here.
test-stdlib: test

repl:
	$(FLOW) repl

install:
	$(FLOW) install

clean:
	rm -rf build/

sync-roadmap:
	python3 scripts/sync_roadmap.py

sync-roadmap-dry:
	python3 scripts/sync_roadmap.py --dry-run

help:
	@echo "Flow repository convenience targets"
	@echo ""
	@echo "  make run PROGRAM=file.flow      -> ./flow run file.flow"
	@echo "  make compile PROGRAM=file.flow  -> ./flow compile file.flow"
	@echo "  make mlir PROGRAM=file.flow     -> ./flow mlir file.flow"
	@echo "  make test                       -> ./flow test --compiler --strict --tier2"
	@echo "  make test-stdlib                -> alias of make test"
	@echo "  make repl                       -> ./flow repl"
	@echo "  make install                    -> ./flow install"
	@echo "  make clean                      -> remove build/"
	@echo "  make sync-roadmap-dry           -> preview ROADMAP -> GitHub sync"
	@echo "  make sync-roadmap               -> apply ROADMAP -> GitHub sync"
