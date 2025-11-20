#!/usr/bin/env python3
"""Fix imports in generated gRPC files.

This script replaces relative imports with absolute imports for proper package structure.
Example: 'from protos.services.indicator.v1 import'
      -> 'from mysingle_protos.protos.services.indicator.v1 import'
"""

import re
from pathlib import Path


def fix_grpc_imports(file_path: Path) -> bool:
    """Fix imports in a single gRPC file.

    Args:
        file_path: Path to the gRPC file

    Returns:
        True if file was modified, False otherwise
    """
    content = file_path.read_text()
    original_content = content

    # Pattern 1: from protos. -> from mysingle_protos.protos.
    content = re.sub(r"from protos\.", "from mysingle_protos.protos.", content)

    # Pattern 2: import protos. -> import mysingle_protos.protos.
    content = re.sub(r"import protos\.", "import mysingle_protos.protos.", content)

    if content != original_content:
        file_path.write_text(content)
        return True
    return False


def main():
    """Fix all gRPC files in generated directory."""
    generated_dir = Path(__file__).parent.parent / "generated"

    if not generated_dir.exists():
        print(f"Error: {generated_dir} does not exist")
        return 1

    modified_files = []

    # Find all _pb2.py and _pb2_grpc.py files
    for pattern in ["*_pb2.py", "*_pb2_grpc.py"]:
        for grpc_file in generated_dir.rglob(pattern):
            if fix_grpc_imports(grpc_file):
                modified_files.append(grpc_file)
                print(f"✅ Fixed: {grpc_file.relative_to(generated_dir)}")

    if modified_files:
        print(f"\n✅ Total {len(modified_files)} files modified")
    else:
        print("\n✅ No files needed modification")

    return 0


if __name__ == "__main__":
    exit(main())
