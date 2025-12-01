"""
Version 명령 - Proto 버전 정보 확인.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from ..models import ProtoConfig
from ..utils import Color, LogLevel, colorize, log, log_header


def get_current_proto_version(config: ProtoConfig) -> str | None:
    """pyproject.toml에서 현재 proto 버전 추출"""
    path = config.repo_root / "pyproject.toml"
    if not path.exists():
        return None

    content = path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"\n]+)"', content, flags=re.MULTILINE)
    return match.group(1) if match else None


def check_git_status(config: ProtoConfig) -> dict[str, str | bool]:
    """Git 상태 확인"""
    import subprocess

    status: dict[str, str | bool] = {"is_clean": False, "current_branch": ""}

    try:
        # 작업 트리 상태 확인
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=config.repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        status["is_clean"] = not result.stdout.strip()

        # 현재 브랜치 확인
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=config.repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        status["current_branch"] = result.stdout.strip()

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return status


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """파서 설정"""
    parser.add_argument(
        "--check-git",
        action="store_true",
        help="Git 상태도 함께 확인",
    )


def execute(args: argparse.Namespace, config: ProtoConfig) -> int:
    """Version 명령 실행"""
    log_header("Proto 버전 정보")

    # 패키지 버전
    version = get_current_proto_version(config)
    if version:
        log(
            f"현재 버전: {colorize(f'v{version}', Color.BRIGHT_GREEN, bold=True)}",
            LogLevel.INFO,
        )
    else:
        log("버전 정보를 찾을 수 없습니다.", LogLevel.WARNING)
        return 1

    # Git 상태 (옵션)
    if args.check_git:
        git_status = check_git_status(config)

        branch = git_status.get("current_branch")
        if branch and isinstance(branch, str):
            log(
                f"현재 브랜치: {colorize(branch, Color.CYAN)}",
                LogLevel.INFO,
            )

        if git_status.get("is_clean"):
            log("Git 작업 트리: ✅ 깨끗함", LogLevel.SUCCESS)
        else:
            log("Git 작업 트리: ⚠️  변경사항 있음", LogLevel.WARNING)

    # GitHub 릴리즈 URL
    log(
        f"\n📦 GitHub 릴리즈: {colorize(f'https://github.com/Br0therDan/grpc-protos/releases/tag/v{version}', Color.BRIGHT_BLUE)}",
        LogLevel.INFO,
    )

    return 0
