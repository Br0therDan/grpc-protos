# gRPC Protos - MySingle Quant

MySingle Quant 플랫폼의 중앙집중식 gRPC Protocol Buffers 저장소입니다.

## 🎯 개요

이 저장소는 모든 마이크로서비스 간 통신에 사용되는 proto 파일을 중앙에서 관리하고, Python gRPC 스텁을 자동 생성하여 배포합니다.

### 주요 기능

- 🔧 **통합 CLI 도구**: `proto-cli` 명령으로 proto 파일 관리 자동화
- 🔗 **Submodule 기반 워크플로우**: 서비스별 grpc-protos submodule 자동 구성
- 🎨 **한국어 인터페이스**: 모든 CLI 출력은 한국어 기반
- 🌈 **색상 코드 로그**: 레벨별 색상 구분 및 아이콘 표시
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

### 패키지 설치

```bash
# Git 저장소에서 직접 설치 (최신 릴리즈)
uv pip install git+https://github.com/Br0therDan/grpc-protos.git@main

# 특정 버전 설치
uv pip install git+https://github.com/Br0therDan/grpc-protos.git@v2.0.4

# 개발 브랜치 설치
uv pip install git+https://github.com/Br0therDan/grpc-protos.git@dev
```

### 로컬 개발

```bash
# 저장소 클론
git clone https://github.com/Br0therDan/grpc-protos.git
cd grpc-protos

# 개발 환경 설정
uv venv
uv pip install -e .

# CLI 도구 사용
uv run proto-cli --help
```

## 🔧 CLI 도구 사용법

### proto-cli 명령어

> **💡 사용 컨텍스트**
> - **grpc-protos 메인 저장소**: `init`, `status`, `validate`, `generate`, `version` 모두 사용 가능
> - **서비스 submodule 내** (`services/*/grpc-protos`): `init`, `validate`, `generate`, `version`만 사용
>   - `status` 명령은 메인 저장소에서만 의미가 있습니다.

#### 1. 저장소 초기화 및 환경 확인

#### 1. 저장소 초기화 및 Submodule 구성

**서비스 디렉토리에서 실행 (권장):**

각 서비스에서 grpc-protos를 submodule로 자동 구성합니다.

```bash
cd services/strategy-service
uv run proto-cli init
```

**출력 예시:**
```
============================================================
  grpc-protos Submodule 구성
============================================================

📋 Submodule 추가 중: https://github.com/Br0therDan/grpc-protos.git
✅ Submodule 추가 완료
📋 Submodule 초기화 중...
✅ Submodule 초기화 완료
📋 dev 브랜치로 전환 중...
✅ dev 브랜치로 전환 완료

============================================================
🎉 Submodule 구성 완료!

다음 단계:
  1. Proto 파일 수정:
     cd grpc-protos/protos/services/strategy/v1/
     vim strategy_service.proto
  2. 검증 및 생성:
     cd grpc-protos
     uv run proto-cli validate --fix
     uv run proto-cli generate
  3. Git 작업:
     git checkout -b feature/xxx
     git add protos/ generated/
     git commit -m 'feat: ...'
     git push origin feature/xxx
```

**grpc-protos 저장소 내에서 실행:**

환경 확인 및 검증용으로 사용합니다.

```bash
cd grpc-protos
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

#### 2. Proto 파일 현황 확인

**⚠️  이 명령은 grpc-protos 메인 저장소에서만 사용하세요.**

grpc-protos 저장소 내부에서 proto 파일 현황을 확인합니다.

```bash
cd grpc-protos  # 메인 저장소로 이동
uv run proto-cli status

# 상세 모드 (파일 목록 포함)
uv run proto-cli status -v
```

**출력 예시:**
```
============================================================
  Proto 파일 현황
============================================================

서비스 이름               Proto 파일 수  최근 수정
--------------------------------------------------------------
strategy                2           2025-12-01
market-data             1           2025-11-28
indicator               1           2025-11-25
```

#### 3. Python 코드 생성

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

#### 4. Proto 파일 검증

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

#### 5. 버전 정보 확인

현재 proto 버전과 Git 상태를 확인합니다.

```bash
# 기본 버전 확인
uv run proto-cli version

# Git 상태 포함
uv run proto-cli version --check-git
```

**출력 예시:**
```
============================================================
  Proto 버전 정보
============================================================

ℹ️  현재 버전: v2.0.4
ℹ️  현재 브랜치: dev
✅ Git 작업 트리: ✅ 깨끗함

📦 GitHub 릴리즈: https://github.com/Br0therDan/grpc-protos/releases/tag/v2.0.4
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

### 🔧 초기 설정 (각 서비스에서 1회만)

각 서비스 디렉토리에서 grpc-protos를 submodule로 자동 구성:

```bash
cd services/strategy-service
uv run proto-cli init
```

**자동 실행 내용:**
- Git submodule 추가 및 초기화
- dev 브랜치로 자동 체크아웃
- 사용 가이드 출력

### 📝 Proto 개발 워크플로우

```bash
# 1. Submodule 최신화
cd services/strategy-service/grpc-protos
git checkout dev
git pull origin dev

# 2. Feature 브랜치 생성
git checkout -b feature/add-batch-get-strategies

# 3. Proto 파일 수정 (다른 서비스 proto 참조 가능!)
vim protos/services/strategy/v1/strategy_service.proto

# 교차 검증 예시
cat protos/services/indicator/v1/indicator_service.proto

# 4. 검증 및 코드 생성
uv run proto-cli validate --fix
uv run proto-cli generate

# 5. Git 작업 (submodule 내에서)
git add protos/ generated/
git commit -m "feat: add BatchGetStrategies RPC method"
git push origin feature/add-batch-get-strategies

# 6. PR 생성
gh pr create --base dev --title "feat: add BatchGetStrategies RPC"

# 7. 부모 레포 업데이트 (선택사항)
cd ..
git add grpc-protos
git commit -m "chore: update grpc-protos submodule"
git push
```

### 🔄 교차 검증 시나리오

다른 서비스의 proto 변경사항을 확인하고 영향도 분석:

```bash
cd services/strategy-service/grpc-protos

# Indicator proto 변경 이력 확인
git log --oneline protos/services/indicator/v1/

# 최신 변경사항 비교
git diff origin/dev protos/services/indicator/v1/indicator_service.proto

# 영향도 분석 후 Strategy proto 수정
vim protos/services/strategy/v1/strategy_service.proto

# 검증
uv run proto-cli validate --fix
uv run proto-cli generate
```

## 📋 CODEOWNERS

팀별 리뷰 권한 자동 지정:

```plaintext
# 공통 proto
/protos/common/ @Br0therDan

# 서비스별 proto
/protos/services/strategy/ @Br0therDan
/protos/services/market_data/ @Br0therDan
/protos/services/indicator/ @Br0therDan
```

## 🚀 CI/CD 파이프라인

### PR 검증 (pr-validation.yml)

PR 생성 시 자동 실행:

- ✅ **buf-lint**: Proto 파일 린트 검사
- ✅ **buf-format-check**: 포맷 규칙 검증
- ✅ **buf-breaking**: Breaking change 검증 (main PR만)
- ✅ **generate-protos-test**: Python 스텁 생성 테스트

### 자동 릴리즈 (auto-release.yml)

dev → main 병합 시 자동 실행:

1. 버전 추출 (`pyproject.toml`)
2. Proto 코드 생성 (`buf generate`)
3. Python 패키지 빌드 (`uv build`)
4. Git 태그 생성 및 GitHub Release 발행

### CLI 테스트 (cli-tests.yml)

CLI 파일 수정 시 자동 실행:

- ✅ `proto-cli --help` 검증
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
│       │   ├── utils.py        # 유틸리티 (colorize, log)
│       │   ├── models.py       # 데이터 모델
│       │   └── commands/       # 명령어 모듈
│       │       ├── init.py     # Submodule 자동 구성
│       │       ├── status.py   # Proto 현황
│       │       ├── validate.py # Buf 검증
│       │       └── generate.py # 코드 생성
│       └── protos/             # 생성된 Python 스텁
├── protos/
│   ├── common/                 # 공통 proto 파일
│   └── services/               # 서비스별 proto 파일
│       ├── strategy/
│       ├── market_data/
│       ├── indicator/
│       └── ...
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

1. dev 브랜치에서 feature 브랜치 생성
2. Proto 파일 수정 및 검증
3. PR 생성 및 리뷰 요청
4. CI 통과 및 승인 후 병합

---

## 🗺️ Roadmap

### 단기 계획
- [ ] **proto-cli pr**: GitHub API 연동 PR 자동 생성
- [ ] **proto-cli diff**: Proto 변경사항 시각화
- [ ] **Breaking Change 상세 리포트**: 영향받는 서비스 자동 감지

### 중기 계획
- [ ] **proto-cli owners**: CODEOWNERS 기반 리뷰어 자동 지정
- [ ] **proto-cli impact**: 의존성 그래프 분석 및 영향도 분석
- [ ] **Web Dashboard**: Proto 문서 자동 생성 및 버전 히스토리

### 장기 계획
- [ ] **Multi-language 지원**: Go, TypeScript, Java 스텁 생성
- [ ] **Proto Registry**: 중앙 집중식 proto 검색 및 문서화
- [ ] **자동 Migration Tool**: Breaking change 자동 마이그레이션

---

**Repository**: https://github.com/Br0therDan/grpc-protos  
**Maintainer**: @Br0therDan
