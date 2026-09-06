#!/usr/bin/env bash
set -euo pipefail

echo "==> Building source distribution and wheel..."
python -m build

echo "==> Uploading to PyPI..."
twine upload dist/*

echo "==> Done."