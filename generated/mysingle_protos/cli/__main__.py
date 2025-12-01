"""
Proto CLI - gRPC Proto 파일 관리 도구.

사용법:
    proto-cli init              # 저장소 초기화 및 submodule 구성
    proto-cli status            # 서비스별 proto 파일 현황
    proto-cli generate          # 코드 생성
    proto-cli validate          # Proto 파일 검증
    proto-cli version           # 버전 정보
    proto-cli --help            # 도움말
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .commands import generate, init, status, validate, version
from .models import ProtoConfig
from .utils import Color, LogLevel, colorize, log


def get_repo_root() -> Path:
    """저장소 루트 디렉터리 찾기"""
    # CLI가 패키지로 설치된 경우
    current = Path.cwd()

    # grpc-protos 디렉터리 찾기
    for parent in [current, *current.parents]:
        if (parent / "protos").exists() and (parent / "buf.yaml").exists():
            return parent

    # 찾지 못한 경우 현재 디렉터리 사용
    return current


def build_parser() -> argparse.ArgumentParser:
    """CLI 파서 생성"""
    parser = argparse.ArgumentParser(
        prog="proto-cli",
        description="🔧 MySingle Quant - gRPC Proto 파일 관리 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s init                    # 저장소 환경 확인 / Submodule 구성
  %(prog)s status                  # 서비스별 proto 현황
  %(prog)s status -v               # 상세 파일 목록 포함
  %(prog)s validate --fix          # Proto 검증 및 자동 수정
  %(prog)s generate                # 코드 생성

더 자세한 정보:
  GitHub: https://github.com/Br0therDan/grpc-protos
        """,
    )

    parser.add_argument(
        "--services-root",
        type=Path,
        help="서비스 루트 디렉터리 경로 (기본값: ../services)",
    )

    # 서브커맨드
    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령")

    # init 명령
    init_parser = subparsers.add_parser(
        "init",
        help="저장소 초기화 및 환경 확인",
        description="grpc-protos 저장소를 초기화하고 필수 도구(Git, Buf) 설치를 확인합니다.",
    )
    init.setup_parser(init_parser)

    # status 명령
    status_parser = subparsers.add_parser(
        "status",
        help="서비스별 proto 파일 현황 확인",
        description="각 서비스의 proto 파일 개수와 경로를 테이블 형식으로 출력합니다.",
    )
    status.setup_parser(status_parser)

    # generate 명령
    generate_parser = subparsers.add_parser(
        "generate",
        help="Buf를 사용하여 Python gRPC 스텁 생성",
        description="proto 파일로부터 Python 코드를 생성하고 import 경로를 수정합니다.",
    )
    generate.setup_parser(generate_parser)

    # validate 명령
    validate_parser = subparsers.add_parser(
        "validate",
        help="Proto 파일 검증 (lint, format, breaking)",
        description="Buf를 사용하여 proto 파일의 린트, 포맷, Breaking change를 검사합니다.",
    )
    validate.setup_parser(validate_parser)

    # version 명령
    version_parser = subparsers.add_parser(
        "version",
        help="Proto 버전 정보 확인",
        description="현재 grpc-protos 버전과 Git 상태를 확인합니다.",
    )
    version.setup_parser(version_parser)

    # TODO: 추가 명령어 구현 예정
    # - pr: Pull Request 생성 자동화
    # - diff: Proto 변경사항 시각화

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 메인 함수"""
    parser = build_parser()
    args = parser.parse_args(argv)

    # 명령이 지정되지 않은 경우 도움말 출력
    if not args.command:
        parser.print_help()
        return 0

    # 저장소 설정
    try:
        repo_root = get_repo_root()
        config = ProtoConfig.from_repo_root(repo_root, services_root=args.services_root)
    except Exception as e:
        log(f"설정 로드 실패: {e}", LogLevel.ERROR)
        return 1

    # 명령 실행
    try:
        if args.command == "init":
            return init.execute(args, config)
        elif args.command == "status":
            return status.execute(args, config)
        elif args.command == "generate":
            return generate.execute(args, config)
        elif args.command == "validate":
            return validate.execute(args, config)
        elif args.command == "version":
            return version.execute(args, config)
        else:
            log(f"알 수 없는 명령: {args.command}", LogLevel.ERROR)
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        log("\n\n작업이 사용자에 의해 중단되었습니다.", LogLevel.WARNING)
        return 130
    except Exception as e:
        log(f"오류 발생: {e}", LogLevel.ERROR)
        if "--debug" in sys.argv:
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
