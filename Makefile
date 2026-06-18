SRC   := kepler_isolation/src
TESTS := kepler_isolation/tests

.PHONY: fmt lint typecheck test check clean run tui install-dev help

# ── Default ───────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  KEPLER ISOLATION — developer targets"
	@echo ""
	@echo "  Code quality"
	@echo "    make fmt          reformat source with ruff (modifies files)"
	@echo "    make lint         lint + auto-fix with ruff (modifies files)"
	@echo "    make typecheck    static type check with pyright (read-only)"
	@echo "    make test         run the test suite with pytest"
	@echo "    make check        CI-safe: format-check + lint + typecheck + test"
	@echo ""
	@echo "  Housekeeping"
	@echo "    make clean        remove __pycache__, .pyc, build artifacts"
	@echo ""
	@echo "  Play"
	@echo "    make run          classic text mode"
	@echo "    make tui          Textual rich UI (needs: pip install textual)"
	@echo ""
	@echo "  Bootstrap"
	@echo "    make install-dev  pip-install all dev dependencies"
	@echo ""

# ── Code quality ──────────────────────────────────────────────────────────────
fmt:
	ruff format $(SRC) $(TESTS)

lint:
	ruff check --fix $(SRC) $(TESTS)

typecheck:
	pyright $(SRC)

test:
	pytest $(TESTS) -v

# CI-safe: fails loudly if formatting is off, never modifies files.
check:
	ruff format --check $(SRC) $(TESTS)
	ruff check $(SRC) $(TESTS)
	pyright $(SRC)
	pytest $(TESTS) -v

# ── Housekeeping ──────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache

# ── Play ──────────────────────────────────────────────────────────────────────
run:
	./play

tui:
	./play --tui

# ── Bootstrap ─────────────────────────────────────────────────────────────────
install-dev:
	pip install ruff pyright pytest textual
