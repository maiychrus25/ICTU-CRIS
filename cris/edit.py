# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Chỉnh tay có xuất xứ (lát cắt H2): phòng KH-CN sửa trực tiếp một số trường
của `work` khi nguồn sai hoặc thiếu, luôn kèm lý do và ghi `field_provenance`
(`set_kind='manual'`) + `audit_log('work.edit')` để tra ngược được ai sửa, lúc
nào, giá trị cũ là gì. Theo BR-23, phòng KH-CN không tự sửa tác giả, đơn vị,
minh chứng — các trường đó không có trong `EDITABLE`."""
from cris import audit
from cris import rules as RU
from cris.db import tx

EDITABLE = ("title", "doi", "year_issue", "journal", "volume", "pub_type_raw",
            "cohort", "abstract", "keywords_raw")


def _coerce(field, value):
    """Ép kiểu giá trị mới theo cột `work`. `year_issue` → int hoặc NULL nếu
    rỗng; các trường còn lại là text (NULL nếu giá trị vào là None)."""
    if field == "year_issue":
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(f"năm phát hành không hợp lệ: {value!r}") from None
    if value is None:
        return None
    return value if isinstance(value, str) else str(value)


def _txt(v):
    return None if v is None else str(v)


def set_field(conn, work_id, field, value, actor_id, reason):
    """Sửa một trường `EDITABLE` của một công trình còn sống. Bắt buộc lý do
    (khác rỗng); `ValueError` cho mọi lỗi nghiệp vụ (không tìm thấy, đã gộp,
    trường cấm, giá trị không hợp lệ, lý do trống) — tầng API map sang 404/409.
    Trả `{field, old, new}` với `old`/`new` là giá trị Python (int/str/None)
    trước và sau khi sửa. Một giao dịch: cập nhật `work` (và `title_norm` nếu
    sửa `title`), thêm `field_provenance(set_kind='manual', set_by=actor_id,
    raw_value=giá trị cũ, value=giá trị mới)`, ghi `audit.log('work.edit')`.
    """
    if field not in EDITABLE:
        raise ValueError(f"không cho phép chỉnh trường '{field}'; chỉ: {', '.join(EDITABLE)}")
    if not (reason or "").strip():
        raise ValueError("cần ghi lý do chỉnh sửa")

    with tx(conn), conn.cursor() as cur:
        cur.execute("SELECT * FROM work WHERE id=%s FOR UPDATE", (work_id,))
        w = cur.fetchone()
        if w is None:
            raise ValueError(f"không tìm thấy công trình: {work_id}")
        if w["merged_into_id"] is not None:
            raise ValueError("công trình đã gộp vào bản ghi khác, không thể chỉnh tay")

        new = _coerce(field, value)
        if field == "title" and not (new or "").strip():
            raise ValueError("tiêu đề không được để trống")
        old = w[field]

        sets = {field: new}
        if field == "title":
            sets["title_norm"] = RU.norm_title(new)
        set_sql = ", ".join(f"{k}=%s" for k in sets)
        cur.execute(f"UPDATE work SET {set_sql}, updated_at=now() WHERE id=%s",
                    (*sets.values(), work_id))

        cur.execute(
            "INSERT INTO field_provenance(work_id, field, raw_value, value, set_kind, set_by) "
            "VALUES (%s,%s,%s,%s,'manual',%s)",
            (work_id, field, _txt(old), _txt(new) or "", actor_id))

        audit.log(conn, actor_id, "work.edit", "work", work_id,
                  before={field: _txt(old)}, after={field: _txt(new), "reason": reason})

        return {"field": field, "old": old, "new": new}
