# gRPC Protos Release Process

## 📋 표준 릴리스 프로세스 (Standard Release Process)

### 전제 조건 (Prerequisites)

- Buf CLI 설치 완료
- GitHub 저장소에 대한 write 권한
- 로컬 환경에서 proto 파일 변경 완료

---

## 🔄 릴리스 절차 (Step-by-Step)

### 1️⃣ Proto 파일 검증 (Validation)

```bash
cd grpc-protos/

# 1. 자동 포맷팅
buf format -w

# 2. Lint 검사
buf lint

# 3. Breaking change 체크
buf breaking --against '.git#branch=main'
```

**결과 확인:**
- ✅ Lint 통과 (경고는 허용)
- ✅ Breaking change 없음 → Minor/Patch 버전 업
- ⚠️ Breaking change 있음 → Major 버전 업 (문서화 필요)

---

### 2️⃣ Proto 파일 커밋 (Commit Proto Files Only)

**중요:** `generated/` 디렉토리는 커밋하지 않음! GitHub Actions가 자동 생성.

```bash
# Proto 파일만 스테이징
git add protos/

# 커밋 메시지 작성 (Conventional Commits)
git commit -m "feat(proto): add Backtest Service and update Strategy Service

- Add BacktestService proto with complete gRPC API
  - ExecuteBacktest, GetBacktestResult, StreamBacktestProgress RPCs
  - Support for backtest configuration, metrics, and result retrieval

- Update StrategyService proto for GenAI integration
  - Add ValidateStrategyIR RPC for multi-stage validation
  - Add GetStrategyTemplate and ListStrategyTemplates RPCs

Affected services:
- backtest-service (new gRPC server)
- strategy-service (updated gRPC server)
- genai-service (client for both services)

Breaking changes: None
Versioning: Minor version bump (0.X.0)"

# Push to main
git push origin main
```

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

Affected services:
- service1 (description)
- service2 (description)

Breaking changes: None | Yes (describe)
Versioning: Major|Minor|Patch version bump
```

**Types:**
- `feat`: 새 RPC 메서드, 새 서비스 추가 (Minor 버전)
- `fix`: 버그 수정, 필드 타입 수정 (Patch 버전)
- `breaking`: Breaking change (Major 버전)

---

### 3️⃣ GitHub Actions 자동 실행 확인

**Workflow:** `auto-generate.yml`

Push 후 자동 실행:
1. Python stubs 생성 (`buf generate`)
2. `generated/` 디렉토리에 커밋 (`[skip ci]`)

**확인:**
```bash
# 약 1-2분 후 확인
git pull origin main

# generated/ 파일들이 자동 커밋되었는지 확인
ls -la generated/mysingle_protos/protos/services/
```

---

### 4️⃣ 버전 업데이트 (Update Version)

`pyproject.toml` 버전 업데이트:

```bash
# pyproject.toml 편집
# version = "0.1.0" → version = "0.2.0"

git add pyproject.toml
git commit -m "chore: bump version to 0.2.0"
git push origin main
```

**버전 규칙:**
- **Major (X.0.0):** Breaking changes (필드 삭제, 타입 변경, 메서드 rename)
- **Minor (0.X.0):** 새 기능 (RPC 추가, optional 필드 추가)
- **Patch (0.0.X):** 버그 수정, 문서 업데이트

---

### 5️⃣ Git Tag 생성 및 Release (Create Tag & Release)

```bash
# 태그 생성
git tag -a v0.2.0 -m "Release v0.2.0: Add Backtest Service and update Strategy Service

- Add BacktestService proto with complete gRPC API
- Update StrategyService proto for GenAI integration
- Backward compatible changes"

# 태그 Push
git push origin v0.2.0
```

**Workflow:** `release.yml`

태그 push 후 자동 실행:
1. 버전 검증 (Git tag vs pyproject.toml)
2. Changelog 자동 생성
3. GitHub Release 생성

**확인:**
- https://github.com/Br0therDan/grpc-protos/releases
- Release 생성 완료 확인

---

## 📦 서비스에서 사용법 (Usage in Services)

### requirements.txt

```txt
mysingle-protos @ git+https://github.com/Br0therDan/grpc-protos.git@v0.2.0
```

### pyproject.toml

```toml
dependencies = [
    "mysingle-protos @ git+https://github.com/Br0therDan/grpc-protos.git@v0.3.0",
]
```

### 설치 및 업데이트

```bash
# 설치
pip install git+https://github.com/Br0therDan/grpc-protos.git@v0.2.0

# 업데이트 (버전 변경 후)
pip install --upgrade --force-reinstall git+https://github.com/Br0therDan/grpc-protos.git@v0.2.0
```

---

## 🔧 트러블슈팅 (Troubleshooting)

### 문제 1: GitHub Actions 실패 (Resource not accessible)

**원인:** Workflow 권한 부족

**해결:**
- `.github/workflows/` 파일들에 `permissions: contents: write` 추가 완료
- 이미 수정되어 있으므로 추가 조치 불필요

### 문제 2: Breaking change 감지

**원인:** 기존 proto 파일과 호환되지 않는 변경

**해결:**
```bash
# Breaking change 확인
buf breaking --against '.git#branch=main'

# 의도적인 경우
# 1. Major 버전 업 (1.0.0 → 2.0.0)
# 2. 커밋 메시지에 "BREAKING CHANGE:" 명시
# 3. 영향받는 서비스 목록 문서화
```

### 문제 3: 버전 불일치

**오류:** `Version mismatch! Git tag: v0.2.0, pyproject.toml: 0.1.0`

**해결:**
```bash
# pyproject.toml 버전 업데이트
git add pyproject.toml
git commit -m "chore: bump version to 0.2.0"
git push origin main

# 태그 재생성
git tag -d v0.2.0
git push origin :refs/tags/v0.2.0
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

### 문제 4: Generated code가 자동 커밋되지 않음

**원인:** `auto-generate.yml` 워크플로우 실행 실패

**확인:**
```bash
# GitHub Actions 로그 확인
# https://github.com/Br0therDan/grpc-protos/actions

# 로컬에서 수동 생성 (임시 대응)
buf generate
git add generated/
git commit -m "chore: regenerate proto stubs [skip ci]"
git push origin main
```

---

## ✅ Checklist

릴리스 전 체크리스트:

- [ ] `buf format -w` 실행
- [ ] `buf lint` 통과
- [ ] `buf breaking` 체크 (의도적 breaking change는 문서화)
- [ ] Proto 파일만 커밋 (generated/ 제외)
- [ ] GitHub Actions (auto-generate) 성공 확인
- [ ] `pyproject.toml` 버전 업데이트
- [ ] Git tag 생성 (vX.Y.Z)
- [ ] GitHub Release 생성 확인
- [ ] 영향받는 서비스 목록 문서화
- [ ] Slack/Discord 알림 (선택)

---

## 📚 관련 문서

- [README.md](./README.md) - 전체 가이드
- [buf.yaml](./buf.yaml) - Buf 설정
- [buf.gen.yaml](./buf.gen.yaml) - 코드 생성 설정
- [.github/workflows/](../.github/workflows/) - CI/CD 워크플로우

---

**Last Updated:** 2025-11-21  
**Maintainer:** MySingle Quant Platform Team
