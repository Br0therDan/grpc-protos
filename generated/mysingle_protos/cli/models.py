"""
Proto 서비스 관리를 위한 핵심 모델 및 함수.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ServiceProtoInfo:
    """서비스 Proto 정보"""

    name: str
    service_dir: Path
    proto_dir: Path
    files: list[Path]


@dataclass
class ProtoConfig:
    """Proto 저장소 설정"""

    repo_root: Path
    services_root: Path
    proto_root: Path
    generated_root: Path
    buf_template: Path
    package_name: str = "mysingle_protos"

    @classmethod
    def from_repo_root(
        cls, repo_root: Path, services_root: Path | None = None
    ) -> ProtoConfig:
        """저장소 루트 경로로부터 설정 생성"""
        if services_root is None:
            services_root = repo_root.parent / "services"

        return cls(
            repo_root=repo_root,
            services_root=services_root,
            proto_root=repo_root / "protos",
            generated_root=repo_root / "generated",
            buf_template=repo_root / "buf.gen.yaml",
        )
