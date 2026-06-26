# groundedwork — developer tasks
# `make test` runs everything: both language suites + cross-language parity.

.PHONY: help test test-py test-ts parity golden install clean

help:
	@echo "groundedwork developer tasks:"
	@echo "  make install   install Python (editable) + TS deps"
	@echo "  make test      run EVERYTHING: python + typescript + parity"
	@echo "  make test-py   python unit suite only"
	@echo "  make test-ts   typescript unit suite only"
	@echo "  make parity    cross-language parity check (vs golden.json)"
	@echo "  make golden    regenerate the parity golden snapshot"
	@echo "  make clean     remove build/test artifacts"

install:
	cd python && pip install -e ".[dev]"
	cd ts && npm install

test: test-py test-ts parity
	@echo ""
	@echo "✅ all suites passed (python + typescript + cross-language parity)"

test-py:
	@echo "── python ──────────────────────────────"
	cd python && python -m pytest -q

test-ts:
	@echo "── typescript ──────────────────────────"
	cd ts && npm test --silent

parity:
	@echo "── cross-language parity ───────────────"
	python bench/parity.py

golden:
	python bench/parity.py --update

clean:
	rm -rf python/dist python/build python/*.egg-info python/.pytest_cache
	rm -rf ts/dist ts/node_modules
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
