.DEFAULT_GOAL := lint

package_dir := aioplatega
tests_dir := tests
code_dir := $(package_dir) $(tests_dir)
reports_dir := reports

# =================================================================================================
# Environment
# =================================================================================================

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]'`
	rm -f `find . -type f -name '*~'`
	rm -f `find . -type f -name '.*~'`
	rm -rf `find . -name .pytest_cache`
	rm -rf *.egg-info
	rm -f .coverage
	rm -rf {build,dist,site,.cache,.mypy_cache,.ruff_cache,reports,docs/_build}

.PHONY: install
install: clean
	uv sync --group dev --group test --group docs
	uv run pre-commit install

# =================================================================================================
# Code quality
# =================================================================================================

.PHONY: lint
lint:
	uv run ruff format --check --diff $(code_dir)
	uv run ruff check --show-fixes $(code_dir)
	uv run mypy $(code_dir)

.PHONY: reformat
reformat:
	uv run ruff format $(code_dir)
	uv run ruff check --fix $(code_dir)

# =================================================================================================
# Tests
# =================================================================================================

.PHONY: test
test:
	uv run pytest --cov=$(package_dir) --cov-report=term-missing

.PHONY: test-coverage
test-coverage:
	mkdir -p $(reports_dir)/tests/
	uv run pytest --cov=$(package_dir) --cov-report=html:$(reports_dir)/coverage --cov-report=term-missing

.PHONY: test-coverage-view
test-coverage-view:
	uv run python -c "import webbrowser; webbrowser.open('file://$(shell pwd)/reports/coverage/index.html')"

# =================================================================================================
# Project
# =================================================================================================

.PHONY: build
build: clean
	uv build

.PHONY: bump
bump:
	uv version --bump $(args)

# Normally you want the Release workflow instead (Actions -> Release -> Run),
# which bumps, runs the gate, tags, publishes and drafts the notes in one go.
# This target is the manual fallback; pushing the tag triggers publish.yml.
.PHONY: release
release:
	git add pyproject.toml uv.lock
	git commit -m "Release $(shell uv version --short)"
	git tag -a v$(shell uv version --short) -m "Release $(shell uv version --short)"

# =================================================================================================
# Documentation
# =================================================================================================

.PHONY: docs-serve
docs-serve:
	uv run sphinx-autobuild docs docs/_build/html --port 8000

.PHONY: docs-build
docs-build:
	uv run sphinx-build -b html docs docs/_build/html
