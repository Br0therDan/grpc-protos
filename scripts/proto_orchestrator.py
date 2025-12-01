#!/usr/bin/env python3
"""통합 프로토 오케스트레이션 유틸리티 (Interactive Workflow)"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SERVICES_ROOT = REPO_ROOT.parent / "services"
PROTO_ROOT = REPO_ROOT / "protos"
RELEASE_NOTES_NAME = "RELEASE.md"
GENERATED_ROOT = REPO_ROOT / "generated"
BUF_TEMPLATE = REPO_ROOT / "buf.gen.yaml"
PYTHON_BIN = os.environ.get("PYTHON") or sys.executable
PACKAGE_NAME = "mysingle_protos"


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


@dataclass
class ServiceProtoInfo:
    name: str
    service_dir: Path
    proto_dir: Path
    files: list[Path]


def colorize(text: str, color: Color, bold: bool = False) -> str:
    """텍스트에 색상 적용"""
    if not sys.stdout.isatty():
        return text
    prefix = f"{Color.BOLD}{color}" if bold else color
    return f"{prefix}{text}{Color.RESET}"


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

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    def format_row(cells: list[str], is_header: bool = False) -> str:
        formatted = " | ".join(
            str(cell).ljust(width) for cell, width in zip(cells, col_widths)
        )
        if is_header:
            return colorize(formatted, Color.BRIGHT_YELLOW, bold=True)
        return formatted

    separator = "-+-".join("-" * w for w in col_widths)

    print(format_row(headers, is_header=True))
    print(colorize(separator, Color.DIM))
    for row in rows:
        print(format_row(row))
    print()


def run_cmd(
    cmd: list[str], cwd: Path | None = None, check: bool = True
) -> subprocess.CompletedProcess:
    display = " ".join(cmd)
    where = f" (작업 디렉터리: {cwd})" if cwd else ""
    log(
        f"💻 명령 실행: {colorize(display, Color.BRIGHT_YELLOW)}{where}", LogLevel.DEBUG
    )
    return subprocess.run(cmd, cwd=cwd, check=check)


def discover_services(services_root: Path) -> list[ServiceProtoInfo]:
    if not services_root.exists():
        raise SystemExit(f"서비스 루트 디렉터리를 찾을 수 없습니다: {services_root}")

    log_header("서비스 스캔")
    result: list[ServiceProtoInfo] = []
    skipped = 0

    for service_dir in sorted(p for p in services_root.iterdir() if p.is_dir()):
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


def get_service_by_name(
    services: Sequence[ServiceProtoInfo], name: str
) -> ServiceProtoInfo:
    for service in services:
        if service.name == name:
            return service
    available = ", ".join(s.name for s in services[:5])
    raise SystemExit(
        f"서비스 '{name}'을(를) 찾을 수 없습니다. 사용 가능한 서비스: {available}..."
    )


def relative_destination(proto_file: Path, service: ServiceProtoInfo) -> Path:
    try:
        rel = proto_file.relative_to(service.proto_dir)
    except ValueError as exc:  # pragma: no cover - guardrail
        raise RuntimeError(f"{proto_file} is not under {service.proto_dir}") from exc
    return PROTO_ROOT / rel


def files_differ(src: Path, dest: Path) -> bool:
    if not dest.exists():
        return True
    return src.read_bytes() != dest.read_bytes()


def ensure_file_exists(path: Path, description: str) -> None:
    if not path.exists():
        raise SystemExit(f"필수 파일 누락: {description} ({path})")


def buf_generate(template_path: Path = BUF_TEMPLATE) -> None:
    ensure_file_exists(template_path, "buf.gen.yaml 템플릿")
    log("Buf를 사용하여 코드 생성 중...", LogLevel.STEP)
    run_cmd(["buf", "generate", "--template", str(template_path)], cwd=REPO_ROOT)
    log("코드 생성 완료", LogLevel.SUCCESS)


def rewrite_generated_imports(generated_dir: Path) -> list[Path]:
    if not generated_dir.exists():
        return []

    log("생성된 파일의 import 경로 수정 중...", LogLevel.STEP)
    patterns = ("*_pb2.py", "*_pb2_grpc.py")
    replacements = [
        (re.compile(r"from protos\."), "from mysingle_protos.protos."),
        (re.compile(r"import protos\."), "import mysingle_protos.protos."),
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


def detect_python_output_dir(generated_root: Path = GENERATED_ROOT) -> Path:
    preferred = generated_root / PACKAGE_NAME
    legacy = generated_root / "python" / PACKAGE_NAME
    if preferred.exists():
        return preferred
    if legacy.exists():
        return legacy
    for candidate in generated_root.iterdir() if generated_root.exists() else []:
        if not candidate.is_dir():
            continue
        if (candidate / "protos").exists() or any(
            (candidate / name).exists() for name in ("setup.py", "pyproject.toml")
        ):
            return candidate
    raise SystemExit(
        f"ERROR: expected generated python output under {generated_root} (no suitable package found)"
    )


def ensure_pip_available(python_bin: str) -> None:
    try:
        subprocess.run(
            [python_bin, "-m", "pip", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    except subprocess.CalledProcessError:
        pass

    log(f"pip not found for {python_bin} — attempting to bootstrap via ensurepip")
    ensure_result = subprocess.run(
        [python_bin, "-m", "ensurepip", "--upgrade"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if ensure_result.returncode == 0:
        log("bootstrapped pip via ensurepip")
        return

    log("ensurepip failed — attempting to install via get-pip")
    bootstrap_code = """
import subprocess, sys, urllib.request
data = urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py').read()
subprocess.run([sys.executable, '-c', data], check=True)
"""
    try:
        subprocess.run(
            [python_bin, "-c", bootstrap_code], check=True, stdout=subprocess.DEVNULL
        )
    except Exception as exc:  # pragma: no cover - network restrictions
        raise SystemExit(
            "ERROR: cannot bootstrap pip (network disabled). Please install pip."
        ) from exc


def pip_version_tuple(python_bin: str) -> tuple[int, ...] | None:
    try:
        result = subprocess.run(
            [python_bin, "-m", "pip", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return None
    parts = result.stdout.strip().split()
    if len(parts) < 2:
        return None
    version_str = parts[1]
    try:
        return tuple(int(piece) for piece in version_str.split(".") if piece.isdigit())
    except ValueError:
        return None


def pip_supports_break_system_packages(python_bin: str) -> bool:
    version = pip_version_tuple(python_bin)
    if version is None:
        return False
    return version >= (23, 3)


def pip_install_flags(python_bin: str) -> list[str]:
    flags: list[str] = []
    if pip_supports_break_system_packages(python_bin):
        flags.append("--break-system-packages")
    if not os.environ.get("VIRTUAL_ENV") and not os.environ.get("CONDA_PREFIX"):
        flags.append("--user")
    return flags


def ensure_setup_metadata(pkg_dir: Path) -> None:
    setup_path = pkg_dir / "setup.py"
    init_path = pkg_dir / "__init__.py"
    if not init_path.exists():
        init_path.write_text("# auto-generated init\n", encoding="utf-8")
    if setup_path.exists() or (pkg_dir / "pyproject.toml").exists():
        return
    setup_path.write_text(
        """
from pathlib import Path
from setuptools import find_packages, setup

package_root = Path(__file__).parent
packages = [pkg for pkg in find_packages(where=str(package_root)) if pkg.startswith('mysingle_protos')]

setup(
    name="mysingle_protos",
    version="0.0.0",
    packages=packages,
    package_dir={"": "."},
    include_package_data=True,
)
""".strip()
        + "\n",
        encoding="utf-8",
    )


def install_editable_package(
    pkg_dir: Path, python_bin: str, flags: Sequence[str]
) -> None:
    ensure_setup_metadata(pkg_dir)
    cmd = [python_bin, "-m", "pip", "install", *flags, "-e", str(pkg_dir)]
    run_cmd(cmd)


def sync_service_protos(
    services: Iterable[ServiceProtoInfo], dry_run: bool = False
) -> dict[str, list[Path]]:
    updates: dict[str, list[Path]] = {}
    for service in services:
        for proto in service.files:
            dest = relative_destination(proto, service)
            if files_differ(proto, dest):
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dry_run:
                    log(f"DRY-RUN would copy {proto} -> {dest}")
                else:
                    shutil.copy2(proto, dest)
                    log(
                        f"📄 Synced {proto.relative_to(service.service_dir)} -> {dest.relative_to(PROTO_ROOT)}"
                    )
                updates.setdefault(service.name, []).append(dest)
    if not updates:
        log("No proto changes detected.")
    return updates


def update_release_notes(
    service: ServiceProtoInfo,
    version: str | None,
    files: list[Path],
    dry_run: bool = False,
) -> None:
    if not files:
        return
    notes_path = service.proto_dir / RELEASE_NOTES_NAME
    if dry_run:
        log(f"DRY-RUN would update {notes_path} for {service.name}")
        return
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = "# Proto Release Notes\n\n" if not notes_path.exists() else ""
    version_label = f"v{version}" if version else "(unreleased)"
    entry = f"- {timestamp} — synced to mysingle-protos {version_label}\n"
    entry += (
        "  - files: " + ", ".join(str(f.relative_to(PROTO_ROOT)) for f in files) + "\n"
    )
    with notes_path.open("a", encoding="utf-8") as fh:
        if header:
            fh.write(header)
        fh.write(entry)
    log(f"📝 Updated release notes for {service.name}")


def get_current_proto_version() -> str | None:
    path = REPO_ROOT / "pyproject.toml"
    content = path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"\n]+)"', content, flags=re.MULTILINE)
    return match.group(1) if match else None


def update_proto_version(new_version: str, dry_run: bool = False) -> None:
    path = REPO_ROOT / "pyproject.toml"
    content = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'^(version\s*=\s*")([^"\n]+)(")',
        f"\\g<1>{new_version}\\3",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if count == 0:
        raise SystemExit("Failed to bump version in pyproject.toml")
    if dry_run:
        log(f"DRY-RUN would set mysingle-protos version to {new_version}")
        return
    path.write_text(updated, encoding="utf-8")
    log(f"🏷️ Updated mysingle-protos version -> {new_version}")


def update_service_dependencies(
    services: Iterable[ServiceProtoInfo], version: str, dry_run: bool = False
) -> list[str]:
    updated: list[str] = []
    pattern = re.compile(
        r'(mysingle-protos\s*@\s*git\+https://github\.com/Br0therDan/grpc-protos\.git)@([^"\s]+)'
    )
    repl = lambda m: f"{m.group(1)}@v{version}"
    for service in services:
        pyproject = service.service_dir / "pyproject.toml"
        if not pyproject.exists():
            continue
        content = pyproject.read_text(encoding="utf-8")
        new_content, count = pattern.subn(repl, content)
        if count == 0:
            continue
        if dry_run:
            log(f"DRY-RUN would pin {service.name} to mysingle-protos v{version}")
        else:
            pyproject.write_text(new_content, encoding="utf-8")
            log(f"🔗 Updated {service.name} dependency -> v{version}")
        updated.append(service.name)
    return updated


def run_buf_suite(dry_run: bool = False) -> None:
    if dry_run:
        log("DRY-RUN would execute buf format/lint/breaking")
        return
    run_cmd(["buf", "format", "-w"], cwd=REPO_ROOT)
    run_cmd(["buf", "lint"], cwd=REPO_ROOT)
    run_cmd(["buf", "breaking", "--against", ".git#branch=main"], cwd=REPO_ROOT)


def regenerate_python_stubs(
    dry_run: bool = False,
    *,
    install: bool = True,
    python_bin: str = PYTHON_BIN,
) -> Path | None:
    if dry_run:
        log("DRY-RUN would regenerate python stubs")
        return None

    log(f"🔧 Generating Python protobuf stubs (cwd: {REPO_ROOT})...")
    buf_generate(BUF_TEMPLATE)
    rewrite_generated_imports(GENERATED_ROOT)
    pkg_dir = detect_python_output_dir(GENERATED_ROOT)

    if install:
        ensure_pip_available(python_bin)
        flags = pip_install_flags(python_bin)
        flag_str = " ".join(flags) if flags else ""
        log(
            "> Installing generated package (editable) using: "
            f"{python_bin} -m pip install {flag_str} -e {pkg_dir}"
        )
        install_editable_package(pkg_dir, python_bin, flags)
        log("✅ Python stubs generated and installed (editable).")
        log(f"📦 Package location: {pkg_dir}")
        log(
            "🔍 Quick import test: "
            f'\n  {python_bin} -c "from {PACKAGE_NAME}.protos.services.backtest.v1 '
            "import backtest_service_pb2_grpc; print('import ok')\""
        )
    else:
        log("✅ Python stubs generated (installation skipped).")

    return pkg_dir


def run_uv_sync(services: Iterable[ServiceProtoInfo], dry_run: bool = False) -> None:
    for service in services:
        if not (service.service_dir / "pyproject.toml").exists():
            continue
        if dry_run:
            log(f"DRY-RUN would run 'uv sync' in {service.name}")
            continue
        run_cmd(["uv", "sync"], cwd=service.service_dir)


def ensure_clean_git_tree(dry_run: bool = False) -> None:
    if dry_run:
        log("DRY-RUN would verify clean git status")
        return
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    if result.stdout.strip():
        raise SystemExit(
            "Error: working tree is not clean. Commit or stash changes before publishing."
        )


def ensure_tag_absent(version: str, dry_run: bool = False) -> None:
    tag = f"v{version}"
    if dry_run:
        log(f"DRY-RUN would ensure tag {tag} is absent")
        return
    result = subprocess.run(
        ["git", "rev-parse", tag],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        raise SystemExit(f"Error: tag {tag} already exists")


def git_commit_all(message: str, dry_run: bool = False) -> None:
    if dry_run:
        log(f"DRY-RUN would commit with message: {message}")
        return
    run_cmd(["git", "add", "-A"], cwd=REPO_ROOT)
    commit_result = subprocess.run(
        ["git", "commit", "-m", message], cwd=REPO_ROOT, capture_output=True, text=True
    )
    if commit_result.returncode != 0:
        log(commit_result.stdout.strip())
        log(commit_result.stderr.strip())
        raise SystemExit("git commit failed. Ensure there are staged changes.")


def git_tag_and_push(version: str, dry_run: bool = False) -> None:
    tag = f"v{version}"
    if dry_run:
        log(f"DRY-RUN would tag {tag} and push to origin")
        return
    run_cmd(["git", "tag", "-a", tag, "-m", f"Release {tag}"], cwd=REPO_ROOT)
    run_cmd(["git", "push", "origin", "HEAD"], cwd=REPO_ROOT)
    run_cmd(["git", "push", "origin", tag], cwd=REPO_ROOT)


def service_dependency_version(pyproject: Path) -> tuple[str | None, str | None]:
    if not pyproject.exists():
        return None, None
    for line in pyproject.read_text(encoding="utf-8").splitlines():
        if "mysingle-protos" not in line:
            continue
        version_match = re.search(r"@v([0-9.]+)", line)
        version = version_match.group(1) if version_match else None
        return line.strip(), version
    return None, None


def check_version_consistency(services_root: Path) -> None:
    proto_version = get_current_proto_version()
    if not proto_version:
        raise SystemExit(
            "Unable to determine mysingle-protos version from pyproject.toml"
        )
    log(f"Current proto version: {proto_version}")
    services = discover_services(services_root)
    mismatches: list[str] = []
    for service in services:
        pyproject = service.service_dir / "pyproject.toml"
        dep_line, version = service_dependency_version(pyproject)
        if not dep_line:
            continue
        log(f"- {service.name}: {dep_line}")
        if version and version != proto_version:
            mismatches.append(
                f"{service.name} pinned to v{version} while proto repo is v{proto_version}"
            )
        elif not version:
            log("  ℹ️  Using branch reference (development mode)")
    if mismatches:
        log("")
        log("❌ Proto version inconsistency detected!")
        for mismatch in mismatches:
            log(f"  - {mismatch}")
        raise SystemExit(1)
    log("")
    log("✅ All services are using consistent proto versions")


def buf_breaking_check(dry_run: bool = False) -> None:
    if dry_run:
        log("DRY-RUN would execute buf breaking")
        return
    run_cmd(["buf", "breaking", "--against", ".git#branch=main"], cwd=REPO_ROOT)


def service_has_proto_imports(service_dir: Path) -> bool:
    app_dir = service_dir / "app"
    if not app_dir.exists():
        return False
    for file_path in app_dir.rglob("*.py"):
        try:
            if "mysingle_protos" in file_path.read_text(encoding="utf-8"):
                return True
        except UnicodeDecodeError:  # pragma: no cover - non-utf8 file
            continue
    return False


def install_service_dependencies(service_dir: Path, python_bin: str) -> None:
    ensure_pip_available(python_bin)
    flags = pip_install_flags(python_bin)
    cmd = [python_bin, "-m", "pip", "install", *flags, "-e", "."]
    run_cmd(cmd, cwd=service_dir)


def validate_service_imports(
    service: ServiceProtoInfo,
    *,
    install_deps: bool = False,
    python_bin: str = PYTHON_BIN,
) -> None:
    log(f"Validating gRPC proto imports in {service.name}...")
    if install_deps:
        log(f"Installing dependencies for {service.name} via pip...")
        install_service_dependencies(service.service_dir, python_bin)
    if not service_has_proto_imports(service.service_dir):
        log("ℹ️  No gRPC proto imports found (HTTP-only service)")
        return
    try:
        subprocess.run(
            [
                python_bin,
                "-c",
                "from mysingle_protos.protos.common import metadata_pb2; print('✅ Common protos import successful')",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"❌ Failed to import mysingle_protos inside {service.name}: {exc}"
        ) from exc


def status_command(services_root: Path) -> None:
    services = discover_services(services_root)
    version = get_current_proto_version()
    log(
        f"Detected {len(services)} services. Current mysingle-protos version: {version or 'unknown'}"
    )
    for svc in services:
        log(f"- {svc.name}: {len(svc.files)} proto files")
    log("\nDiff preview:")
    sync_service_protos(services, dry_run=True)


def sync_command(services_root: Path, dry_run: bool = False) -> dict[str, list[Path]]:
    services = discover_services(services_root)
    updates = sync_service_protos(services, dry_run=dry_run)
    for service in services:
        update_release_notes(
            service, None, updates.get(service.name, []), dry_run=dry_run
        )
    return updates


def release_command(
    services_root: Path,
    version: str,
    *,
    dry_run: bool = False,
    skip_buf: bool = False,
    skip_codegen: bool = False,
    install_stubs: bool = True,
    uv_sync_enabled: bool = False,
) -> None:
    services = discover_services(services_root)
    updates = sync_service_protos(services, dry_run=dry_run)
    # Run validations/codegen before mutating downstream files so failures leave a clean tree.
    if not skip_buf:
        run_buf_suite(dry_run=dry_run)
    if not skip_codegen:
        regenerate_python_stubs(dry_run=dry_run, install=install_stubs)
    for service in services:
        update_release_notes(
            service, version, updates.get(service.name, []), dry_run=dry_run
        )
    update_proto_version(version, dry_run=dry_run)
    update_service_dependencies(services, version, dry_run=dry_run)
    if uv_sync_enabled:
        run_uv_sync(services, dry_run=dry_run)


def publish_release(
    services_root: Path,
    version: str,
    *,
    dry_run: bool = False,
    skip_buf: bool = False,
    skip_codegen: bool = False,
    skip_install: bool = True,
    uv_sync_enabled: bool = False,
    commit_message: str | None = None,
) -> None:
    ensure_clean_git_tree(dry_run=dry_run)
    ensure_tag_absent(version, dry_run=dry_run)
    release_command(
        services_root,
        version,
        dry_run=dry_run,
        skip_buf=skip_buf,
        skip_codegen=skip_codegen,
        install_stubs=not skip_install,
        uv_sync_enabled=uv_sync_enabled,
    )
    if dry_run:
        log("DRY-RUN publish complete — skipping git commit/tag")
        return
    message = commit_message or f"chore(release): v{version}"
    git_commit_all(message, dry_run=False)
    git_tag_and_push(version, dry_run=False)


def prompt(prompt_text: str) -> str:
    try:
        return input(prompt_text)
    except EOFError:  # pragma: no cover - interactive fallback
        return ""


def prompt_choice(prompt_text: str, choices: dict[str, str]) -> str:
    while True:
        answer = prompt(prompt_text).strip()
        if answer in choices:
            return answer
        log(f"Please choose one of {', '.join(choices)}")


def prompt_yes_no(prompt_text: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        answer = prompt(f"{prompt_text} {suffix} ").strip().lower()
        if not answer:
            return default
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        log("Please answer y or n")


def interactive_flow(services_root: Path) -> None:
    log("Proto Orchestrator Interactive Mode")
    choices = {
        "1": "Status",
        "2": "Sync",
        "3": "Release",
        "4": "Publish",
        "5": "Exit",
    }
    while True:
        for key, label in choices.items():
            log(f"{key}. {label}")
        selection = prompt_choice("Select an option: ", choices)
        if selection == "1":
            status_command(services_root)
        elif selection == "2":
            dry_run = prompt_yes_no("Dry-run sync only?", default=True)
            sync_command(services_root, dry_run=dry_run)
        elif selection == "3":
            version = prompt("New mysingle-protos version (e.g. 2.0.3): ").strip()
            if not version:
                log("Version is required for release.")
                continue
            dry_run = prompt_yes_no("Execute as dry-run?", default=False)
            run_buf = prompt_yes_no("Run buf validation?", default=True)
            run_codegen = prompt_yes_no("Regenerate Python stubs?", default=True)
            install_stubs = False
            if run_codegen:
                install_stubs = prompt_yes_no(
                    "Install generated Python stubs locally?", default=True
                )
            uv_choice = prompt_yes_no(
                "Run 'uv sync' for all services after release?", default=False
            )
            release_command(
                services_root,
                version,
                dry_run=dry_run,
                skip_buf=not run_buf,
                skip_codegen=not run_codegen,
                install_stubs=install_stubs,
                uv_sync_enabled=uv_choice,
            )
        elif selection == "4":
            version = prompt("Release version (e.g. 2.0.3): ").strip()
            if not version:
                log("Version is required for publish.")
                continue
            dry_run = prompt_yes_no("Execute as dry-run?", default=False)
            run_buf = prompt_yes_no("Run buf validation?", default=True)
            run_codegen = prompt_yes_no("Regenerate Python stubs?", default=True)
            install_stubs = False
            if run_codegen:
                install_stubs = prompt_yes_no(
                    "Install generated Python stubs locally?", default=False
                )
            uv_choice = prompt_yes_no(
                "Run 'uv sync' for all services after release?", default=False
            )
            commit_message = prompt(
                "Commit message (default: chore(release): v<version>): "
            ).strip()
            publish_release(
                services_root,
                version,
                dry_run=dry_run,
                skip_buf=not run_buf,
                skip_codegen=not run_codegen,
                skip_install=not install_stubs,
                uv_sync_enabled=uv_choice,
                commit_message=commit_message or None,
            )
        else:
            log("Exiting interactive mode.")
            return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="mysingle proto orchestrator")
    parser.add_argument(
        "--services-root",
        default=str(DEFAULT_SERVICES_ROOT),
        help="Path to the services directory (default: ../services)",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Preview proto changes without touching files")

    sync_parser = subparsers.add_parser(
        "sync", help="Copy service protos into grpc-protos"
    )
    sync_parser.add_argument(
        "--dry-run", action="store_true", help="Log planned copies only"
    )

    release_parser = subparsers.add_parser(
        "release", help="Perform a tagged release flow"
    )
    release_parser.add_argument(
        "--version", required=True, help="New mysingle-protos version (e.g. 2.0.3)"
    )
    release_parser.add_argument(
        "--dry-run", action="store_true", help="Print steps without touching files"
    )
    release_parser.add_argument(
        "--skip-buf", action="store_true", help="Skip buf format/lint/breaking checks"
    )
    release_parser.add_argument(
        "--skip-codegen", action="store_true", help="Skip python stub regeneration"
    )
    release_parser.add_argument(
        "--skip-stub-install",
        action="store_true",
        help="Skip installing generated python package after codegen",
    )
    release_parser.add_argument(
        "--uv-sync",
        action="store_true",
        help="Run 'uv sync' across every service after release",
    )

    codegen_parser = subparsers.add_parser(
        "codegen", help="Generate Python stubs via buf"
    )
    codegen_parser.add_argument(
        "--dry-run", action="store_true", help="Log actions without executing"
    )
    codegen_parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip installing the generated package after codegen",
    )

    publish_parser = subparsers.add_parser(
        "publish", help="Perform release flow plus git tagging/push"
    )
    publish_parser.add_argument(
        "--version", required=True, help="Release version (e.g. 2.0.4)"
    )
    publish_parser.add_argument(
        "--dry-run", action="store_true", help="Print steps without touching git"
    )
    publish_parser.add_argument(
        "--skip-buf", action="store_true", help="Skip buf format/lint/breaking checks"
    )
    publish_parser.add_argument(
        "--skip-codegen", action="store_true", help="Skip python stub regeneration"
    )
    publish_parser.add_argument(
        "--install-stubs",
        action="store_true",
        help="Install generated python package locally (default: skip)",
    )
    publish_parser.add_argument(
        "--uv-sync",
        action="store_true",
        help="Run 'uv sync' across every service after release",
    )
    publish_parser.add_argument(
        "--commit-message",
        help="Override default commit message (chore/release): v<version>",
    )

    subparsers.add_parser(
        "check-versions", help="Ensure all services use the current proto version"
    )

    breaking_parser = subparsers.add_parser(
        "breaking", help="Run buf breaking against main"
    )
    breaking_parser.add_argument(
        "--dry-run", action="store_true", help="Log the command without executing"
    )

    validate_parser = subparsers.add_parser(
        "validate-imports", help="Validate mysingle_protos imports for a service"
    )
    validate_parser.add_argument(
        "--service",
        required=True,
        help="Service name under services/ (e.g. strategy-service)",
    )
    validate_parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install service dependencies via pip before validation",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    services_root = Path(args.services_root).resolve()

    if not args.command:
        interactive_flow(services_root)
        return

    if args.command == "status":
        status_command(services_root)
        return

    if args.command == "sync":
        sync_command(services_root, dry_run=args.dry_run)
        return

    if args.command == "codegen":
        regenerate_python_stubs(
            dry_run=args.dry_run,
            install=not args.skip_install,
            python_bin=PYTHON_BIN,
        )
        return

    if args.command == "release":
        release_command(
            services_root,
            args.version,
            dry_run=args.dry_run,
            skip_buf=args.skip_buf,
            skip_codegen=args.skip_codegen,
            install_stubs=not args.skip_stub_install,
            uv_sync_enabled=args.uv_sync,
        )
        return

    if args.command == "publish":
        publish_release(
            services_root,
            args.version,
            dry_run=args.dry_run,
            skip_buf=args.skip_buf,
            skip_codegen=args.skip_codegen,
            skip_install=not args.install_stubs,
            uv_sync_enabled=args.uv_sync,
            commit_message=args.commit_message,
        )
        return

    if args.command == "check-versions":
        check_version_consistency(services_root)
        return

    if args.command == "breaking":
        buf_breaking_check(dry_run=args.dry_run)
        return

    if args.command == "validate-imports":
        services = discover_services(services_root)
        service = get_service_by_name(services, args.service)
        validate_service_imports(
            service, install_deps=args.install_deps, python_bin=PYTHON_BIN
        )
        return

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
