# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""SC-07 — hàng đợi nghi trùng: danh sách nhóm nghi trùng, so sánh cạnh nhau từng
trường, và quyết định gộp/giữ riêng qua `cris.dedup.decide_group`.

Không tự động hoá quyết định (BR-18): không route nào tự gộp hay tự chọn giá trị
"đúng" cho một trường mâu thuẫn — người dùng luôn phải tự chọn giá trị giữ lại cho
từng trường khác nhau (BR-10) và bản ghi sống sót trước khi gộp. `dedup._diff` đã
tính sẵn các trường khác nhau giữa từng thành viên và lưu vào `duplicate_member.diff`
lúc `find_duplicates` chạy; trang so sánh chỉ ĐỌC lại cột đó, không tính lại.

Nhóm mà các thành viên nhiều khả năng khác sinh viên nhau (đồ án nhóm, BR-08) đã
được `dedup.find_duplicates` gắn `duplicate_group.hint` — trang chi tiết hiện cảnh
báo đó và xếp hành động "Giữ riêng" lên trước, mặc định đề xuất, thay vì gộp.
"""
from urllib.parse import quote

from cris import dedup
from cris.web.render import badge, e, layout, pager, table
from cris.web.wsgi import Redirect, route

PER_PAGE = 50

BASIS_LABELS = {
    "doi": "DOI",
    "title_norm": "Tiêu đề",
    "title_student_cohort": "Tiêu đề + khoá sinh viên",
}

FIELD_LABELS = {
    "title": "Tiêu đề",
    "doi": "DOI",
    "year_issue": "Năm/kỳ",
    "journal": "Tạp chí",
    "volume": "Tập/số",
    "pub_type_raw": "Loại xuất bản (thô)",
    "cohort": "Khoá",
}

GROUP_STATE_LABELS = {
    "NghiTrung": ("Chờ quyết định", "warn"),
    "DaGop": ("Đã gộp", "ok"),
    "GiuRieng": ("Giữ riêng", "default"),
    "BoQua": ("Đã bỏ qua", "default"),
}


def _page_of(raw):
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return 1
    return n if n > 0 else 1


def _not_found(gid):
    msg = f"Không tìm thấy nhóm nghi trùng #{gid}."
    return 404, [], layout("Không tìm thấy", f'<p class="error-page">{e(msg)}</p>')


def _fetch_group(conn, gid):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM duplicate_group WHERE id=%s", (gid,))
        return cur.fetchone()


def _fetch_ai_similarity(conn, gid):
    """Tương đồng tóm tắt (AI, FR-AI-07): min–max cosine giữa các thành viên,
    hoặc `None` nếu chưa có gợi ý. Chỉ đọc `ai_suggestion` — không tính lại."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT payload FROM ai_suggestion WHERE kind='duplicate' AND target_id=%s "
            "ORDER BY built_at DESC LIMIT 1",
            (gid,),
        )
        row = cur.fetchone()
    return row["payload"] if row else None


def _fetch_members(conn, gid):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT w.*, m.diff AS diff FROM duplicate_member m "
            "JOIN work w ON w.id = m.work_id WHERE m.group_id=%s ORDER BY w.id",
            (gid,),
        )
        return cur.fetchall()


def _diff_fields(members):
    """Hợp các khoá trong `duplicate_member.diff` đã lưu sẵn — không tính lại."""
    changed = set()
    for m in members:
        changed.update((m.get("diff") or {}).keys())
    return [f for f in dedup.COMPARE if f in changed]


@route("GET", "/doi-soat/trung-lap")
def list_groups(req):
    state = req.query.get("state") or "NghiTrung"
    page = _page_of(req.query.get("page"))
    show_all = state == "tat-ca"
    with req.conn.cursor() as cur:
        if show_all:
            cur.execute("SELECT count(*) AS n FROM duplicate_group")
        else:
            cur.execute("SELECT count(*) AS n FROM duplicate_group WHERE state=%s", (state,))
        total = cur.fetchone()["n"]
        offset = (page - 1) * PER_PAGE
        base_sql = (
            "SELECT g.id, g.doc_type, g.basis, g.hint, g.state, g.created_at, "
            "(SELECT count(*) FROM duplicate_member m WHERE m.group_id = g.id) AS member_count "
            "FROM duplicate_group g {where} "
            "ORDER BY (g.basis <> 'doi'), g.created_at, g.id LIMIT %s OFFSET %s"
        )
        if show_all:
            cur.execute(base_sql.format(where=""), (PER_PAGE, offset))
        else:
            cur.execute(base_sql.format(where="WHERE g.state=%s"), (state, PER_PAGE, offset))
        groups = cur.fetchall()

    rows = []
    for g in groups:
        state_label, state_kind = GROUP_STATE_LABELS.get(g["state"], (g["state"], "default"))
        rows.append([
            f'<a href="/doi-soat/trung-lap/{g["id"]}">#{e(g["id"])}</a>',
            e(g["doc_type"]),
            e(BASIS_LABELS.get(g["basis"], g["basis"])),
            badge("đồ án nhóm?", "warn") if g["hint"] else "",
            e(g["member_count"]),
            badge(state_label, state_kind),
        ])
    body = table(
        ["Nhóm", "Loại tài liệu", "Căn cứ ghép", "Cảnh báo", "Số bản ghi", "Trạng thái"],
        rows,
    )
    base_url = f"/doi-soat/trung-lap?state={quote(state)}"
    body += pager(page, total, PER_PAGE, base_url)
    return layout("Hàng đợi nghi trùng", body, active="/doi-soat/trung-lap")


def _render_compare_table(members, diff_fields):
    headers = ["Trường"] + [f"Bản #{m['id']} ({m['state']})" for m in members]
    rows = []
    for field in dedup.COMPARE:
        differs = field in diff_fields
        cells = [e(FIELD_LABELS.get(field, field))]
        for m in members:
            val = e(m.get(field))
            cells.append(f"<mark>{val}</mark>" if differs else val)
        rows.append(cells)
    return table(headers, rows)


def _render_merge_form(gid, members, diff_fields):
    parts = [
        f'<form method="post" action="/doi-soat/trung-lap/{gid}/quyet-dinh">',
        '<input type="hidden" name="decision" value="merge">',
        "<h2>Gộp thành một bản ghi</h2>",
        "<fieldset><legend>Bản ghi sống sót</legend>",
    ]
    for m in members:
        parts.append(
            f'<label><input type="radio" name="survivor_id" value="{m["id"]}" required> '
            f'Bản #{e(m["id"])} — {e(m["title"])}</label><br>'
        )
    parts.append("</fieldset>")
    if diff_fields:
        parts.append(
            "<p>Các trường sau khác nhau giữa các bản ghi — hệ thống không tự chọn, "
            "hãy tự chọn giá trị giữ lại cho từng trường (BR-10):</p>"
        )
    for field in diff_fields:
        parts.append(
            f"<fieldset><legend>{e(FIELD_LABELS.get(field, field))} — khác nhau</legend>"
        )
        for m in members:
            parts.append(
                f'<label><input type="radio" name="field__{field}" value="{m["id"]}" required> '
                f'Bản #{e(m["id"])}: {e(m.get(field))}</label><br>'
            )
        parts.append("</fieldset>")
    parts.append(
        '<label>Ghi chú (không bắt buộc)<br><textarea name="reason" rows="2"></textarea></label>'
    )
    parts.append('<p><button type="submit">Gộp các bản ghi</button></p>')
    parts.append("</form>")
    return "".join(parts)


def _render_keep_form(gid, recommended):
    label = "Giữ riêng (khuyến nghị)" if recommended else "Giữ riêng"
    return (
        f'<form method="post" action="/doi-soat/trung-lap/{gid}/quyet-dinh">'
        '<input type="hidden" name="decision" value="keep">'
        "<h2>Giữ riêng</h2>"
        '<label>Lý do (bắt buộc)<br>'
        '<textarea name="reason" rows="2" required></textarea></label>'
        f'<p><button type="submit">{e(label)}</button></p>'
        "</form>"
    )


def _render_decided_summary(group):
    bits = [
        f"<p>Nhóm này đã được quyết định lúc {e(group['decided_at'])} "
        f"bởi người dùng #{e(group['decided_by'])}.</p>"
    ]
    if group.get("reason"):
        bits.append(f"<p>Lý do: {e(group['reason'])}</p>")
    if group.get("survivor_work_id"):
        bits.append(f"<p>Bản ghi sống sót: #{e(group['survivor_work_id'])}.</p>")
    return "".join(bits)


@route("GET", "/doi-soat/trung-lap/<int:gid>")
def detail(req, gid):
    group = _fetch_group(req.conn, gid)
    if group is None:
        return _not_found(gid)
    members = _fetch_members(req.conn, gid)
    diff_fields = _diff_fields(members)

    parts = []
    error = req.query.get("loi")
    if error:
        parts.append(f'<p class="error-page">{e(error)}</p>')

    state_label, state_kind = GROUP_STATE_LABELS.get(group["state"], (group["state"], "default"))
    parts.append(
        f'<p>{badge(state_label, state_kind)} · '
        f'{e(BASIS_LABELS.get(group["basis"], group["basis"]))} · {e(group["doc_type"])}</p>'
    )

    ai_sim = _fetch_ai_similarity(req.conn, gid)
    if ai_sim:
        parts.append(
            f'<p>Tương đồng tóm tắt (AI): {e(round(ai_sim["min"], 2))}–{e(round(ai_sim["max"], 2))}</p>'
        )

    has_hint = bool(group["hint"])
    if has_hint:
        parts.append(f'<p class="badge badge-warn">{e(group["hint"])}</p>')
        parts.append(
            "<p>Các thành viên nhiều khả năng KHÁC sinh viên nhau (đồ án nhóm) — "
            "khuyến nghị <strong>Giữ riêng</strong> thay vì gộp, để tránh xoá nhầm "
            "bản ghi thật của người khác (BR-08).</p>"
        )

    parts.append(_render_compare_table(members, diff_fields))

    if group["state"] == "NghiTrung":
        keep_form = _render_keep_form(gid, has_hint)
        merge_form = _render_merge_form(gid, members, diff_fields)
        if has_hint:
            parts.append(keep_form)
            parts.append(merge_form)
        else:
            parts.append(merge_form)
            parts.append(keep_form)
    else:
        parts.append(_render_decided_summary(group))

    return layout(f"Nhóm nghi trùng #{gid}", "".join(parts), active="/doi-soat/trung-lap")


@route("POST", "/doi-soat/trung-lap/<int:gid>/quyet-dinh")
def decide(req, gid):
    group = _fetch_group(req.conn, gid)
    if group is None:
        return _not_found(gid)

    decision = req.form.get("decision")
    reason = (req.form.get("reason") or "").strip() or None

    if decision == "keep":
        # BR-10/giao diện: Giữ riêng bắt buộc có lý do — kiểm ở đây (server), không
        # chỉ dựa vào `required` phía trình duyệt, trước khi gọi tầng nghiệp vụ.
        if not reason:
            msg = "Cần nhập lý do khi chọn Giữ riêng."
            return Redirect(f"/doi-soat/trung-lap/{gid}?loi={quote(msg)}")
        try:
            dedup.decide_group(req.conn, gid, "keep", req.actor_id, reason=reason)
        except ValueError as exc:
            return Redirect(f"/doi-soat/trung-lap/{gid}?loi={quote(str(exc))}")
        return Redirect("/doi-soat/trung-lap")

    if decision == "merge":
        try:
            survivor_id = int(req.form.get("survivor_id"))
        except (TypeError, ValueError):
            msg = "Cần chọn bản ghi sống sót."
            return Redirect(f"/doi-soat/trung-lap/{gid}?loi={quote(msg)}")
        field_choices = {}
        for key, value in req.form.items():
            if not key.startswith("field__"):
                continue
            try:
                field_choices[key[len("field__"):]] = int(value)
            except (TypeError, ValueError):
                msg = "Giá trị trường chọn không hợp lệ."
                return Redirect(f"/doi-soat/trung-lap/{gid}?loi={quote(msg)}")
        try:
            dedup.decide_group(
                req.conn, gid, "merge", req.actor_id,
                survivor_id=survivor_id, field_choices=field_choices, reason=reason,
            )
        except ValueError as exc:
            return Redirect(f"/doi-soat/trung-lap/{gid}?loi={quote(str(exc))}")
        return Redirect("/doi-soat/trung-lap")

    msg = "Quyết định không hợp lệ."
    return Redirect(f"/doi-soat/trung-lap/{gid}?loi={quote(msg)}")
