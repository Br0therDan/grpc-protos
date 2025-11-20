#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
  echo "Usage: ./publish-package.sh <version>"
  exit 1
fi

echo "📦 Publishing mysingle-protos v$VERSION..."

# Generate fresh code
buf generate --template buf.gen.yaml

# Build Python package
cd generated/python
python -m build

# Publish to PyPI
python -m twine upload dist/* --verbose

echo "✅ Published mysingle-protos v$VERSION to PyPI"
