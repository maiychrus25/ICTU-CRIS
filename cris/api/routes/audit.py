# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Nhật ký thao tác (SC-08, minh bạch): đọc `audit_log` JOIN `app_user`, không ghi gì
— mọi ghi nhận đi qua `cris.audit.log` từ tầng nghiệp vụ. Cần đăng nhập khi
`auth_required` (NFR-01/G2); chế độ mở giữ công khai như trước."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from cris.api.deps import Conn, require_login
from cris.api.schemas import AuditList, AuditRow, Page

router = APIRouter(prefix="/api", tags=["nhat-ky"])
RequireLogin = Annotated[dict | None, Depends(require_login)]

PER_PAGE = 50

ACTION_LABELS = {
    "link.confirm": "Xác nhận liên kết",
    "link.reject": "Bác bỏ liên kết",
    "link.reassign": "Chuyển liên kết cho người khác",
    "dup.merge": "Gộp bản ghi trùng",
    "dup.keep": "Giữ riêng",
    "dup.skip": "Bỏ qua nhóm trùng",
    "period.open": "Mở kỳ báo cáo",
    "period.close_submissions": "Đóng nộp kỳ báo cáo",
    "period.cancel": "Huỷ kỳ báo cáo",
    "source_record.new_version": "Nguồn có phiên bản mới",
    "mention.orphaned": "Lượt tên mất nguồn",
}


@router.get("/audit", response_model=AuditList)
def list_audit(conn: Conn, _login: RequireLogin, entity: str = "", entity_id: int | None = None,
               actor: int | None = None, page: int = Query(1, ge=1)):
    where, params = [], []
    if entity:
        where.append("a.entity = %s"); params.append(entity)
    if entity_id is not None:
        where.append("a.entity_id = %s"); params.append(entity_id)
    if actor is not None:
        where.append("a.actor_id = %s"); params.append(actor)
    where_sql = " AND ".join(where) if where else "TRUE"
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) AS n FROM audit_log a WHERE {where_sql}", params)
        total = cur.fetchone()["n"]
        cur.execute(
            f"SELECT a.id, a.at, a.action, a.entity, a.entity_id, a.before, a.after, "
            f"u.display_name AS actor_name "
            f"FROM audit_log a LEFT JOIN app_user u ON u.id = a.actor_id "
            f"WHERE {where_sql} ORDER BY a.at DESC, a.id DESC LIMIT %s OFFSET %s",
            params + [PER_PAGE, (page - 1) * PER_PAGE])
        rows = cur.fetchall()
    items = [
        AuditRow(id=r["id"], at=r["at"], actor_name=r["actor_name"], action=r["action"],
                 action_label=ACTION_LABELS.get(r["action"], r["action"]), entity=r["entity"],
                 entity_id=r["entity_id"], before=r["before"], after=r["after"])
        for r in rows
    ]
    return AuditList(items=items, page=Page(page=page, per_page=PER_PAGE, total=total))
