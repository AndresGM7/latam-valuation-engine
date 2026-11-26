#!/usr/bin/env bash
# Build check for the latam-valuation-engine CANVAS wizard frontend.
# Usage:   ./build_check.sh
# Exits 0 on success, non-zero otherwise.

set -euo pipefail

# Run from the script's directory regardless of where it is invoked.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[build_check] node:  $(node --version)"
echo "[build_check] npm:   $(npm --version)"
echo "[build_check] cwd:   $SCRIPT_DIR"

echo "[build_check] Step 1/3 — npm install"
npm install --no-audit --no-fund

echo "[build_check] Step 2/3 — typecheck"
npm run typecheck

echo "[build_check] Step 3/3 — build"
npm run build

echo "[build_check] OK — dist/ produced"
ls -la dist
