# gRPC Protos - MySingle Quant

Centralized gRPC proto file repository for MySingle Quant microservices platform.

## Quick Start

### Install Buf

```bash
brew install bufbuild/buf/buf
buf --version
```

### Install Package from GitHub

```bash
# Latest from main branch
pip install git+https://github.com/Br0therDan/grpc-protos.git@main

# Specific tagged version (recommended)
pip install git+https://github.com/Br0therDan/grpc-protos.git@v1.0.0
```

## Repository Structure

```
grpc-protos/
├── protos/                       # Proto definitions
│   ├── common/                   # Shared types
│   ├── services/                 # Service-specific protos
│   │   ├── market_data/v1/
│   │   ├── strategy/v1/
│   │   ├── indicator/v1/
│   │   ├── genai/v1/
│   │   ├── ml/v1/
│   │   └── backtest/v1/
│   └── third_party/              # External dependencies
├── scripts/                      # Build and publish scripts
├── generated/                    # Generated code (gitignored)
└── buf.yaml                      # Buf configuration
```

## Package Usage

### Install from GitHub

```bash
# In your service's requirements.txt
mysingle-protos @ git+https://github.com/Br0therDan/grpc-protos.git@v1.0.0

# Or install directly
pip install git+https://github.com/Br0therDan/grpc-protos.git@v1.0.0
```

### Import in Services

```python
from mysingle_protos.services.market_data.v1 import market_data_service_pb2
from mysingle_protos.services.market_data.v1 import market_data_service_pb2_grpc
```

## Development Workflow

1. **Make Proto Changes**
   ```bash
   vim protos/services/market_data/v1/market_data_service.proto
   ```

2. **Lint**
   ```bash
   buf lint
   ```

3. **Check Breaking Changes**
   ```bash
   ./scripts/validate-breaking.sh
   ```

4. **Generate Code**
   ```bash
   ./scripts/generate-python.sh
   ```

5. **Test Locally**
   ```bash
   cd generated/python
   pytest tests/
   ```

6. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat(market_data): add new RPC method"
   git push origin main
   ```

## Release Process

### Semantic Versioning

- **MAJOR**: Breaking changes (v1.0.0 → v2.0.0)
- **MINOR**: New features (v1.0.0 → v1.1.0)
- **PATCH**: Bug fixes, docs (v1.0.0 → v1.0.1)

### Publish New Version

```bash
# 1. Update version in pyproject.toml and generate code
./scripts/publish-release.sh 1.0.0

# This will:
# - Update version in pyproject.toml
# - Generate Python stubs
# - Commit changes
# - Create and push git tag v1.0.0
```

### Update Services

```bash
# Update requirements.txt or pyproject.toml
mysingle-protos @ git+https://github.com/Br0therDan/grpc-protos.git@v1.0.0

# Reinstall
pip install --upgrade --force-reinstall -r requirements.txt
```

## CI/CD

GitHub Actions workflows:
- **validate-protos.yml**: Lint and breaking change detection on PRs
- **auto-generate.yml**: Auto-generate and commit code on main branch
- No PyPI publishing needed - services install directly from GitHub tags

## Documentation

See [GRPC_PROTO_REPOSITORY_DESIGN.md](../docs/Inter-service-communications/GRPC_PROTO_REPOSITORY_DESIGN.md) for full design details.

## Current Status

✅ Repository structure created  
✅ Buf configuration in place  
✅ market_data_service.proto migrated  
⏳ Remaining services pending migration  

## Next Steps

1. ✅ Buf configuration complete
2. ✅ market_data_service.proto migrated
3. ⏳ Migrate remaining proto files
4. ⏳ Fix lint warnings
5. ⏳ Generate initial Python package (v0.1.0)
6. ⏳ Set up GitHub Actions CI/CD
7. ⏳ Create first GitHub release tag

---

**Repository:** `grpc-protos`  
**Package Name:** `mysingle-protos`  
**Maintainer:** MySingle Quant Platform Team
