#!/usr/bin/env python3
# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Kiểm header SPDX trong 4 dòng đầu của các tệp được truyền vào (dùng cho pre-commit).
Cùng quy tắc với tests/test_spdx.py."""
import pathlib
import sys

COMMENT = {".sql": "--"}


def main(paths):
    bad = []
    for p in map(pathlib.Path, paths):
        c = COMMENT.get(p.suffix, "#")
        head = p.read_text(encoding="utf-8", errors="replace").splitlines()[:4]
        if f"{c} Copyright (c) 2026 ICTU-CRIS contributors" not in head or f"{c} SPDX-License-Identifier: Apache-2.0" not in head:
            bad.append(str(p))
    for b in bad:
        print(f"thiếu header SPDX: {b}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
