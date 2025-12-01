"""
Init 명령 - grpc-protos 저장소 초기화 또는 서비스에 submodule 추가.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from ..models import ProtoConfig
from ..utils import Color, LogLevel, colorize, log, log_header


def _is_service_directory(cwd: Path) -> bool:
    """현재 디렉토리가 서비스 디렉토리인지 확인"""
    # services/* 디렉토리 패턴 확인
    return "services" in cwd.parts and cwd.name.endswith("-service")


def _setup_submodule(cwd: Path, remote_url: str) -> int:
    """서비스 디렉토리에 grpc-protos submodule 추가"""
    log_header("grpc-protos Submodule 구성")

    submodule_path = cwd / "grpc-protos"

    # 이미 submodule이 있는지 확인
    if submodule_path.exists():
        log(f"Submodule이 이미 존재합니다: {submodule_path}", LogLevel.INFO)

        # 최신 상태로 업데이트
        log("Submodule을 최신 상태로 업데이트합니다...", LogLevel.STEP)
        result = subprocess.run(
            ["git", "submodule", "update", "--remote", "--merge"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            log("✅ Submodule 업데이트 완료", LogLevel.SUCCESS)
        else:
            log(f"⚠️  Submodule 업데이트 실패: {result.stderr}", LogLevel.WARNING)
        return 0

    # Submodule 추가
    log(f"Submodule 추가 중: {remote_url}", LogLevel.STEP)
    result = subprocess.run(
        ["git", "submodule", "add", remote_url, "grpc-protos"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        log(f"❌ Submodule 추가 실패: {result.stderr}", LogLevel.ERROR)
        return 1

    log("✅ Submodule 추가 완료", LogLevel.SUCCESS)

    # Submodule 초기화
    log("Submodule 초기화 중...", LogLevel.STEP)
    result = subprocess.run(
        ["git", "submodule", "update", "--init", "--recursive"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        log(f"❌ Submodule 초기화 실패: {result.stderr}", LogLevel.ERROR)
        return 1

    log("✅ Submodule 초기화 완료", LogLevel.SUCCESS)

    # dev 브랜치로 체크아웃
    log("dev 브랜치로 전환 중...", LogLevel.STEP)
    result = subprocess.run(
        ["git", "checkout", "dev"],
        cwd=submodule_path,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        log("✅ dev 브랜치로 전환 완료", LogLevel.SUCCESS)
    else:
        log(f"⚠️  dev 브랜치 전환 실패 (main 유지): {result.stderr}", LogLevel.WARNING)

    # 사용 안내
    log("\n" + "=" * 60, LogLevel.INFO)
    log("🎉 Submodule 구성 완료!", LogLevel.SUCCESS)
    log("\n다음 단계:", LogLevel.INFO)
    log("  1. Proto 파일 수정:", LogLevel.INFO)
    log(
        f"     cd grpc-protos/protos/services/{cwd.name.replace('-service', '')}/v1/",
        LogLevel.INFO,
    )
    log("     vim <proto_file>.proto", LogLevel.INFO)
    log("  2. 검증 및 생성:", LogLevel.INFO)
    log("     cd grpc-protos", LogLevel.INFO)
    log("     uv run proto-cli validate --fix", LogLevel.INFO)
    log("     uv run proto-cli generate", LogLevel.INFO)
    log("  3. Git 작업:", LogLevel.INFO)
    log("     git checkout -b feature/xxx", LogLevel.INFO)
    log("     git add protos/ generated/", LogLevel.INFO)
    log("     git commit -m 'feat: ...'", LogLevel.INFO)
    log("     git push origin feature/xxx", LogLevel.INFO)

    return 0


def execute(args: argparse.Namespace, config: ProtoConfig) -> int:
    """Init 명령 실행"""
    cwd = Path.cwd()

    # 서비스 디렉토리인 경우 submodule 구성
    if _is_service_directory(cwd):
        remote_url = args.remote or "https://github.com/Br0therDan/grpc-protos.git"
        return _setup_submodule(cwd, remote_url)

    # grpc-protos 저장소 초기화
    log_header("grpc-protos 저장소 초기화")

    # Git 저장소 확인
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=config.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            log(
                f"이미 Git 저장소가 초기화되어 있습니다: {config.repo_root}",
                LogLevel.INFO,
            )
        else:
            log("Git 저장소가 아닙니다. 클론이 필요합니다.", LogLevel.WARNING)
            return 1
    except FileNotFoundError:
        log("Git이 설치되어 있지 않습니다.", LogLevel.ERROR)
        return 1

    # 브랜치 확인
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=config.repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    current_branch = result.stdout.strip()
    log(f"현재 브랜치: {colorize(current_branch, Color.BRIGHT_GREEN)}", LogLevel.INFO)

    # 원격 저장소 확인
    result = subprocess.run(
        ["git", "remote", "-v"],
        cwd=config.repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout:
        log("원격 저장소:", LogLevel.INFO)
        for line in result.stdout.strip().split("\n"):
            print(f"  {line}")
    else:
        log("원격 저장소가 설정되어 있지 않습니다.", LogLevel.WARNING)

    # Buf 설치 확인
    try:
        result = subprocess.run(
            ["buf", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            log(f"Buf 설치 확인: {colorize(version, Color.GREEN)}", LogLevel.SUCCESS)
        else:
            log("Buf가 설치되어 있지 않습니다.", LogLevel.WARNING)
            log("설치 방법: https://buf.build/docs/installation", LogLevel.INFO)
    except FileNotFoundError:
        log("Buf가 설치되어 있지 않습니다.", LogLevel.WARNING)
        log("설치 방법: https://buf.build/docs/installation", LogLevel.INFO)

    # 필수 디렉터리 확인
    directories = [
        ("Proto 디렉터리", config.proto_root),
        ("생성 디렉터리", config.generated_root),
    ]

    log("\n필수 디렉터리 확인:", LogLevel.INFO)
    for name, path in directories:
        if path.exists():
            log(f"  ✅ {name}: {path}", LogLevel.SUCCESS)
        else:
            log(f"  ❌ {name}: {path} (없음)", LogLevel.ERROR)

    log("\n초기화 완료!", LogLevel.SUCCESS)
    log(
        f"다음 명령으로 서비스 상태를 확인하세요: {colorize('proto-cli status', Color.BRIGHT_YELLOW)}",
        LogLevel.INFO,
    )

    return 0


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Init 명령 파서 설정"""
    parser.add_argument(
        "--remote",
        type=str,
        default="https://github.com/Br0therDan/grpc-protos.git",
        help="grpc-protos 저장소 원격 URL (기본: https://github.com/Br0therDan/grpc-protos.git)",
    )
