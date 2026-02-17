.DEFAULT_GOAL := lint

package_dir := aioplatega
tests_dir := tests
scripts_dir := scripts
code_dir := $(package_dir) $(tests_dir) $(scripts_dir)
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
	uv run ruff format --check --diff $(package_dir)
	uv run ruff check --show-fixes $(package_dir)
	uv run mypy $(package_dir)

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
	uv run python scripts/bump_version.py $(args)

.PHONY: release
release:
	git add .
	git commit -m "Release $(shell uv run python -c 'from aioplatega import __version__; print(__version__)')"
	git tag v$(shell uv run python -c 'from aioplatega import __version__; print(__version__)')

# =================================================================================================
# Documentation
# =================================================================================================

.PHONY: docs-serve
docs-serve:
	uv run sphinx-autobuild docs docs/_build/html --port 8000

.PHONY: docs-build
docs-build:
	uv run sphinx-build -b html docs docs/_build/html
