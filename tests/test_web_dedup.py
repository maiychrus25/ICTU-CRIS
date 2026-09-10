# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import io
import itertools

import pytest

from cris import dedup, rules
from cris.web import wsgi
import cris.web.views_dedup  # noqa: F401 - import để decorator @route đăng ký

_seq = itertools.count()


def q(conn, sql, *a):
    with conn.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchall() if cur.description else None


def mk(conn, doc_type, title, doi=None, year=None, journal=None, student=None, cohort=None):
    key = f"{doc_type}/{title}/{student}/{doi}/{next(_seq)}"
    q(conn, "INSERT INTO source_record(sync_run_id, source, source_key, doc_type, content_hash, raw) "
            "VALUES (1,'manual',%s,%s,'h','{}')", key, doc_type)
    wid = q(conn, """INSERT INTO work(doc_type, primary_source_record_id, title, title_norm, doi, year_issue, journal, cohort, state)
                     VALUES (%s, currval('source_record_id_seq'), %s, %s, %s, %s, %s, %s, 'DaChuanHoa') RETURNING id""",
            doc_type, title, rules.norm_title(title), doi, year, journal, cohort)[0]["id"]
    for f, v in (("year_issue", year), ("journal", journal)):
        if v is not None:
            q(conn, "INSERT INTO field_provenance(work_id, field, value, set_kind) VALUES (%s,%s,%s,'normalize')", wid, f, str(v))
    if student:
        nn, _ = rules.norm_name(student, rules.RULES_V1["name_norm"])
        q(conn, "INSERT INTO author_mention(work_id, role, position, raw_name, name_norm, name_key) "
                "VALUES (%s,'student',1,%s,%s,%s)", wid, student, nn, rules.name_key(nn))
    return wid


@pytest.fixture(autouse=True)
def seed(conn):
    rules.seed_rules(conn, None)
    q(conn, "INSERT INTO sync_run(source, scope) VALUES ('manual','t')")


def call(app, method, path, headers=None, body=b"", query=""):
    """Dựng environ WSGI giả, gọi app, trả (status, headers, body_text) — không dựng server thật."""
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "wsgi.input": io.BytesIO(body),
        "CONTENT_LENGTH": str(len(body)),
    }
    if headers:
        environ.update(headers)
    captured = {}

    def start_response(status, resp_headers, exc_info=None):
        captured["status"] = status
        captured["headers"] = resp_headers

    result = app(environ, start_response)
    body_bytes = b"".join(result)
    return captured["status"], captured["headers"], body_bytes.decode("utf-8", errors="replace")


def auth(user_id):
    return {"HTTP_X_CRIS_USER": str(user_id)}


def form(**fields):
    parts = []
    for k, v in fields.items():
        if isinstance(v, (list, tuple)):
            parts.extend(f"{k}={item}" for item in v)
        else:
            parts.append(f"{k}={v}")
    return "&".join(parts).encode("utf-8")


def test_list_orders_doi_groups_before_title_groups(conn, user_id):
    a = mk(conn, "bai_bao", "Doi List Order Alpha", doi="10.1/list-order")
    b = mk(conn, "bai_bao", "Doi List Order Alpha copy", doi="10.1/list-order")
    c = mk(conn, "bai_bao", "Title List Order Beta")
    d = mk(conn, "bai_bao", "title list order beta")
    dedup.find_duplicates(conn)
    gids = {r["basis"]: r["id"] for r in q(conn, "SELECT basis, id FROM duplicate_group")}
    assert set(gids) == {"doi", "title_norm"}

    status, _, body = call(wsgi.app, "GET", "/doi-soat/trung-lap", headers=auth(user_id))
    assert status.startswith("200")
    doi_pos = body.index(f'/doi-soat/trung-lap/{gids["doi"]}"')
    title_pos = body.index(f'/doi-soat/trung-lap/{gids["title_norm"]}"')
    assert doi_pos < title_pos


def test_detail_shows_all_members_and_marks_differing_fields(conn, user_id):
    a = mk(conn, "bai_bao", "Cocktail Party Effect", doi="10.1/detail", year=2025, journal="ACS Omega")
    b = mk(conn, "bai_bao", "Cocktail Party Effect", doi="10.1/detail", year=2024, journal="ACS omega")
    dedup.find_duplicates(conn)
    gid = q(conn, "SELECT id FROM duplicate_group")[0]["id"]

    status, _, body = call(wsgi.app, "GET", f"/doi-soat/trung-lap/{gid}", headers=auth(user_id))
    assert status.startswith("200")
    # Cả hai thành viên đều có mặt.
    assert f"Bản #{a} (" in body
    assert f"Bản #{b} (" in body
    # Trường khác nhau (year_issue, journal) được tô đậm bằng <mark>.
    assert "<mark>2025</mark>" in body and "<mark>2024</mark>" in body
    assert "<mark>ACS Omega</mark>" in body and "<mark>ACS omega</mark>" in body
    # Trường giống nhau (title) không bị đánh dấu khác biệt.
    assert "<mark>Cocktail Party Effect</mark>" not in body


def test_merge_with_field_choices_keeps_original_row(conn, user_id):
    a = mk(conn, "bai_bao", "Merge Choice", doi="10.1/merge-choice", year=2025, journal="ACS Omega")
    b = mk(conn, "bai_bao", "Merge Choice", doi="10.1/merge-choice", year=2024, journal="ACS omega")
    dedup.find_duplicates(conn)
    gid = q(conn, "SELECT id FROM duplicate_group")[0]["id"]

    body = form(decision="merge", survivor_id=a, **{"field__year_issue": b, "field__journal": a})
    status, headers, _ = call(
        wsgi.app, "POST", f"/doi-soat/trung-lap/{gid}/quyet-dinh", headers=auth(user_id), body=body
    )
    assert status.startswith("303")
    assert dict(headers)["Location"] == "/doi-soat/trung-lap"

    ws = {w["id"]: w for w in q(conn, "SELECT id, state, merged_into_id, year_issue, journal FROM work")}
    assert ws[a]["state"] == "DaXacNhan"
    assert ws[a]["year_issue"] == 2024        # giá trị chọn từ b được áp cho a
    assert ws[a]["journal"] == "ACS Omega"    # chọn từ a (giữ nguyên)
    assert ws[b]["state"] == "DaGop" and ws[b]["merged_into_id"] == a
    assert len(q(conn, "SELECT 1 FROM work")) == 2   # bản gốc (b) vẫn còn, không bị xoá


def test_thesis_group_shows_hint_and_defaults_to_keep(conn, user_id):
    for s in ["Nguyễn A", "Trần B", "Lê C"]:
        mk(conn, "do_an", "Xây dựng chuỗi sản phẩm truyền thông", student=s, cohort="K14")
    dedup.find_duplicates(conn)
    gid = q(conn, "SELECT id FROM duplicate_group")[0]["id"]

    status, _, body = call(wsgi.app, "GET", f"/doi-soat/trung-lap/{gid}", headers=auth(user_id))
    assert status.startswith("200")
    assert "đồ án nhóm" in body
    assert "Giữ riêng (khuyến nghị)" in body
    # Hành động "Giữ riêng" được xếp trước, đề xuất mặc định, so với "Gộp".
    assert body.index("Giữ riêng (khuyến nghị)") < body.index("Gộp các bản ghi")


def test_keep_without_reason_does_not_change_state(conn, user_id):
    mk(conn, "do_an", "Chua co ly do", student="A B", cohort="K1")
    mk(conn, "do_an", "Chua co ly do", student="C D", cohort="K1")
    dedup.find_duplicates(conn)
    gid = q(conn, "SELECT id FROM duplicate_group")[0]["id"]

    status, headers, _ = call(
        wsgi.app, "POST", f"/doi-soat/trung-lap/{gid}/quyet-dinh",
        headers=auth(user_id), body=form(decision="keep"),
    )
    assert status.startswith("303")
    assert dict(headers)["Location"].startswith(f"/doi-soat/trung-lap/{gid}?loi=")
    assert q(conn, "SELECT state FROM duplicate_group WHERE id=%s", gid)[0]["state"] == "NghiTrung"
    assert {w["state"] for w in q(conn, "SELECT state FROM work")} == {"NghiTrung"}


def test_unknown_gid_returns_404(conn, user_id):
    status, _, body = call(wsgi.app, "GET", "/doi-soat/trung-lap/999999", headers=auth(user_id))
    assert status.startswith("404")
    assert "<!doctype html>" in body.lower()

    status2, _, _ = call(
        wsgi.app, "POST", "/doi-soat/trung-lap/999999/quyet-dinh",
        headers=auth(user_id), body=form(decision="keep", reason="x"),
    )
    assert status2.startswith("404")


def test_script_in_title_is_escaped_on_detail_page(conn, user_id):
    a = mk(conn, "bai_bao", "<script>alert(1)</script>", doi="10.1/xss")
    mk(conn, "bai_bao", "<script>alert(2)</script>", doi="10.1/xss")
    dedup.find_duplicates(conn)
    gid = q(conn, "SELECT id FROM duplicate_group")[0]["id"]

    status, _, body = call(wsgi.app, "GET", f"/doi-soat/trung-lap/{gid}", headers=auth(user_id))
    assert status.startswith("200")
    assert "<script>alert" not in body
    assert "&lt;script&gt;" in body
