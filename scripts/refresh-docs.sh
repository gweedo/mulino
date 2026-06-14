#!/usr/bin/env bash
#
# refresh-docs.sh — sanity-check and regenerate the tracked docs/ tree.
#
# Run at MILESTONES (after the backend is complete, after the frontend is
# complete, and before any release) rather than on every PR. With no source
# changes this script produces no diff — it is idempotent.
#
# Usage: bash scripts/refresh-docs.sh
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS="$ROOT/docs"

expected=(
  "README.md"
  "architecture.md"
  "domain-model.md"
  "roadmap.md"
  "development.md"
  "ci.md"
)

missing=0
for f in "${expected[@]}"; do
  if [[ ! -f "$DOCS/$f" ]]; then
    echo "MISSING: docs/$f"
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo "One or more docs are missing. Recreate them before continuing." >&2
  exit 1
fi

echo "All expected docs present:"
printf '  docs/%s\n' "${expected[@]}"

# Surface recent commits so a maintainer can verify docs/roadmap.md is current.
echo
echo "Most recent commits (verify docs/roadmap.md matches):"
git -C "$ROOT" log --oneline -10

echo
echo "refresh-docs: ok"
