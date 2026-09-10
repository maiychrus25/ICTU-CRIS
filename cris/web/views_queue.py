# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Hàng đợi liên kết tác giả (SC-08).

Danh sách các lượt tên (`author_mention`) đang chờ người dùng xác nhận ứng viên
`person` do `cris.link.candidates`/`link_pending` đề xuất, và route xử lý quyết
định hàng loạt gọi thẳng vào `cris.link.decide_link`.

Về giao dịch của thao tác hàng loạt: `link.decide_link` tự mở và `commit()` một
giao dịch thật cho MỖI lời gọi (xem `cris.db.tx`). Để nhiều lời gọi trong một lô
nằm chung một giao dịch — một id lỗi thì không id nào trong lô đổi — route POST
bọc `req.conn` bằng `_DeferredCommitConn`: hoãn `commit()` (chỉ commit thật một
lần, sau khi cả lô đã chạy xong không lỗi) trong khi `rollback()` vẫn xuyên
thẳng xuống kết nối thật, để việc rollback bên trong `decide_link` (khi một id
hỏng) cuốn theo luôn những id đã "commit hờ" trước đó trong cùng lô.
"""
from urllib.parse import urlencode

from cris import link
from cris.web.render import badge, e, layout, pager, table
from cris.web.wsgi import Redirect, route

PATH_LIST = "/doi-soat/tac-gia"
PATH_DECIDE = "/doi-soat/tac-gia/quyet-dinh"

PER_PAGE = 50
DEFAULT_STATE = "ChoXacNhan"

STATE_LABELS = {
    "ChoXacNhan": "Đang chờ xác nhận",
    "DaNoiTuDong": "Đã nối tự động",
    "DaXacNhan": "Đã xác nhận",
    "DaBacBo": "Đã bác bỏ",
}

CONFIDENCE_BADGE_KIND = {
    "orcid": "ok",
    "ten_day_du_duy_nhat": "ok",
    "ten_day_du_nhieu_ung_vien": "warn",
    "ten_mot_phan": "warn",
}

DECISIONS = {"confirm", "reject", "reassign"}

DECISION_LABELS = {
    "confirm": "Xác nhận",
    "reject": "Bác bỏ",
    "reassign": "Chuyển cho người khác",
}


class _DeferredCommitConn:
    """Bọc quanh một kết nối psycopg thật: `commit()` là no-op, `rollback()` và
    mọi thuộc tính/phương thức khác xuyên thẳng xuống kết nối thật.

    Dùng để nhiều lời gọi `link.decide_link` (mỗi lời gọi tự `commit()` sau khi
    thành công) gộp lại thành một giao dịch thật duy nhất do route quyết định
    khi nào commit thật.
    """

    def __init__(self, conn):
        self._conn = conn

    def commit(self):
        pass

    def rollback(self):
        self._conn.rollback()

    def __getattr__(self, name):
        return getattr(self._conn, name)


def _filters(source):
    """Đọc `state`, `q`, `page` từ một dict phẳng (`req.query` hoặc `req.form`)."""
    state = source.get("state") or DEFAULT_STATE
    if state not in STATE_LABELS:
        state = DEFAULT_STATE
    q = (source.get("q") or "").strip()
    try:
        page = int(source.get("page") or "1")
    except (TypeError, ValueError):
        page = 1
    return state, q, max(1, page)


def _base_url(state, q):
    params = {"state": state}
    if q:
        params["q"] = q
    return f"{PATH_LIST}?{urlencode(params)}"


def _redirect_url(state, q, page, error=None):
    params = {"state": state}
    if q:
        params["q"] = q
    if page and page > 1:
        params["page"] = page
    if error:
        params["error"] = error
    return f"{PATH_LIST}?{urlencode(params)}"


def _fetch(req, state, q, page):
    where = ["l.state = %(state)s"]
    params = {"state": state}
    if q:
        where.append("m.raw_name ILIKE %(q)s")
        params["q"] = f"%{q}%"
    where_sql = " AND ".join(where)
    # cùng điều kiện lọc, đổi bí danh cho subquery gộp
    where_sql_g = where_sql.replace("l.", "l2.").replace("m.", "m2.")
    with req.conn.cursor() as cur:
        cur.execute(
            f"SELECT count(*) AS n FROM author_link l "
            f"JOIN author_mention m ON m.id = l.mention_id WHERE {where_sql}",
            params,
        )
        total = cur.fetchone()["n"]
        cur.execute(
            f"""
            SELECT l.id AS link_id, l.confidence, l.degree_conflict,
                   m.raw_name, w.id AS work_id, w.title,
                   p.display_name AS candidate_name,
                   g.group_work_count
            FROM author_link l
            JOIN author_mention m ON m.id = l.mention_id
            JOIN work w ON w.id = m.work_id
            JOIN person p ON p.id = l.person_id
            -- Postgres không cho DISTINCT trong window function, nên gộp sẵn
            -- số công trình theo raw_name ở subquery rồi mới nối vào.
            JOIN (
                SELECT m2.raw_name, count(DISTINCT m2.work_id) AS group_work_count
                FROM author_link l2
                JOIN author_mention m2 ON m2.id = l2.mention_id
                WHERE {where_sql_g}
                GROUP BY m2.raw_name
            ) g ON g.raw_name = m.raw_name
            WHERE {where_sql}
            ORDER BY g.group_work_count DESC, m.raw_name, w.id, l.id
            LIMIT %(limit)s OFFSET %(offset)s
            """,
            {**params, "limit": PER_PAGE, "offset": (page - 1) * PER_PAGE},
        )
        rows = cur.fetchall()
    return rows, total


def _filter_form(state, q):
    options = "".join(
        f'<option value="{e(s)}"{" selected" if s == state else ""}>{e(label)}</option>'
        for s, label in STATE_LABELS.items()
    )
    return (
        f'<form method="get" action="{e(PATH_LIST)}" class="filter-form">'
        f'<label>Trạng thái <select name="state">{options}</select></label> '
        f'<label>Tên thô <input type="text" name="q" value="{e(q)}" '
        f'placeholder="lọc theo tên thô trong bản ghi"></label> '
        f'<button type="submit">Lọc</button>'
        f"</form>"
    )


def _select_cell(link_id, group_idx, is_group_head, group_work_count):
    cb = (
        f'<input type="checkbox" name="link_id" value="{link_id}" '
        f'data-group="{group_idx}" form="quyet-dinh-form">'
    )
    if not is_group_head:
        return cb
    group_cb = (
        f'<label class="group-select"><input type="checkbox" '
        f'onclick="toggleGroup(this,{group_idx})"> '
        f"Cả nhóm ({group_work_count} công trình)</label>"
    )
    return f"{cb}<br>{group_cb}"


def _rows_html(rows):
    out = []
    last_raw_name = object()
    group_idx = -1
    for r in rows:
        is_group_head = r["raw_name"] != last_raw_name
        if is_group_head:
            group_idx += 1
            last_raw_name = r["raw_name"]
        out.append(
            [
                _select_cell(r["link_id"], group_idx, is_group_head, r["group_work_count"]),
                e(r["raw_name"]),
                e(r["title"]),
                e(r["candidate_name"]),
                badge(r["confidence"], CONFIDENCE_BADGE_KIND.get(r["confidence"], "default")),
                badge("Mâu thuẫn học vị", "danger") if r["degree_conflict"] else "",
            ]
        )
    return out


_SCRIPT = """
function toggleGroup(el, group) {
  var boxes = document.querySelectorAll('input[data-group="' + group + '"]');
  for (var i = 0; i < boxes.length; i++) { boxes[i].checked = el.checked; }
}
function capNhatYeuCauLyDo(sel) {
  var reason = document.getElementById('quyet-dinh-reason');
  if (reason) { reason.required = (sel.value === 'reject'); }
}
"""


def _decision_controls():
    decision_options = "".join(
        f'<option value="{e(k)}">{e(v)}</option>' for k, v in DECISION_LABELS.items()
    )
    return (
        f'<div class="decision-controls">'
        f'<label>Quyết định '
        f'<select name="decision" form="quyet-dinh-form" onchange="capNhatYeuCauLyDo(this)">'
        f"{decision_options}</select></label> "
        f'<label>Người thay thế (khi chuyển) '
        f'<input type="number" name="person_id" form="quyet-dinh-form" min="1"></label> '
        f'<label>Lý do (bắt buộc khi bác bỏ) '
        f'<textarea id="quyet-dinh-reason" name="reason" form="quyet-dinh-form" rows="2">'
        f"</textarea></label> "
        f'<button type="submit" form="quyet-dinh-form">Áp dụng cho các mục đã chọn</button>'
        f"</div>"
    )


@route("GET", PATH_LIST)
def list_queue(req):
    state, q, page = _filters(req.query)
    error = req.query.get("error")
    rows, total = _fetch(req, state, q, page)

    body_parts = []
    if error:
        body_parts.append(f'<p class="error-page">{e(error)}</p>')
    body_parts.append(_filter_form(state, q))

    if not rows:
        body_parts.append(
            '<p class="empty-state">Không có lượt tên nào khớp bộ lọc hiện tại.</p>'
        )
    else:
        body_parts.append(f"<script>{_SCRIPT}</script>")
        body_parts.append(
            f'<form id="quyet-dinh-form" method="post" action="{e(PATH_DECIDE)}">'
            f'<input type="hidden" name="state" value="{e(state)}">'
            f'<input type="hidden" name="q" value="{e(q)}">'
            f'<input type="hidden" name="page" value="{e(page)}">'
            f"</form>"
        )
        body_parts.append(_decision_controls())
        headers = ["Chọn", "Tên thô", "Công trình", "Ứng viên đề xuất", "Độ tin cậy", "Cảnh báo"]
        body_parts.append(table(headers, _rows_html(rows)))
        body_parts.append(pager(page, total, PER_PAGE, _base_url(state, q)))

    return layout("Hàng đợi liên kết tác giả", "".join(body_parts), active=PATH_LIST)


@route("POST", PATH_DECIDE)
def decide(req):
    state, q, page = _filters(req.form)

    link_ids_raw = req.form_list("link_id")
    decision = (req.form.get("decision") or "").strip()
    reason = (req.form.get("reason") or "").strip() or None
    person_id_raw = (req.form.get("person_id") or "").strip()

    if not link_ids_raw:
        return Redirect(_redirect_url(state, q, page, "Chưa chọn liên kết nào để xử lý."))
    if decision not in DECISIONS:
        return Redirect(_redirect_url(state, q, page, "Quyết định không hợp lệ."))
    if decision == "reject" and not reason:
        return Redirect(_redirect_url(state, q, page, "Bác bỏ bắt buộc phải nêu lý do."))

    try:
        link_ids = [int(v) for v in link_ids_raw]
    except ValueError:
        return Redirect(_redirect_url(state, q, page, "Mã liên kết không hợp lệ."))

    person_id = None
    if decision == "reassign":
        if not person_id_raw:
            return Redirect(
                _redirect_url(state, q, page, "Chuyển cho người khác bắt buộc phải chọn người.")
            )
        try:
            person_id = int(person_id_raw)
        except ValueError:
            return Redirect(_redirect_url(state, q, page, "Mã người dùng không hợp lệ."))

    proxy = _DeferredCommitConn(req.conn)
    failed_id = None
    try:
        for link_id in link_ids:
            failed_id = link_id
            link.decide_link(proxy, link_id, decision, req.actor_id, reason=reason, person_id=person_id)
    except Exception as exc:  # noqa: BLE001 - lỗi tầng nghiệp vụ hiển thị lại cho người dùng
        req.conn.rollback()
        return Redirect(
            _redirect_url(state, q, page, f"Không xử lý được mã {failed_id}: {exc}")
        )

    req.conn.commit()
    return Redirect(_redirect_url(state, q, page))
