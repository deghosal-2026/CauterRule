#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing PyInstaller..."
pip install pyinstaller

echo "==> Building standalone binary..."
pyinstaller \
    --name cauterule \
    --onefile \
    --clean \
    --add-data "src/cauterule:src/cauterule" \
    --hidden-import cauterule.cli.app \
    src/cauterule/cli/app.py

echo "==> Binary built at dist/cauterule"
ls -lh dist/cauterule