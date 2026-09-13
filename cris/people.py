# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import hashlib
import re
from datetime import datetime

import psycopg

from cris import audit
from cris import rules as RU
from cris.db import tx

# `jobTitle` ở kho nguồn là CHỨC VỤ, không phải đơn vị (lát cắt M — đơn vị thật
# nay đọc từ bộ lọc `dept` của kho, xem cris/normalize.py và migration 0020).
# Chuẩn hoá vài biến thể thường gặp; giá trị lạ vẫn giữ nguyên làm chức vụ,
# KHÔNG suy ra/tạo đơn vị từ đây nữa (đó là việc của assign_units_by_works).
POSITION_NORMALIZE = {
    "hiệu trưởng": "Hiệu trưởng",
    "phó hiệu trưởng": "Phó Hiệu trưởng",
    "hiệu phó": "Phó Hiệu trưởng",
    "trưởng khoa": "Trưởng khoa",
    "phó trưởng khoa": "Phó Trưởng khoa",
    "phó khoa": "Phó Trưởng khoa",
    "trưởng phòng": "Trưởng phòng",
    "phó trưởng phòng": "Phó Trưởng phòng",
    "trưởng bộ môn": "Trưởng bộ môn",
    "phó trưởng bộ môn": "Phó Trưởng bộ môn",
    "giảng viên": "Giảng viên",
    "giảng viên chính": "Giảng viên chính",
    "trợ giảng": "Trợ giảng",
}


def position_from_job_title(job_title):
    """Chuẩn hoá `jobTitle` (chức vụ) của nguồn — biến thể đã biết (vd "Hiệu phó")
    map về dạng chuẩn; giá trị khác giữ nguyên (chỉ gọn khoảng trắng). `None`/rỗng
    → `None`."""
    squashed = " ".join((job_title or "").split())
    key = squashed.lower()
    if not key:
        return None
    return POSITION_NORMALIZE.get(key, squashed)


def ensure_unit(conn, name):
    name = (name or "").strip()
    if not name:
        return None
    with conn.cursor() as cur:
        cur.execute("""SELECT id FROM unit WHERE name=%s OR code=%s OR %s = ANY(aliases)
                       ORDER BY (name = %s) DESC, (code = %s) DESC LIMIT 1""",
                    (name, name, name, name, name))
        row = cur.fetchone()
        if row:
            return row["id"]
        code = re.sub(r"[^A-Z0-9]", "", RU.strip_accents(name).upper())[:16] or "UNIT"
        cur.execute("SELECT 1 FROM unit WHERE code=%s", (code,))
        if cur.fetchone():
            code = code[:12] + hashlib.sha1(name.encode("utf-8")).hexdigest()[:4].upper()
        cur.execute("INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", (code, name))
        return cur.fetchone()["id"]

def _dob(s):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime((s or "").strip(), fmt).date()
        except ValueError:
            pass
    return None

def import_people(conn):
    rules = RU.load_active(conn)
    nb = rules["name_norm"][1]
    out = {"created": 0, "updated": 0, "errors": []}
    with tx(conn), conn.cursor() as cur:
        cur.execute("""SELECT s.* FROM source_record s WHERE s.doc_type='giang_vien' AND s.status='active'
                       AND s.version=(SELECT max(version) FROM source_record x WHERE x.source=s.source AND x.source_key=s.source_key)
                       ORDER BY s.id""")
        for rec in cur.fetchall():
            try:
                with conn.transaction():
                    a = rec["raw"]["archive"]
                    # `display` ở nguồn giữ đúng hoa/thường ("PGS.TS. Phùng Trung Nghĩa"), còn
                    # `name` thường là chữ thường (slug) — ưu tiên display cho tên hiển thị.
                    raw_name = a.get("display") or a.get("name") or ""
                    nn, deg = RU.norm_name(a.get("name") or raw_name, nb)
                    display = re.sub(r"\s+", " ", raw_name).strip()
                    for canon, variants in nb["prefixes"].items():
                        matched = next((v for v in variants if display.lower().startswith(v + " ")), None)
                        if matched:
                            display = display[len(matched):].strip()
                            break
                    display = RU.title_case_name(display)
                    # jobTitle là CHỨC VỤ (lát cắt M) → person.position; KHÔNG suy/gán đơn vị
                    # từ đây nữa — đơn vị nay đến từ assign_units_by_works (đa số công trình
                    # đã liên kết) hoặc gán tay (cris.units.set_person_unit), xem migration 0020.
                    position = position_from_job_title(a.get("jobTitle"))
                    # `rank` (học hàm GS/PGS, khác `degree_raw` học vị): ngoại lệ tối thiểu
                    # ngoài phạm vi K1 thường không sửa `cris.people` — chỉ dòng vals dưới đây,
                    # cột mới ở migration 0016 (nguồn: archive.rank, xem cris/source/repository.py).
                    vals = dict(display_name=display, name_norm=nn, degree_raw=a.get("degree") or deg,
                                email=a.get("email"), orcid=(rec["raw"].get("detail") or {}).get("orcid") or a.get("orcid"),
                                phone=a.get("phone"), dob=_dob(a.get("dob")), rank=a.get("rank"), position=position)
                    cur.execute("SELECT id, name_keys FROM person WHERE source_record_id IN (SELECT id FROM source_record WHERE source=%s AND source_key=%s)",
                                (rec["source"], rec["source_key"]))
                    row = cur.fetchone()
                    key = RU.name_key(nn)
                    if row:
                        keys = sorted(set(row["name_keys"]) | {key})
                        cur.execute("""UPDATE person SET display_name=%s, name_norm=%s, degree_raw=%s, email=%s, orcid=%s,
                                       phone=%s, dob=%s, rank=%s, position=%s, name_keys=%s, source_record_id=%s WHERE id=%s""",
                                    (*vals.values(), keys, rec["id"], row["id"]))
                        out["updated"] += 1
                    else:
                        cur.execute("""INSERT INTO person(kind, source_record_id, display_name, name_norm, degree_raw, email, orcid, phone, dob, rank, position, name_keys)
                                       VALUES ('lecturer',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (rec["id"], *vals.values(), [key]))
                        out["created"] += 1
            except psycopg.errors.IntegrityError as e:
                out["errors"].append({"source_key": rec["source_key"], "error": str(e).splitlines()[0]})
    return out


def assign_units_by_works(conn, actor_id=None):
    """Gán đơn vị giảng viên (`person.unit_id`) theo đa số `work_unit(source)`
    của các công trình đã liên kết còn sống (`v_person_publications`, trạng thái
    'DaNoiTuDong'/'DaXacNhan') — CLI `people --assign-units`. Chỉ động tới
    `unit_source='auto'` (đơn vị gán tay qua `cris.units.set_person_unit` không
    bị ghi đè). Hoà phiếu (nhiều đơn vị cùng số công trình cao nhất) → bỏ, để
    `unit_id=NULL` thay vì đoán. Mỗi thay đổi ghi `audit_log('person.unit_auto')`."""
    out = {"assigned": 0, "cleared": 0, "unchanged": 0, "tied": 0}
    with tx(conn), conn.cursor() as cur:
        cur.execute("SELECT id, unit_id FROM person WHERE kind='lecturer' AND unit_source='auto'")
        people_rows = cur.fetchall()
        for p in people_rows:
            cur.execute("""
                SELECT wu.unit_id, count(DISTINCT vp.work_id) AS n
                FROM v_person_publications vp
                JOIN work_unit wu ON wu.work_id = vp.work_id AND wu.source = 'source'
                WHERE vp.person_id = %s AND vp.state IN ('DaNoiTuDong', 'DaXacNhan')
                GROUP BY wu.unit_id ORDER BY n DESC
            """, (p["id"],))
            counts = cur.fetchall()
            new_unit_id, tied = None, False
            if counts:
                top_n = counts[0]["n"]
                leaders = [c for c in counts if c["n"] == top_n]
                if len(leaders) == 1:
                    new_unit_id = leaders[0]["unit_id"]
                else:
                    tied = True
            if new_unit_id == p["unit_id"]:
                out["unchanged"] += 1
                continue
            cur.execute("UPDATE person SET unit_id=%s WHERE id=%s", (new_unit_id, p["id"]))
            audit.log(conn, actor_id, "person.unit_auto", "person", p["id"],
                      before={"unit_id": p["unit_id"]}, after={"unit_id": new_unit_id})
            out["assigned" if new_unit_id is not None else "cleared"] += 1
            if tied:
                out["tied"] += 1
    return out
