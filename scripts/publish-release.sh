#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  echo "Usage: ./scripts/publish-release.sh <version>" >&2
  echo "Example: ./scripts/publish-release.sh 1.0.0" >&2
  exit 1
fi

if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Version must be in format X.Y.Z" >&2
  exit 1
fi

cd "$REPO_ROOT"

ensure_clean_tree() {
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "Error: working tree is not clean. Commit or stash changes before releasing." >&2
    exit 1
  fi
}

ensure_tag_absent() {
  if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "Error: tag v$VERSION already exists" >&2
    exit 1
  fi
}

run_with_retry() {
  local attempts=${RETRY_ATTEMPTS:-3}
  local delay=${RETRY_DELAY_SECONDS:-5}
  local attempt=1
  while true; do
    if "$@"; then
      return 0
    fi
    if (( attempt >= attempts )); then
      echo "ERROR: command '$*' failed after $attempts attempts" >&2
      return 1
    fi
    echo "Command '$*' failed (attempt $attempt/$attempts). Retrying in ${delay}s..." >&2
    sleep "$delay"
    attempt=$((attempt + 1))
    delay=$((delay * 2))
  done
}

update_version() {
  python3 - <<PY
from pathlib import Path
import re

path = Path("pyproject.toml")
text = path.read_text()
pattern = r'^version = "[^"]+"'
replacement = 'version = "${VERSION}"'
new_text, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)
if count != 1:
  raise SystemExit("Could not update version line in pyproject.toml")
path.write_text(new_text)
PY
}

echo "📦 Publishing release v$VERSION"

ensure_clean_tree
ensure_tag_absent
update_version

echo "🔍 Running buf lint & breaking checks"
buf lint
buf breaking --against '.git#branch=main'

echo "🛠️ Regenerating stubs via scripts/generate-python.sh"
run_with_retry "$SCRIPT_DIR/generate-python.sh" --no-install

git add generated/ pyproject.toml

git commit -m "chore(release): v$VERSION"

git tag -a "v$VERSION" -m "Release v$VERSION"

git push origin HEAD
git push origin "v$VERSION"

echo "✅ Released v$VERSION to GitHub"
echo "Services can now install with:"
echo "  pip install git+https://github.com/Br0therDan/grpc-protos.git@v$VERSION"
