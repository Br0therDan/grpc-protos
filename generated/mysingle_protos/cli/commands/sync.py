"""
Sync 명령 - 서비스별 proto 파일을 중앙 저장소로 동기화.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from ..models import ProtoConfig, ServiceProtoInfo
from ..utils import Color, LogLevel, colorize, log, log_header
from .status import discover_services


def get_service_by_name(
    services: list[ServiceProtoInfo], name: str
) -> ServiceProtoInfo:
    """이름으로 서비스 찾기"""
    for service in services:
        if service.name == name:
            return service
    available = ", ".join(s.name for s in services[:5])
    raise SystemExit(
        f"서비스 '{name}'을(를) 찾을 수 없습니다. 사용 가능한 서비스: {available}..."
    )


def relative_destination(
    proto_file: Path, service: ServiceProtoInfo, config: ProtoConfig
) -> Path:
    """Proto 파일의 대상 경로 계산"""
    try:
        rel = proto_file.relative_to(service.proto_dir)
    except ValueError as exc:
        raise RuntimeError(f"{proto_file} is not under {service.proto_dir}") from exc
    return config.proto_root / rel


def files_differ(src: Path, dest: Path) -> bool:
    """파일 내용 비교"""
    if not dest.exists():
        return True
    return src.read_bytes() != dest.read_bytes()


def sync_service_protos(
    service: ServiceProtoInfo, config: ProtoConfig, dry_run: bool = False
) -> list[Path]:
    """단일 서비스의 proto 파일 동기화"""
    updates: list[Path] = []
    total_files = len(service.files)
    processed = 0

    log_header(f"{service.name} Proto 동기화")

    for proto in service.files:
        processed += 1
        dest = relative_destination(proto, service, config)

        if files_differ(proto, dest):
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dry_run:
                log(
                    f"[{processed}/{total_files}] DRY-RUN: {colorize(str(proto.relative_to(service.service_dir)), Color.YELLOW)} → {dest.relative_to(config.proto_root)}",
                    LogLevel.INFO,
                )
            else:
                shutil.copy2(proto, dest)
                log(
                    f"[{processed}/{total_files}] 동기화: {colorize(service.name, Color.GREEN)} / {proto.name}",
                    LogLevel.SUCCESS,
                )
            updates.append(dest)
        else:
            log(
                f"[{processed}/{total_files}] 건너뜀: {proto.name} (변경 없음)",
                LogLevel.DEBUG,
            )

    if not updates:
        log("변경된 proto 파일이 없습니다.", LogLevel.INFO)
    else:
        log(
            f"\n총 {colorize(str(len(updates)), Color.BRIGHT_GREEN, bold=True)}개 파일 동기화 완료",
            LogLevel.SUCCESS,
        )

    return updates


def sync_all_services(
    services: list[ServiceProtoInfo], config: ProtoConfig, dry_run: bool = False
) -> dict[str, list[Path]]:
    """모든 서비스의 proto 파일 동기화"""
    log_header("전체 서비스 Proto 동기화")

    updates: dict[str, list[Path]] = {}
    total_files = sum(len(s.files) for s in services)
    processed = 0

    for service in services:
        for proto in service.files:
            processed += 1
            dest = relative_destination(proto, service, config)

            if files_differ(proto, dest):
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dry_run:
                    log(
                        f"[{processed}/{total_files}] DRY-RUN: {colorize(str(proto.relative_to(service.service_dir)), Color.YELLOW)} → {dest.relative_to(config.proto_root)}",
                        LogLevel.INFO,
                    )
                else:
                    shutil.copy2(proto, dest)
                    log(
                        f"[{processed}/{total_files}] 동기화: {colorize(service.name, Color.GREEN)} / {proto.name}",
                        LogLevel.SUCCESS,
                    )
                updates.setdefault(service.name, []).append(dest)

    if not updates:
        log("변경된 proto 파일이 없습니다.", LogLevel.INFO)
    else:
        log(
            f"\n총 {colorize(str(sum(len(v) for v in updates.values())), Color.BRIGHT_GREEN, bold=True)}개 파일 동기화 완료",
            LogLevel.SUCCESS,
        )

    return updates


def execute(args: argparse.Namespace, config: ProtoConfig) -> int:
    """Sync 명령 실행"""
    services = discover_services(config)

    if not services:
        log("발견된 서비스가 없습니다.", LogLevel.WARNING)
        return 1

    # 특정 서비스만 동기화
    if args.service:
        service = get_service_by_name(services, args.service)
        updates = sync_service_protos(service, config, dry_run=args.dry_run)
        return 0 if updates or args.dry_run else 1

    # 전체 서비스 동기화
    updates = sync_all_services(services, config, dry_run=args.dry_run)
    return 0 if updates or args.dry_run else 1


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Sync 명령 파서 설정"""
    parser.add_argument(
        "service",
        nargs="?",
        help="동기화할 서비스 이름 (생략 시 전체 동기화)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 동기화 없이 변경 사항만 출력",
    )
