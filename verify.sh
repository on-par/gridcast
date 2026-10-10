#!/usr/bin/env bash
# Run the same four gates CI runs. Stops at the first failure.
set -euo pipefail

uv run ruff check
uv run ruff format --check
uv run pyright
uv run pytest
