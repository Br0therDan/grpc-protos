# gRPC Protos - MySingle Quant

Centralized gRPC proto file repository for MySingle Quant microservices platform.

## Quick Start

### Install Buf

```bash
brew install bufbuild/buf/buf
buf --version
```

### Generate Python Stubs

```bash
./scripts/generate-python.sh
```

### Validate Breaking Changes

```bash
./scripts/validate-breaking.sh
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

### Install from PyPI

```bash
pip install mysingle-protos
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
# 1. Update version in pyproject.toml
vim generated/python/pyproject.toml

# 2. Tag release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 3. GitHub Actions auto-publishes to PyPI
```

## CI/CD

GitHub Actions workflows:
- **validate-protos.yml**: Lint and breaking change detection on PRs
- **generate-clients.yml**: Auto-generate code on main branch
- **publish-package.yml**: Publish to PyPI on tag push

## Documentation

See [GRPC_PROTO_REPOSITORY_DESIGN.md](../docs/Inter-service-communications/GRPC_PROTO_REPOSITORY_DESIGN.md) for full design details.

## Current Status

✅ Repository structure created  
✅ Buf configuration in place  
✅ market_data_service.proto migrated  
⏳ Remaining services pending migration  

## Next Steps

1. Buf mod update (fetch google dependencies)
2. Fix lint warnings for market_data_service.proto
3. Generate initial Python package (v0.1.0-alpha)
4. Migrate remaining proto files
5. Set up GitHub Actions CI/CD

---

**Repository:** `grpc-protos`  
**Package Name:** `mysingle-protos`  
**Maintainer:** MySingle Quant Platform Team
