# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Đồ thị đồng tác giả (J2): giảng viên–giảng viên cùng đứng tên một công
trình đã liên kết, cho tab "Đồng tác giả" của bản đồ tri thức.

Tính trực tiếp mỗi lần gọi, chỉ đọc `v_person_publications` (liên kết sống —
mọi trạng thái trừ `DaBacBo`, cùng cách `cris.ai.expert` coi là "công trình
của người này") và `person`/`unit` — không ghi bảng nào.
"""


def coauthor_graph(conn, *, min_works=2, max_nodes=300):
    """Nút là người có ít nhất `min_works` công trình liên kết (đếm qua
    `v_person_publications`, không phân biệt loại công trình); cạnh là cặp
    người cùng đứng tên ít nhất một công trình, `weight` = số công trình
    chung (đếm theo `work_id` phân biệt, không nhân đôi khi một công trình có
    nhiều lượt tên cùng một người — hiếm nhưng dữ liệu nguồn có thể lặp).

    Cắt còn tối đa `max_nodes` nút, ưu tiên người có nhiều `works` nhất; cạnh
    chỉ giữ giữa hai nút còn lại sau khi cắt (không phải cạnh nào cũng còn cả
    hai đầu).

    Trả `{"nodes": [{"person_id","display_name","unit_code","works"}],
    "edges": [{"a","b","weight"}]}` — `nodes` sắp giảm dần theo `works`.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT person_id, work_id FROM v_person_publications")
        links = cur.fetchall()

    works_by_person: dict[int, set] = {}
    for r in links:
        works_by_person.setdefault(r["person_id"], set()).add(r["work_id"])

    eligible = {pid: len(ws) for pid, ws in works_by_person.items() if len(ws) >= min_works}
    if not eligible:
        return {"nodes": [], "edges": []}

    top_ids = sorted(eligible, key=lambda pid: (-eligible[pid], pid))[:max_nodes]
    top_set = set(top_ids)

    with conn.cursor() as cur:
        cur.execute(
            "SELECT p.id, p.display_name, u.code AS unit_code FROM person p "
            "LEFT JOIN unit u ON u.id = p.unit_id WHERE p.id = ANY(%s)",
            (top_ids,),
        )
        info = {r["id"]: r for r in cur.fetchall()}

    nodes = [
        {"person_id": pid, "display_name": info[pid]["display_name"], "unit_code": info[pid]["unit_code"],
         "works": eligible[pid]}
        for pid in top_ids if pid in info
    ]

    by_work: dict[int, set] = {}
    for r in links:
        if r["person_id"] in top_set:
            by_work.setdefault(r["work_id"], set()).add(r["person_id"])

    weight: dict[tuple, int] = {}
    for pids in by_work.values():
        ordered = sorted(pids)
        for i in range(len(ordered)):
            for j in range(i + 1, len(ordered)):
                key = (ordered[i], ordered[j])
                weight[key] = weight.get(key, 0) + 1

    edges = [{"a": a, "b": b, "weight": w} for (a, b), w in weight.items()]
    return {"nodes": nodes, "edges": edges}
