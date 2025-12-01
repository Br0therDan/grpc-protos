"""
Generate 명령 - Buf를 사용하여 Python gRPC 스텁 생성.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from ..models import ProtoConfig
from ..utils import Color, LogLevel, colorize, log, log_header


def ensure_file_exists(path: Path, description: str) -> None:
    """필수 파일 존재 확인"""
    if not path.exists():
        raise SystemExit(f"필수 파일 누락: {description} ({path})")


def buf_generate(config: ProtoConfig) -> None:
    """Buf를 사용하여 코드 생성"""
    ensure_file_exists(config.buf_template, "buf.gen.yaml 템플릿")

    log("Buf를 사용하여 코드 생성 중...", LogLevel.STEP)

    try:
        subprocess.run(
            ["buf", "generate", "--template", str(config.buf_template)],
            cwd=config.repo_root,
            check=True,
        )
        log("코드 생성 완료", LogLevel.SUCCESS)
    except subprocess.CalledProcessError as e:
        log(f"코드 생성 실패: {e}", LogLevel.ERROR)
        raise SystemExit(1) from e
    except FileNotFoundError:
        log("Buf가 설치되어 있지 않습니다.", LogLevel.ERROR)
        log("설치 방법: https://buf.build/docs/installation", LogLevel.INFO)
        raise SystemExit(1)


def rewrite_generated_imports(
    generated_dir: Path, package_name: str = "mysingle_protos"
) -> list[Path]:
    """생성된 파일의 import 경로 수정"""
    if not generated_dir.exists():
        return []

    log("생성된 파일의 import 경로 수정 중...", LogLevel.STEP)

    patterns = ("*_pb2.py", "*_pb2_grpc.py")
    replacements = [
        (re.compile(r"from protos\."), f"from {package_name}.protos."),
        (re.compile(r"import protos\."), f"import {package_name}.protos."),
    ]

    modified: list[Path] = []

    for pattern in patterns:
        for file_path in generated_dir.rglob(pattern):
            original = file_path.read_text(encoding="utf-8")
            updated = original

            for regex, repl in replacements:
                updated = regex.sub(repl, updated)

            if updated != original:
                file_path.write_text(updated, encoding="utf-8")
                modified.append(file_path)
                log(
                    f"수정: {colorize(str(file_path.relative_to(generated_dir)), Color.CYAN)}",
                    LogLevel.DEBUG,
                )

    if modified:
        log(
            f"총 {colorize(str(len(modified)), Color.GREEN, bold=True)}개 파일 import 수정 완료",
            LogLevel.SUCCESS,
        )
    else:
        log("import 수정이 필요한 파일 없음", LogLevel.INFO)

    return modified


def execute(args: argparse.Namespace, config: ProtoConfig) -> int:
    """Generate 명령 실행"""
    log_header("Proto 코드 생성")

    # 1. Buf 코드 생성
    buf_generate(config)

    # 2. Import 경로 수정
    if not args.skip_rewrite:
        package_dir = config.generated_root / config.package_name
        rewrite_generated_imports(package_dir, config.package_name)

    log("\n✅ 모든 작업 완료!", LogLevel.SUCCESS)

    return 0


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Generate 명령 파서 설정"""
    parser.add_argument(
        "--skip-rewrite",
        action="store_true",
        help="import 경로 수정 단계 건너뛰기",
    )
