#!/usr/bin/env python3
# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Chặn thông điệp commit có dòng ghi công AI (Co-Authored-By: Claude/…, "Generated with").

Dùng hai cách:
- CI: `python scripts/check_commit_trailers.py <base>..<head>` quét mọi commit trong khoảng.
- Hook commit-msg (pre-commit): `python scripts/check_commit_trailers.py --file .git/COMMIT_EDITMSG`.
Quy tắc dự án (CONTRIBUTING.md): thông điệp commit không có trailer ghi công AI.
"""
import re
import subprocess
import sys

BANNED = re.compile(r"^(Co-Authored-By:.*(claude|anthropic|codex|openai|gpt|copilot)|.*Generated with \[?Claude Code)", re.I | re.M)


def check(msg: str) -> list[str]:
    return [m.group(0).strip() for m in BANNED.finditer(msg)]


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "--file":
        hits = check(open(argv[1], encoding="utf-8").read())
        if hits:
            print("✘ thông điệp commit chứa dòng ghi công AI (quy tắc dự án):", *hits, sep="\n  ")
            return 1
        return 0
    rng = argv[0] if argv else "HEAD~1..HEAD"
    out = subprocess.run(["git", "log", "--format=%H%x00%B%x1e", rng], capture_output=True, text=True, check=True).stdout
    bad = []
    for rec in filter(None, out.split("\x1e")):
        sha, _, body = rec.strip("\n").partition("\x00")
        if check(body):
            bad.append(sha[:10])
    if bad:
        print(f"::error::{len(bad)} commit có dòng ghi công AI trong thông điệp: {', '.join(bad)} — viết lại thông điệp (git commit --amend / rebase) rồi đẩy lại")
        return 1
    print(f"OK: không có trailer ghi công AI trong {rng}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
