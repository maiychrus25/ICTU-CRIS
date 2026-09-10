import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXT = {".py", ".sql", ".sh", ".yml", ".yaml"}
COMMENT = {".sql": "--"}

def tracked_source_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / p for p in out.split() if pathlib.Path(p).suffix in EXT]

def test_every_source_file_has_spdx_header():
    missing = []
    for path in tracked_source_files():
        c = COMMENT.get(path.suffix, "#")
        head = path.read_text(encoding="utf-8").splitlines()[:4]
        want1 = f"{c} Copyright (c) 2026 ICTU-CRIS contributors"
        want2 = f"{c} SPDX-License-Identifier: Apache-2.0"
        if want1 not in head or want2 not in head:
            missing.append(str(path.relative_to(ROOT)))
    assert missing == [], "thiếu header SPDX: " + ", ".join(missing)
