.ONESHELL:
.DEFAULT_GOAL:=help
SHELL:=/bin/bash
PACKAGE_TARGET:=src/road_to_the_sea_scraper

UV := uv
RUN := $(UV) run --group dev

RUFF := $(RUN) ruff
MYPY := $(RUN) mypy
PYTEST := $(RUN) pytest
BASEDPYRITE := $(RUN) basedpyright
MKDOCS := $(RUN) mkdocs
TYPOS := $(RUN) typos

SRC_DIR := src
TEST_DIR := tests

install:
	$(UV) sync --group dev

# ==== Helpers =========================================================================================================
.PHONY: confirm
confirm:  ## Don't use this directly
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]


.PHONY: help
help:  ## Show help message
	@awk 'BEGIN {FS = ": .*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% 0-9a-zA-Z_\/-]+(\\:[$$()% 0-9a-zA-Z_\/-]+)*:.*?##/ { gsub(/\\:/,":", $$1); printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


.PHONY: clean
clean:  ## Clean up build artifacts and other junk
	@rm -rf .venv
	@uv run pyclean . --debris
	@rm -rf dist
	@rm -rf .ruff_cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -f .coverage*
	@rm -f .junit.xml


# ==== Quality Control =================================================================================================
.PHONY: qa/test
qa: qa/full  ## Shortcut for qa/full


.PHONY: qa/test
qa/test:  ## Run the tests
	$(PYTEST) $(TEST_DIR)


.PHONY: qa/types
qa/types:  ## Run static type checks
	$(MYPY) ${PACKAGE_TARGET} tests --pretty
	$(BASEDPYRITE) ${PACKAGE_TARGET} tests


.PHONY: qa/lint
qa/lint:  ## Run linters
	$(RUFF) check ${PACKAGE_TARGET} tests
	$(TYPOS) ${PACKAGE_TARGET} tests


.PHONY: qa/full
qa/full: qa/format qa/test qa/lint qa/types  ## Run the full set of quality checks
	@echo "All quality checks pass!"


.PHONY: qa/format
qa/format:  # Run code formatters
	$(RUFF) format ${PACKAGE_TARGET} tests
	$(RUFF) check --select I --fix ${PACKAGE_TARGET} tests


# ==== Documentation ===================================================================================================
.PHONY: docs
docs: docs/serve  ## Shortcut for docs/serve


.PHONY: docs/build
docs/build:  ## Build the documentation
	$(MKDOCS) build --config-file=docs/mkdocs.yaml


.PHONY: docs/serve
docs/serve:  ## Build the docs and start a local dev server
	$(MKDOCS) serve --config-file=docs/mkdocs.yaml --dev-addr=localhost:10000


# ==== Other Commands ==================================================================================================
.PHONY: publish
publish: confirm
	@if [[ "$$(git rev-parse --abbrev-ref HEAD)" != "main" ]] then \
		echo "You must be on the main branch to publish." && exit 1; \
	fi
	@git tag v$$(uv version --short) && git push origin v$$(uv version --short)
