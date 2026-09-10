#!/usr/bin/env python3
# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Kiểm phiên bản trong pyproject.toml khớp tag git (vX.Y.Z). Dùng trong workflow Release."""
import pathlib
import sys
import tomllib


def main(tag):
    version = tomllib.loads(pathlib.Path("pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    want = tag[1:] if tag.startswith("v") else tag
    if version != want:
        print(f"::error::pyproject.toml ghi version={version} nhưng tag là {tag}; sửa một trong hai trước khi phát hành")
        return 1
    print(f"OK: pyproject version {version} == tag {tag}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("dùng: check_version.py vX.Y.Z"); sys.exit(2)
    sys.exit(main(sys.argv[1]))
