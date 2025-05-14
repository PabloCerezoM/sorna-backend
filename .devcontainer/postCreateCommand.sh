

#!/bin/bash
set -e

echo "[postCreateCommand] Installing dev dependencies..."
pip install --upgrade pip
pip install -e ".[dev]"

echo "[postCreateCommand] Cleaning up build artifacts..."
rm -rf *.egg-info build data

echo "[postCreateCommand] Installing pre-commit hooks..."
git config --unset core.hooksPath || true
pre-commit install

echo "[postCreateCommand] Done."