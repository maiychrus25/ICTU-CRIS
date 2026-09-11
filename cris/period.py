# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import json
from datetime import datetime, timezone
from cris import audit
from cris.db import tx

# Kỳ báo cáo chỉ đi qua các trạng thái thuộc phạm vi lát cắt K; "duyệt/trả lại"
# (lát cắt D) và "chốt kỳ/báo cáo" (lát cắt R) sẽ mở rộng bảng này ở lát cắt sau.
PERIOD_STATES = ("ChuanBi", "DangMo", "DaDongNop", "Huy")
DECLARATION_STATES = ("Nhap", "ChoBoSung", "ChoKhoaDuyet", "KhoaDaDuyet", "ChoPhongKiemTra",
                       "DatYeuCau", "DaChot", "Rut")

# Kind của rule_set gắn vào kỳ khi mở (BR-05). "year_rule" là kind duy nhất trong
# rules.RULES_V1 chưa gắn với một khâu nghiệp vụ cụ thể nào (thân rỗng, để dành);
# về ngữ nghĩa đây đúng là bộ quy tắc "phạm vi năm/kỳ" nên được chọn làm mặc định.
DEFAULT_RULE_KIND = "year_rule"


def _active_rule_set_id(conn, kind):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM rule_set WHERE kind=%s AND active", (kind,))
        row = cur.fetchone()
        return row["id"] if row else None


def _get_period(cur, period_id, lock=False):
    sql = "SELECT * FROM period WHERE id=%s"
    if lock:
        sql += " FOR UPDATE"
    cur.execute(sql, (period_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"không tìm thấy kỳ báo cáo: {period_id}")
    return row


def _transition(conn, cur, period_id, *, to_state, allowed_from, actor_id, action, reject_message, set_opens_at=False):
    before = _get_period(cur, period_id, lock=True)
    if before["state"] not in allowed_from:
        raise ValueError(reject_message)
    if set_opens_at:
        cur.execute("UPDATE period SET state=%s, opens_at=now() WHERE id=%s", (to_state, period_id))
    else:
        cur.execute("UPDATE period SET state=%s WHERE id=%s", (to_state, period_id))
    after = _get_period(cur, period_id)
    audit.log(conn, actor_id, action, "period", period_id,
              before={"state": before["state"]}, after={"state": after["state"]})
    return after


def open_period(conn, *, code, name, scope, criteria, due_at, actor_id, rule_set_id=None):
    """Tạo kỳ báo cáo ở trạng thái ChuanBi rồi chuyển ngay sang DangMo.

    Gắn rule_set_id của bộ quy tắc đang hoạt động (kind=year_rule, trừ khi gọi
    truyền sẵn rule_set_id) vào kỳ NGAY TẠI THỜI ĐIỂM MỞ — theo BR-05, đổi bộ quy
    tắc đang hoạt động sau đó không được làm đổi period.rule_set_id.
    Trả về id của kỳ vừa mở.
    """
    with tx(conn), conn.cursor() as cur:
        if rule_set_id is None:
            rule_set_id = _active_rule_set_id(conn, DEFAULT_RULE_KIND)
            if rule_set_id is None:
                raise ValueError("chưa có bộ quy tắc năm đang hoạt động để gắn vào kỳ")
        cur.execute("SELECT id FROM period WHERE code=%s", (code,))
        if cur.fetchone():
            raise ValueError(f"mã kỳ báo cáo đã tồn tại: {code}")
        cur.execute(
            "INSERT INTO period(code, name, scope, criteria, rule_set_id, due_at, created_by) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (code, name, json.dumps(scope, ensure_ascii=False), criteria, rule_set_id, due_at, actor_id))
        period_id = cur.fetchone()["id"]
        _transition(conn, cur, period_id, to_state="DangMo", allowed_from=("ChuanBi",), actor_id=actor_id,
                    action="period.open", reject_message="không thể mở kỳ", set_opens_at=True)
    return period_id


def close_submissions(conn, period_id, actor_id):
    """DangMo -> DaDongNop. Chỉ chấp nhận từ kỳ đang mở."""
    with tx(conn), conn.cursor() as cur:
        _transition(conn, cur, period_id, to_state="DaDongNop", allowed_from=("DangMo",), actor_id=actor_id,
                    action="period.close_submissions",
                    reject_message="chỉ đóng cổng nộp khi kỳ đang ở trạng thái đang mở")


def cancel_period(conn, period_id, actor_id):
    """ChuanBi hoặc DangMo -> Huy."""
    with tx(conn), conn.cursor() as cur:
        _transition(conn, cur, period_id, to_state="Huy", allowed_from=("ChuanBi", "DangMo"), actor_id=actor_id,
                    action="period.cancel",
                    reject_message="chỉ huỷ kỳ khi đang chuẩn bị hoặc đang mở")


def list_periods(conn, unit_id=None):
    """Danh sách kỳ báo cáo, mới nhất trước.

    unit_id=None trả toàn bộ kỳ (kỳ là thực thể toàn trường, không thuộc riêng
    đơn vị nào). Truyền unit_id để chỉ lấy các kỳ mà đơn vị đó đã có ít nhất một
    hồ sơ kê khai — phục vụ màn hình lọc theo đơn vị.
    """
    with conn.cursor() as cur:
        if unit_id is None:
            cur.execute("SELECT * FROM period ORDER BY created_at DESC")
        else:
            cur.execute(
                "SELECT * FROM period p WHERE EXISTS "
                "(SELECT 1 FROM declaration d WHERE d.period_id = p.id AND d.unit_id = %s) "
                "ORDER BY p.created_at DESC",
                (unit_id,))
        return cur.fetchall()


def period_progress(conn, period_id):
    """Tiến độ kê khai theo từng đơn vị cho một kỳ.

    Trả {"period_id", "state", "due_at", "days_remaining",
         "units": [{"unit_id", "unit_code", "unit_name", "counts": {state: n}, "total"}]}.
    Liệt kê MỌI đơn vị đang hoạt động, kể cả khi kỳ chưa có hồ sơ nào (counts=0),
    để bảng tiến độ ở SC-03 không bỏ sót đơn vị chưa nộp gì.
    """
    with conn.cursor() as cur:
        period = _get_period(cur, period_id)
        cur.execute("SELECT id, code, name FROM unit WHERE active ORDER BY name")
        units = cur.fetchall()
        cur.execute(
            "SELECT unit_id, state, count(*) AS n FROM declaration WHERE period_id=%s GROUP BY unit_id, state",
            (period_id,))
        by_unit = {}
        for row in cur.fetchall():
            by_unit.setdefault(row["unit_id"], {})[row["state"]] = row["n"]

    days_remaining = None
    if period["due_at"] is not None:
        now = datetime.now(timezone.utc)
        days_remaining = (period["due_at"] - now).days

    rows = []
    for u in units:
        counts_for_unit = by_unit.get(u["id"], {})
        counts = {s: counts_for_unit.get(s, 0) for s in DECLARATION_STATES}
        rows.append({
            "unit_id": u["id"],
            "unit_code": u["code"],
            "unit_name": u["name"],
            "counts": counts,
            "total": sum(counts.values()),
        })

    return {
        "period_id": period_id,
        "state": period["state"],
        "due_at": period["due_at"],
        "days_remaining": days_remaining,
        "units": rows,
    }
