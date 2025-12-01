# gRPC Protos - MySingle Quant

Centralized gRPC proto file repository for MySingle Quant microservices platform.

## 📚 Documentation

- **[RELEASE_PROCESS.md](./RELEASE_PROCESS.md)** - 표준 릴리스 프로세스 가이드 (필독!)
- **[Development Workflow](#development-workflow)** - Proto 파일 개발 및 배포 절차

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

### Standard Proto Change Procedure

#### 1. Create Feature Branch

```bash
git checkout -b feat/add-batch-get-strategies
# or
git checkout -b fix/correct-field-type
# or
git checkout -b breaking/rename-service-method
```

**Branch Naming Convention:**
- `feat/*`: New features (minor version bump)
- `fix/*`: Bug fixes (patch version bump)
- `breaking/*`: Breaking changes (major version bump)
- `docs/*`: Documentation only (patch version bump)

#### 2. Modify Proto Files

```bash
# Example: Add new RPC method
vim protos/services/strategy/v1/strategy_service.proto
```

**Best Practices:**
- Add fields, don't remove (use `reserved` for deleted fields)
- Use optional for new fields in existing messages
- Document all fields with comments
- Follow naming conventions (snake_case for fields, PascalCase for messages)

**Example - Adding New RPC:**
```protobuf
service StrategyService {
  rpc GetStrategy(GetStrategyRequest) returns (GetStrategyResponse);
  
  // New method - backward compatible
  rpc BatchGetStrategies(BatchGetStrategiesRequest) returns (stream StrategyResponse);
}

message BatchGetStrategiesRequest {
  repeated string strategy_ids = 1;
  string user_id = 2;
}
```

**Example - Adding Optional Field:**
```protobuf
message StrategyResponse {
  string id = 1;
  string name = 2;
  // New optional field - backward compatible
  optional google.protobuf.Timestamp last_updated = 3;
}
```

#### 3. Validation & Quality Checks

```bash
# Format proto files (auto-fix)
buf format -w

# Lint for style issues
buf lint

# Check for breaking changes against main
buf breaking --against '.git#branch=main'

# If breaking changes detected, verify they're intentional
# and document in PR description
```

**Common Lint Issues:**
- Missing field comments
- Incorrect naming convention
- Missing package declaration
- Incorrect import paths

#### 4. Generate Python Stubs (Local Test)

```bash
# Generate stubs to verify compilation
./scripts/generate-python.sh

# Check generated files
ls -la generated/mysingle_protos/protos/services/strategy/v1/
```

#### 5. Test Generated Code

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .

# Test imports
python -c "from mysingle_protos.protos.services.strategy.v1 import strategy_service_pb2; print('OK')"
```

#### 6. Commit Changes

```bash
git add protos/
git commit -m "feat(strategy): add BatchGetStrategies RPC method

- Add streaming RPC for batch strategy retrieval
- Add BatchGetStrategiesRequest message
- Backward compatible change (minor version bump)

Affected services: backtest-service, genai-service"

git push origin feat/add-batch-get-strategies
```

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

- **type**: feat, fix, breaking, docs, chore
- **scope**: service name (strategy, market_data, indicator, etc.)
- **subject**: Brief description
- **body**: Detailed explanation, rationale
- **footer**: Affected services, breaking change notes

#### 7. Create Pull Request

**PR Title:** Same as commit subject  
**PR Description Template:**

```markdown
## Changes
- Add BatchGetStrategies RPC method
- Add BatchGetStrategiesRequest/Response messages

## Affected Services
- backtest-service (needs client update)
- genai-service (needs client update)

## Breaking Changes
- [ ] No breaking changes
- [x] Breaking changes (describe below)

## Versioning
- [ ] Patch (0.0.X) - Bug fix
- [x] Minor (0.X.0) - New feature
- [ ] Major (X.0.0) - Breaking change

## Checklist
- [x] Buf lint passes
- [x] Breaking change check passes (or documented)
- [x] Python stubs generate successfully
- [x] Imports tested locally
- [x] Affected services documented
```

#### 8. CI Validation (Automatic)

GitHub Actions will automatically:
- ✅ Run `buf lint`
- ✅ Run `buf breaking` check
- ✅ Generate Python stubs
- ✅ Test package installation
- ✅ Validate all imports

**If CI fails:**
- Review error messages
- Fix issues locally
- Push updates to same branch (CI re-runs)

#### 9. Review & Merge

**Review Checklist:**
- [ ] Proto changes follow conventions
- [ ] Backward compatibility maintained (or breaking change justified)
- [ ] All affected services identified
- [ ] Documentation updated
- [ ] CI passes

**After approval:**
- Merge to `main` branch (squash or merge commit)
- Delete feature branch

#### 10. Automatic Release (Post-Merge)

GitHub Action automatically:
1. Detects version bump type from commit message
2. Updates version in `pyproject.toml`
3. Generates Python stubs
4. Commits generated code
5. Creates git tag (e.g., `v1.1.0`)
6. Publishes GitHub release with changelog

## Release Process

### Semantic Versioning Rules

**Version Format:** `MAJOR.MINOR.PATCH` (e.g., `v1.2.3`)

| Version   | When to Bump                     | Examples                                          |
| --------- | -------------------------------- | ------------------------------------------------- |
| **MAJOR** | Breaking changes                 | Remove fields, rename methods, change field types |
| **MINOR** | New backward-compatible features | Add RPC methods, add optional fields              |
| **PATCH** | Bug fixes, documentation         | Fix field numbers, update comments                |

### Automatic Release (Recommended)

**Triggered by:** Merge to `main` branch

**GitHub Action Workflow:**
1. Analyzes commit messages for version bump type
2. Updates `pyproject.toml` version
3. Generates Python stubs via Buf
4. Commits generated code
5. Creates git tag (e.g., `v1.1.0`)
6. Publishes GitHub Release with auto-generated changelog

**Commit Message Keywords:**
- `feat:` or `feat(scope):` → Minor version bump
- `fix:` or `fix(scope):` → Patch version bump
- `breaking:` or `BREAKING CHANGE:` in footer → Major version bump

**Example:**
```bash
git commit -m "feat(strategy): add BatchGetStrategies RPC

BREAKING CHANGE: Renamed GetStrategy to GetSingleStrategy"
# Result: v1.0.0 → v2.0.0 (major bump due to breaking change)
```

### Manual Release (Alternative)

**Use when:** Need explicit version control or hotfix

```bash
# 1. Update version and generate code
./scripts/publish-release.sh 1.2.0 "Add indicator metadata RPC"

# This will:
# - Update version in pyproject.toml to 1.2.0
# - Run buf generate for Python stubs
# - Commit changes with message
# - Create and push git tag v1.2.0
# - Trigger GitHub release creation
```

### Verify Release

```bash
# Check latest release
git tag --sort=-v:refname | head -n 1

# View release on GitHub
open https://github.com/Br0therDan/grpc-protos/releases

# Test installation
pip install git+https://github.com/Br0therDan/grpc-protos.git@v1.2.0
python -c "import mysingle_protos; print(mysingle_protos.__version__)"
```

---

## Service Integration Guide

### Update Service Dependencies

**Step 1: Update Dependency Version**

```toml
# pyproject.toml
[project]
dependencies = [
    "mysingle-protos @ git+https://github.com/Br0therDan/grpc-protos.git@v2.0.1",
]
```

**Or in requirements.txt:**
```txt
mysingle-protos @ git+https://github.com/Br0therDan/grpc-protos.git@v1.2.0
```

**Step 2: Reinstall Package**

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install --upgrade --force-reinstall -r requirements.txt
```

**Step 3: Verify Installation**

```bash
pip show mysingle-protos
# Check version matches expected tag

python -c "from mysingle_protos.protos.services.strategy.v1 import strategy_service_pb2; print('OK')"
```

### Implement Proto Changes

#### For gRPC Server (Servicer Implementation)

```python
# app/servicers/strategy_servicer.py
from mysingle_protos.protos.services.strategy.v1 import strategy_service_pb2
from mysingle_protos.protos.services.strategy.v1 import strategy_service_pb2_grpc

class StrategyServicer(strategy_service_pb2_grpc.StrategyServiceServicer):
    # Implement new RPC method
    async def BatchGetStrategies(
        self,
        request: strategy_service_pb2.BatchGetStrategiesRequest,
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[strategy_service_pb2.StrategyResponse]:
        for strategy_id in request.strategy_ids:
            strategy = await self._get_strategy(strategy_id, request.user_id)
            yield strategy_service_pb2.StrategyResponse(
                id=strategy.id,
                name=strategy.name,
                # ... other fields
            )
```

#### For gRPC Client

```python
# app/clients/strategy_client.py
from mysingle.clients import BaseGrpcClient
from mysingle_protos.protos.services.strategy.v1 import strategy_service_pb2
from mysingle_protos.protos.services.strategy.v1 import strategy_service_pb2_grpc

class StrategyGrpcClient(BaseGrpcClient):
    def __init__(self, user_id=None, correlation_id=None, **kwargs):
        super().__init__(
            service_name="strategy-service",
            default_port=50051,
            user_id=user_id,
            correlation_id=correlation_id,
            **kwargs
        )
        self.stub = strategy_service_pb2_grpc.StrategyServiceStub(self.channel)

    async def batch_get_strategies(self, strategy_ids: list[str]) -> list[dict]:
        request = strategy_service_pb2.BatchGetStrategiesRequest(
            strategy_ids=strategy_ids,
            user_id=self.user_id or "",
        )
        
        results = []
        async for response in self.stub.BatchGetStrategies(
            request,
            metadata=self.metadata,
        ):
            results.append({
                "id": response.id,
                "name": response.name,
                # ... other fields
            })
        return results
```

### Testing Proto Changes

```bash
# Run gRPC-specific tests
uv run pytest tests/grpc/ -v

# Test end-to-end
uv run pytest tests/integration/test_strategy_grpc.py -v
```

### Handling Breaking Changes

**Strategy 1: Feature Flags (Recommended)**

```python
# app/core/config.py
class Settings(CommonSettings):
    USE_STRATEGY_V2_API: bool = False  # Feature flag

# app/clients/strategy_client.py
class StrategyGrpcClient(BaseGrpcClient):
    async def get_strategy(self, strategy_id: str) -> dict:
        if self.settings.USE_STRATEGY_V2_API:
            # Use new proto version
            response = await self.stub.GetSingleStrategy(request)
        else:
            # Fallback to old version
            response = await self.stub.GetStrategy(request)
        return response
```

**Deployment Steps:**
1. Deploy services with feature flag OFF (use old proto)
2. Gradually enable feature flag per service
3. Monitor for errors
4. Once all services migrated, remove fallback code

**Strategy 2: Blue-Green Deployment**

1. Deploy new service version (Blue) alongside old (Green)
2. Route 10% traffic to Blue
3. Monitor metrics
4. Gradually increase to 100%
5. Decommission Green

### Multi-Service Coordination

**When proto change affects multiple services:**

1. **Identify Dependencies:**
   - Strategy Service (server) ← Backtest Service (client)
   - Strategy Service (server) ← GenAI Service (client)

2. **Deployment Order:**
   - Deploy Strategy Service (server) first with backward compatibility
   - Deploy Backtest Service (client)
   - Deploy GenAI Service (client)
   - Remove backward compatibility code from Strategy Service

3. **Communication:**
   - Document in proto PR which services are affected
   - Coordinate deployment in team chat
   - Use feature flags for gradual rollout

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
