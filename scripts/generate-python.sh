#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROTO_DIR="$REPO_ROOT"
PYTHON_BIN="${PYTHON:-python3}"

NO_INSTALL=0
while [[ ${1:-} != "" ]]; do
	case "$1" in
		--no-install|--skip-install)
			NO_INSTALL=1; shift ;;
		-h|--help)
			echo "Usage: $(basename "$0") [--no-install]"; exit 0 ;;
		*) echo "Unknown arg: $1"; exit 2 ;;
	esac
done

echo "🔧 Generating Python protobuf stubs (cwd: $PROTO_DIR)..."

if ! command -v buf >/dev/null 2>&1; then
	echo "ERROR: 'buf' not found in PATH. Install buf: https://docs.buf.build/installation" >&2
	exit 2
fi

pushd "$PROTO_DIR" >/dev/null

if [[ ! -f "buf.gen.yaml" ]]; then
	echo "ERROR: buf.gen.yaml not found in $PROTO_DIR" >&2
	popd >/dev/null
	exit 2
fi

# Clean the default python output directory to avoid stale files.
rm -rf "$PROTO_DIR/generated/python/mysingle_protos" || true

echo "> Running: buf generate --template buf.gen.yaml"
buf generate --template buf.gen.yaml

if [[ -f "$SCRIPT_DIR/fix_imports.py" ]]; then
	echo "> Rewriting imports via scripts/fix_imports.py"
	"$PYTHON_BIN" "$SCRIPT_DIR/fix_imports.py"
fi

# Detect generated python output directory. Prefer the canonical
# generated/mysingle_protos layout but fall back to other known patterns.
PY_OUTPUT_DIR=""
if [[ -d "$PROTO_DIR/generated/mysingle_protos" ]]; then
	PY_OUTPUT_DIR="$PROTO_DIR/generated/mysingle_protos"
elif [[ -d "$PROTO_DIR/generated/python/mysingle_protos" ]]; then
	PY_OUTPUT_DIR="$PROTO_DIR/generated/python/mysingle_protos"
else
	for candidate in "$PROTO_DIR/generated"/*; do
		if [[ -d "$candidate" ]]; then
			if [[ -d "$candidate/protos" || -f "$candidate/setup.py" || -f "$candidate/pyproject.toml" ]]; then
				PY_OUTPUT_DIR="$candidate"
				break
			fi
		fi
	done
fi

if [[ -z "$PY_OUTPUT_DIR" ]]; then
	echo "ERROR: expected generated python output under $PROTO_DIR/generated (no suitable package found)" >&2
	ls -la "$PROTO_DIR/generated" >&2 || true
	popd >/dev/null
	exit 3
fi

if [[ $NO_INSTALL -eq 0 ]]; then
	echo "> Installing generated package (editable) using: $PYTHON_BIN -m pip install -e $PY_OUTPUT_DIR"

	if ! "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
		echo "> pip not found for $PYTHON_BIN — attempting to bootstrap via ensurepip"
		if "$PYTHON_BIN" -m ensurepip --upgrade >/dev/null 2>&1; then
			echo "> bootstrapped pip via ensurepip"
		else
			echo "> ensurepip failed — attempting to install/upgrade pip via get-pip"
			if "$PYTHON_BIN" -c "import urllib.request, sys" >/dev/null 2>&1; then
				"$PYTHON_BIN" - <<'PY'
import sys, subprocess, urllib.request
data = urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py').read()
subprocess.run([sys.executable, '-c', data], check=True)
PY
			else
				echo "ERROR: cannot bootstrap pip (network disabled). Please install pip in your venv." >&2
				popd >/dev/null
				exit 4
			fi
		fi
	fi

	"$PYTHON_BIN" -m pip install -U pip setuptools wheel

	if [[ ! -f "$PY_OUTPUT_DIR/setup.py" && ! -f "$PY_OUTPUT_DIR/pyproject.toml" ]]; then
		echo "> Creating minimal setup.py and __init__.py in $PY_OUTPUT_DIR for editable install"
		if [[ ! -f "$PY_OUTPUT_DIR/__init__.py" ]]; then
			printf "# auto-generated init\n" > "$PY_OUTPUT_DIR/__init__.py"
		fi

		cat > "$PY_OUTPUT_DIR/setup.py" <<'PYSETUP'
from pathlib import Path
from setuptools import find_packages, setup

package_root = Path(__file__).parent
packages = [pkg for pkg in find_packages(where=str(package_root)) if pkg.startswith('mysingle_protos')]

setup(
	name="mysingle_protos",
	version="0.0.0",
	packages=packages,
	package_dir={"": "."},
	include_package_data=True,
)
PYSETUP
	fi

	"$PYTHON_BIN" -m pip install -e "$PY_OUTPUT_DIR"

	echo "✅ Python stubs generated and installed (editable)."
	echo "📦 Package location: $PY_OUTPUT_DIR"
	echo "🔍 Quick import test: \n  $PYTHON_BIN -c \"from mysingle_protos.protos.services.backtest.v1 import backtest_service_pb2_grpc; print('import ok')\""
else
	echo "✅ Python stubs generated (installation skipped with --no-install)."
fi

popd >/dev/null

exit 0
