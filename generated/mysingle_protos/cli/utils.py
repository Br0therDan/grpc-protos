"""
공통 유틸리티 함수 모듈.

색상 출력, 로깅, 테이블 포맷팅 등의 공통 기능을 제공합니다.
"""

from __future__ import annotations

import os
import sys
from enum import Enum


class Color(str, Enum):
    """ANSI 색상 코드"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # 기본 색상
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # 밝은 색상
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"


class LogLevel(str, Enum):
    """로그 레벨"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    STEP = "STEP"


def colorize(text: str, color: Color, bold: bool = False) -> str:
    """텍스트에 색상 적용"""
    # 터미널이 색상을 지원하지 않거나 파이프로 리다이렉트된 경우 색상 코드 생략
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return text
    prefix = f"{Color.BOLD.value}{color.value}" if bold else color.value
    return f"{prefix}{text}{Color.RESET.value}"


def log(msg: str, level: LogLevel = LogLevel.INFO) -> None:
    """로그 출력 (레벨별 색상 및 아이콘 적용)"""
    icons = {
        LogLevel.DEBUG: "🔍",
        LogLevel.INFO: "ℹ️ ",
        LogLevel.SUCCESS: "✅",
        LogLevel.WARNING: "⚠️ ",
        LogLevel.ERROR: "❌",
        LogLevel.STEP: "📋",
    }
    colors = {
        LogLevel.DEBUG: Color.DIM,
        LogLevel.INFO: Color.CYAN,
        LogLevel.SUCCESS: Color.GREEN,
        LogLevel.WARNING: Color.YELLOW,
        LogLevel.ERROR: Color.RED,
        LogLevel.STEP: Color.BRIGHT_BLUE,
    }
    icon = icons.get(level, "  ")
    color = colors.get(level, Color.RESET)

    if level == LogLevel.STEP:
        print(colorize(f"\n{icon} {msg}", color, bold=True), flush=True)
    else:
        print(f"{icon} {colorize(msg, color)}", flush=True)


def log_header(title: str) -> None:
    """섹션 헤더 출력"""
    border = "=" * 60
    print()
    print(colorize(border, Color.BRIGHT_CYAN, bold=True))
    print(colorize(f"  {title}", Color.BRIGHT_CYAN, bold=True))
    print(colorize(border, Color.BRIGHT_CYAN, bold=True))
    print()


def log_table(headers: list[str], rows: list[list[str]]) -> None:
    """테이블 형식으로 출력"""
    if not rows:
        return

    # 각 컬럼의 최대 너비 계산
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # 헤더 출력
    header_line = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(colorize(header_line, Color.BRIGHT_CYAN, bold=True))
    print(colorize("-" * len(header_line), Color.CYAN))

    # 데이터 행 출력
    for row in rows:
        row_line = "  ".join(
            str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)
        )
        print(row_line)
    print()
