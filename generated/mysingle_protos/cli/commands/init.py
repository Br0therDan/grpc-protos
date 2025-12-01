"""
Init 명령 - 로컬에서 grpc-protos 저장소 초기화.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from ..models import ProtoConfig
from ..utils import Color, LogLevel, colorize, log, log_header


def execute(args: argparse.Namespace, config: ProtoConfig) -> int:
    """Init 명령 실행"""
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
    pass  # Init 명령은 추가 인자가 없음
