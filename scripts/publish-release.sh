#!/bin/bash
set -e

VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Usage: ./scripts/publish-release.sh <version>"
  echo "Example: ./scripts/publish-release.sh 1.0.0"
  exit 1
fi

# Validate version format
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Version must be in format X.Y.Z"
  exit 1
fi

echo "📦 Publishing release v$VERSION"

# Update version in pyproject.toml
sed -i "" "s/^version = .*/version = \"$VERSION\"/" pyproject.toml

# Generate fresh code
buf generate --template buf.gen.yaml

# Commit generated code
git add generated/ pyproject.toml
git commit -m "chore(release): v$VERSION"

# Create and push tag
git tag -a "v$VERSION" -m "Release v$VERSION"
git push origin main
git push origin "v$VERSION"

echo "✅ Released v$VERSION to GitHub"
echo "Services can now install with:"
echo "  pip install git+https://github.com/Br0therDan/grpc-protos.git@v$VERSION"
