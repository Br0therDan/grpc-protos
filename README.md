# gRPC Protos - MySingle Quant

MySingle Quant 플랫폼의 중앙집중식 gRPC Protocol Buffers 저장소입니다.

## 🎯 개요

이 저장소는 모든 마이크로서비스 간 통신에 사용되는 proto 파일을 중앙에서 관리하고, Python gRPC 스텁을 자동 생성하여 배포합니다.

### 주요 기능

- 🔧 **통합 CLI 도구**: `proto-cli` 명령으로 proto 파일 관리 자동화
- 🎨 **한국어 인터페이스**: 모든 CLI 출력은 한국어 기반
- 🌈 **색상 코드 로그**: 레벨별 색상 구분 및 아이콘 표시
- 📊 **테이블 포맷**: 서비스별 proto 현황을 보기 좋게 표시
- 🚀 **자동 릴리즈**: dev → main 병합 시 자동 태그 및 GitHub Release 생성
- ✅ **PR 검증**: buf lint, format check, breaking change detection

## 📦 설치

### 필수 요구사항

```bash
# uv 설치 (Python 패키지 관리자)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는 macOS/Linux
brew install uv
```

### 패키지 설치 (서비스 개발자)

```bash
# Git 저장소에서 직접 설치
uv pip install git+https://github.com/Br0therDan/grpc-protos.git@v2.0.4

# 또는 특정 브랜치
uv pip install git+https://github.com/Br0therDan/grpc-protos.git@dev
```

### 로컬 개발 (Proto 관리자)

```bash
# 저장소 클론
git clone https://github.com/Br0therDan/grpc-protos.git
cd grpc-protos

# 개발 모드 설치
uv pip install -e .

# CLI 도구 사용
uv run proto-cli --help
```

## 🔧 CLI 도구 사용법

### proto-cli 명령어

#### 1. 저장소 초기화 및 환경 확인

```bash
uv run proto-cli init
```

**출력 예시:**
```
============================================================
  grpc-protos 저장소 초기화
============================================================

ℹ️  이미 Git 저장소가 초기화되어 있습니다
ℹ️  현재 브랜치: dev
✅ Buf 설치 확인: 1.60.0
✅ Proto 디렉터리: /path/to/grpc-protos/protos
✅ 생성 디렉터리: /path/to/grpc-protos/generated
✅ 초기화 완료!
```

#### 2. 서비스별 Proto 파일 현황 확인

```bash
# 기본 모드
uv run proto-cli status

# 상세 모드 (파일 목록 포함)
uv run proto-cli status -v
```

**출력 예시:**
```
============================================================
  서비스 스캔
============================================================

✅ 발견: strategy-service (1개 파일)
✅ 발견: market-data-service (1개 파일)
⚠️  건너뛰기: iam-service (proto 파일 없음)

총 6개 서비스 발견 (건너뜀: 4개)

============================================================
  서비스별 Proto 파일 현황
============================================================

서비스 이름               Proto 파일 수  경로
--------------------------------------------------------------
strategy-service     1           /path/to/services/strategy-service/protos
market-data-service  1           /path/to/services/market-data-service/protos
```

#### 3. Proto 파일 동기화

서비스 디렉터리의 proto 파일을 중앙 저장소로 복사합니다.

```bash
# 전체 서비스 동기화
uv run proto-cli sync

# 특정 서비스만 동기화
uv run proto-cli sync strategy-service

# 변경 사항 미리보기 (실제 복사 안 함)
uv run proto-cli sync --dry-run
```

#### 4. Python 코드 생성

Buf를 사용하여 proto 파일로부터 Python gRPC 스텁을 생성합니다.

```bash
# 코드 생성 및 import 경로 수정
uv run proto-cli generate

# import 경로 수정 건너뛰기
uv run proto-cli generate --skip-rewrite
```

**출력 예시:**
```
============================================================
  Proto 코드 생성
============================================================

📋 Buf를 사용하여 코드 생성 중...
✅ 코드 생성 완료

📋 생성된 파일의 import 경로 수정 중...
🔍 수정: protos/services/strategy/v1/strategy_service_pb2.py
✅ 총 15개 파일 import 수정 완료
✅ 모든 작업 완료!
```

#### 5. Proto 파일 검증

Buf lint, format check, breaking change 검증을 실행합니다.

```bash
# 기본 검증 (lint + format)
uv run proto-cli validate

# Format 오류 자동 수정
uv run proto-cli validate --fix

# Breaking change 검사 포함
uv run proto-cli validate --breaking

# Lint 건너뛰기
uv run proto-cli validate --skip-lint

# 특정 브랜치와 비교
uv run proto-cli validate --breaking --against dev
```

**출력 예시:**
```
============================================================
  Proto 파일 검증
============================================================

📋 Buf lint 실행 중...
✅ Lint 통과

📋 Buf format check 실행 중...
✅ Format 통과

📋 Breaking change 검사 중 (vs main)...
✅ Breaking change 없음

============================================================
  검증 결과
============================================================

Lint            ✅ 통과
Format          ✅ 통과
Breaking        ✅ 통과

🎉 모든 검증 통과!
```

#### 6. 도움말

```bash
uv run proto-cli --help
```

## 🌳 브랜치 전략

### Git Flow 기반 브랜치 구조

```
main (보호됨)
  ↑ PR (2명 승인 + CI 통과)
dev (보호됨)
  ↑ PR (1명 승인 + CI 통과)
feature/* (자유롭게 생성)
hotfix/* (긴급 수정)
```

### 브랜치 설명

- **main**: 프로덕션 릴리즈 브랜치 (태그 자동 생성)
- **dev**: 개발 통합 브랜치
- **feature/\***: 기능 개발 브랜치
- **hotfix/\***: 긴급 수정 브랜치

## 👥 협업 워크플로우

### 서버 팀 (gRPC Server 개발자)

```bash
# 1. dev 브랜치에서 feature 브랜치 생성
git checkout dev
git pull origin dev
git checkout -b feature/add-batch-get-strategies

# 2. Proto 파일 수정
vim protos/services/strategy/v1/strategy_service.proto

# 3. CLI를 사용한 검증
uv run proto-cli validate --fix

# 4. 커밋 및 푸시
git add protos/
git commit -m "feat: add BatchGetStrategies RPC method"
git push origin feature/add-batch-get-strategies

# 5. GitHub에서 PR 생성 (feature → dev)
# CI 자동 실행: buf-lint, buf-format-check, generate-protos-test
```

### 클라이언트 팀 (gRPC Client 개발자)

```bash
# 1. 최신 proto 패키지 설치
uv pip install git+https://github.com/Br0therDan/grpc-protos.git@v2.0.4

# 2. gRPC 클라이언트 코드 작성
from mysingle_protos.protos.services.strategy.v1 import strategy_service_pb2
from mysingle_protos.protos.services.strategy.v1 import strategy_service_pb2_grpc

# 3. 필요한 경우 proto 수정 제안
# GitHub Issue 또는 서버 팀에 요청
```

## 📋 CODEOWNERS

`.github/CODEOWNERS` 파일을 통해 팀별 리뷰 권한이 자동 지정됩니다:

```
# 공통 proto (모든 서비스에 영향)
/protos/common/ @Br0therDan

# 서비스별 proto
/protos/services/strategy/ @Br0therDan
/protos/services/market_data/ @Br0therDan
```

## 🚀 CI/CD 파이프라인

### PR 검증 (pr-validation.yml)

dev 또는 main 브랜치로의 PR 시 자동 실행:

- ✅ **buf-lint**: Proto 파일 린트 검사
- ✅ **buf-format-check**: 포맷 규칙 검증
- ✅ **buf-breaking**: Breaking change 검증 (main PR만)
- ✅ **generate-protos-test**: Python 스텁 생성 테스트

### 자동 릴리즈 (auto-release.yml)

dev → main 병합 시 자동 실행:

1. `pyproject.toml`에서 버전 추출
2. Proto 코드 생성 (`buf generate`)
3. Python 패키지 빌드 (`uv build`)
4. Git 태그 생성 및 GitHub Release 발행
5. 빌드된 패키지 첨부

### CLI 테스트 (cli-tests.yml)

CLI 관련 파일 수정 시 자동 실행:

- ✅ `proto-cli --help` 출력 검증
- ✅ `proto-cli init` 동작 확인
- ✅ `proto-cli status` 동작 확인

## 📚 디렉터리 구조

```
grpc-protos/
├── .github/
│   ├── CODEOWNERS              # 팀별 코드 소유권
│   └── workflows/               # GitHub Actions
│       ├── pr-validation.yml
│       ├── auto-release.yml
│       └── cli-tests.yml
├── docs/
│   └── COLLABORATIVE_WORKFLOW_DESIGN.md  # 협업 워크플로우 설계 문서
├── generated/
│   └── mysingle_protos/
│       ├── cli/                 # CLI 도구 모듈
│       │   ├── __main__.py     # CLI 진입점
│       │   ├── utils.py        # 유틸리티 함수
│       │   ├── models.py       # 데이터 모델
│       │   └── commands/       # 명령어 모듈
│       │       ├── init.py
│       │       └── status.py
│       └── protos/             # 생성된 Python 스텁
├── protos/
│   ├── common/                 # 공통 proto 파일
│   └── services/               # 서비스별 proto 파일
│       ├── strategy/
│       ├── market_data/
│       └── ...
├── scripts/
│   └── proto_orchestrator.py  # 레거시 오케스트레이터 (deprecated)
├── buf.yaml                    # Buf 설정
├── buf.gen.yaml                # 코드 생성 설정
└── pyproject.toml              # Python 패키지 설정
```

## 🔍 Buf 도구

### Buf CLI 설치

```bash
# macOS
brew install bufbuild/buf/buf

# Linux
curl -sSL https://github.com/bufbuild/buf/releases/download/v1.60.0/buf-Linux-x86_64 -o /usr/local/bin/buf
chmod +x /usr/local/bin/buf
```

### 주요 명령어

```bash
# Proto 파일 린트
buf lint

# 포맷 검사
buf format -d --exit-code

# 포맷 자동 수정
buf format -w

# Breaking change 검증
buf breaking --against '.git#branch=main'

# 코드 생성
buf generate
```

## 📖 참고 문서

- [협업 워크플로우 설계 문서](docs/COLLABORATIVE_WORKFLOW_DESIGN.md)
- [Buf 공식 문서](https://buf.build/docs)
- [gRPC Python Quickstart](https://grpc.io/docs/languages/python/quickstart/)

## 🤝 기여 가이드

1. Issue 생성 또는 기존 Issue 확인
2. dev 브랜치에서 feature 브랜치 생성
3. Proto 파일 수정 및 buf 검증
4. PR 생성 및 리뷰 요청
5. CI 통과 및 승인 후 병합

## 📄 라이선스

MIT License

---

**Repository**: https://github.com/Br0therDan/grpc-protos  
**Maintainer**: @Br0therDan
