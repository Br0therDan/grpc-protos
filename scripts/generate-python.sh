#!/bin/bash
set -e

echo "🔧 Generating Python protobuf stubs..."

# Clean previous build
rm -rf generated/python/mysingle_protos

# Generate using Buf
buf generate --template buf.gen.yaml

# Install package in editable mode for testing
cd generated/python
pip install -e .

echo "✅ Python stubs generated successfully"
echo "📦 Package: mysingle-protos"
echo "🔍 Test import: python -c 'from mysingle_protos.services.market_data.v1 import market_data_service_pb2'"
