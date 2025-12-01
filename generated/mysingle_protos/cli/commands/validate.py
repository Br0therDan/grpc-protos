"""
Validate 명령 - Buf lint 및 format check 실행.
"""

from __future__ import annotations

import argparse
import subprocess

from ..models import ProtoConfig
from ..utils import Color, LogLevel, colorize, log, log_header


def buf_lint(config: ProtoConfig) -> bool:
    """Buf lint 실행"""
    log("Buf lint 실행 중...", LogLevel.STEP)

    try:
        subprocess.run(
            ["buf", "lint"],
            cwd=config.repo_root,
            check=True,
        )
        log("✅ Lint 통과", LogLevel.SUCCESS)
        return True
    except subprocess.CalledProcessError:
        log("❌ Lint 실패", LogLevel.ERROR)
        return False
    except FileNotFoundError:
        log("Buf가 설치되어 있지 않습니다.", LogLevel.ERROR)
        log("설치 방법: https://buf.build/docs/installation", LogLevel.INFO)
        return False


def buf_format_check(config: ProtoConfig, fix: bool = False) -> bool:
    """Buf format check 실행"""
    if fix:
        log("Buf format 자동 수정 중...", LogLevel.STEP)
        try:
            subprocess.run(
                ["buf", "format", "-w"],
                cwd=config.repo_root,
                check=True,
            )
            log("✅ Format 수정 완료", LogLevel.SUCCESS)
            return True
        except subprocess.CalledProcessError:
            log("❌ Format 수정 실패", LogLevel.ERROR)
            return False
        except FileNotFoundError:
            log("Buf가 설치되어 있지 않습니다.", LogLevel.ERROR)
            return False
    else:
        log("Buf format check 실행 중...", LogLevel.STEP)
        try:
            subprocess.run(
                ["buf", "format", "-d", "--exit-code"],
                cwd=config.repo_root,
                check=True,
            )
            log("✅ Format 통과", LogLevel.SUCCESS)
            return True
        except subprocess.CalledProcessError:
            log("❌ Format 검사 실패 (수정이 필요합니다)", LogLevel.ERROR)
            log(
                f"자동 수정: {colorize('proto-cli validate --fix', Color.BRIGHT_YELLOW)}",
                LogLevel.INFO,
            )
            return False
        except FileNotFoundError:
            log("Buf가 설치되어 있지 않습니다.", LogLevel.ERROR)
            return False


def buf_breaking(config: ProtoConfig, against: str = "main") -> bool:
    """Buf breaking change 검사"""
    log(f"Breaking change 검사 중 (vs {against})...", LogLevel.STEP)

    try:
        subprocess.run(
            [
                "buf",
                "breaking",
                "--against",
                f"https://github.com/Br0therDan/grpc-protos.git#branch={against}",
            ],
            cwd=config.repo_root,
            check=True,
        )
        log("✅ Breaking change 없음", LogLevel.SUCCESS)
        return True
    except subprocess.CalledProcessError:
        log("⚠️  Breaking change 감지됨", LogLevel.WARNING)
        log("주의: Breaking change는 버전 메이저 업데이트가 필요합니다.", LogLevel.INFO)
        return False
    except FileNotFoundError:
        log("Buf가 설치되어 있지 않습니다.", LogLevel.ERROR)
        return False


def execute(args: argparse.Namespace, config: ProtoConfig) -> int:
    """Validate 명령 실행"""
    log_header("Proto 파일 검증")

    results = []

    # 1. Lint 검사
    if not args.skip_lint:
        lint_pass = buf_lint(config)
        results.append(("Lint", lint_pass))

    # 2. Format 검사
    if not args.skip_format:
        format_pass = buf_format_check(config, fix=args.fix)
        results.append(("Format", format_pass))

    # 3. Breaking change 검사
    if args.breaking:
        breaking_pass = buf_breaking(config, against=args.against)
        results.append(("Breaking", breaking_pass))

    # 결과 요약
    log_header("검증 결과")
    for name, passed in results:
        status = (
            colorize("✅ 통과", Color.GREEN)
            if passed
            else colorize("❌ 실패", Color.RED)
        )
        print(f"{name:15} {status}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        log("\n🎉 모든 검증 통과!", LogLevel.SUCCESS)
        return 0
    else:
        log("\n⚠️  일부 검증 실패", LogLevel.WARNING)
        return 1


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Validate 명령 파서 설정"""
    parser.add_argument(
        "--skip-lint",
        action="store_true",
        help="Lint 검사 건너뛰기",
    )
    parser.add_argument(
        "--skip-format",
        action="store_true",
        help="Format 검사 건너뛰기",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Format 오류 자동 수정",
    )
    parser.add_argument(
        "--breaking",
        action="store_true",
        help="Breaking change 검사 수행",
    )
    parser.add_argument(
        "--against",
        default="main",
        help="Breaking change 비교 대상 브랜치 (기본값: main)",
    )
