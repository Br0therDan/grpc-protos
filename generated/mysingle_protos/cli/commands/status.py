"""
Status 명령 - 서비스별 proto 파일 상태 확인.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ..models import ProtoConfig, ServiceProtoInfo
from ..utils import Color, LogLevel, colorize, log, log_header, log_table


def discover_services(config: ProtoConfig) -> list[ServiceProtoInfo]:
    """서비스 디렉터리에서 proto 정보 스캔"""
    if not config.services_root.exists():
        raise SystemExit(
            f"서비스 루트 디렉터리를 찾을 수 없습니다: {config.services_root}"
        )

    log_header("서비스 스캔")
    result: list[ServiceProtoInfo] = []
    skipped = 0

    for service_dir in sorted(p for p in config.services_root.iterdir() if p.is_dir()):
        proto_dir = service_dir / "protos"
        if not proto_dir.exists():
            log(
                f"건너뛰기: {colorize(service_dir.name, Color.DIM)} (protos 디렉터리 없음)",
                LogLevel.WARNING,
            )
            skipped += 1
            continue
        files = sorted(proto_dir.rglob("*.proto"))
        if not files:
            log(
                f"건너뛰기: {colorize(service_dir.name, Color.DIM)} (proto 파일 없음)",
                LogLevel.WARNING,
            )
            skipped += 1
            continue
        result.append(ServiceProtoInfo(service_dir.name, service_dir, proto_dir, files))
        log(
            f"발견: {colorize(service_dir.name, Color.GREEN)} ({len(files)}개 파일)",
            LogLevel.SUCCESS,
        )

    log(
        f"\n총 {colorize(str(len(result)), Color.BRIGHT_GREEN, bold=True)}개 서비스 발견 (건너뜀: {skipped}개)",
        LogLevel.INFO,
    )
    return result


def execute(args: argparse.Namespace, config: ProtoConfig) -> int:
    """Status 명령 실행"""
    services = discover_services(config)

    if not services:
        log("발견된 서비스가 없습니다.", LogLevel.WARNING)
        return 1

    log_header("서비스별 Proto 파일 현황")

    rows = []
    for service in services:
        rows.append([service.name, str(len(service.files)), str(service.proto_dir)])

    log_table(["서비스 이름", "Proto 파일 수", "경로"], rows)

    # 상세 모드
    if args.verbose:
        log_header("Proto 파일 상세 목록")
        for service in services:
            print(f"\n{colorize(service.name, Color.BRIGHT_CYAN, bold=True)}:")
            for proto_file in service.files:
                rel_path = proto_file.relative_to(service.proto_dir)
                print(f"  • {rel_path}")

    return 0


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Status 명령 파서 설정"""
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Proto 파일 상세 목록 출력",
    )
