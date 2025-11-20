#!/bin/bash
set -e

echo "🔍 Checking for breaking changes..."

# Compare against main branch
if buf breaking --against '.git#branch=main'; then
  echo "✅ No breaking changes detected"
  exit 0
else
  echo "⚠️  Breaking changes detected!"
  echo "This requires a MAJOR version bump (e.g., 1.0.0 → 2.0.0)"
  exit 1
fi
