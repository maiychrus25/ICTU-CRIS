# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import argparse
import getpass
import json
import os
import sys

from cris import auth, db, dedup, link, normalize, people, quality, rules, sync
from cris.source import repository as R


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cris")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("migrate"); sub.add_parser("seed")
    s = sub.add_parser("sync"); s.add_argument("paths", nargs="*", default=list(R.DOC_TYPES)); s.add_argument("--no-details", action="store_true")
    sub.add_parser("people")
    np = sub.add_parser("normalize")
    np.add_argument("--redo", action="store_true", help="chuẩn hoá lại toàn bộ bản ghi sống, không chỉ phần đang chờ")
    np.add_argument("--doc-type", choices=list(normalize.WORK_TYPES), help="chỉ chuẩn hoá một loại (mặc định: tất cả)")
    sub.add_parser("link"); sub.add_parser("dedup")
    qp = sub.add_parser("quality"); qp.add_argument("--json", action="store_true")
    ai = sub.add_parser("ai", help="vector ngữ nghĩa và gợi ý (cần CRIS_AI_PROVIDER)")
    ais = ai.add_subparsers(dest="ai_cmd", required=True)
    e = ais.add_parser("embed"); e.add_argument("--all", action="store_true", help="tính lại toàn bộ, không chỉ phần đổi")
    ais.add_parser("status"); ais.add_parser("download")
    tp = ais.add_parser("topics"); tp.add_argument("--k", type=int, default=40, help="số cụm mong muốn")
    ais.add_parser("suggest")
    sc = ais.add_parser("screen", help="rà soát trùng đề tài của một khoá với các khoá khác")
    sc.add_argument("--cohort", required=True); sc.add_argument("--k", type=int, default=3)
    sc.add_argument("--high", type=float, default=None, help="ngưỡng mức 'cao' (mặc định SCREEN_THRESHOLDS[0]=0.90)")
    sc.add_argument("--mid", type=float, default=None, help="ngưỡng mức 'vua' (mặc định SCREEN_THRESHOLDS[1]=0.80)")
    mt = ais.add_parser("mentors", help="gợi ý người hướng dẫn thật cho đồ án đang ghi ICTU_TEACHER")
    mt.add_argument("--k", type=int, default=5, help="số đồ án láng giềng tìm mỗi đích (mặc định 5)")
    mt.add_argument("--min-votes", type=int, default=2, help="số láng giềng tối thiểu cùng một người (mặc định 2)")
    mt.add_argument("--min-score", type=float, default=0.70, help="tổng cosine tối thiểu (mặc định 0.70)")
    ex = ais.add_parser("experts", help="tìm giảng viên gần chuyên môn với một đề tài (J1)")
    ex.add_argument("title")
    ex.add_argument("--description", default="")
    ex.add_argument("--k", type=int, default=10)
    sv = sub.add_parser("serve"); sv.add_argument("--host", default="127.0.0.1"); sv.add_argument("--port", type=int, default=8000)
    u = sub.add_parser("user", help="đăng nhập cục bộ (NFR-01)")
    us = u.add_subparsers(dest="user_cmd", required=True)
    sp = us.add_parser("set-password", help="đọc mật khẩu từ biến CRIS_PASSWORD hoặc hỏi (getpass)")
    sp.add_argument("email")
    us.add_parser("list")
    uc = us.add_parser("create", help="tạo tài khoản mới (lát cắt H1)")
    uc.add_argument("--email", required=True)
    uc.add_argument("--name", required=True)
    uc.add_argument("--roles", required=True, help="phân tách bằng dấu phẩy, vd: faculty_officer,rd_officer")
    uc.add_argument("--unit", help="mã đơn vị (unit.code)")
    uc.add_argument("--password", help="đặt mật khẩu ngay; mặc định không đặt (giữ chế độ mở, NFR-01)")
    su = us.add_parser("set-unit", help="gán/đổi đơn vị của một tài khoản")
    su.add_argument("--email", required=True)
    su.add_argument("--unit", required=True, help="mã đơn vị (unit.code)")
    cl = us.add_parser("create-lecturers", help="tạo tài khoản lecturer từ person.kind='lecturer' có email (lát cắt H3)")
    cl.add_argument("--unit", help="mã đơn vị (unit.code), lọc theo person.unit_id")
    cl.add_argument("--dry-run", action="store_true", help="chỉ đếm, không ghi")
    a = ap.parse_args(argv)
    if a.cmd == "serve":
        import uvicorn
        uvicorn.run("cris.api.app:app", host=a.host, port=a.port)
        return
    conn = db.connect()
    if a.cmd == "migrate":
        print(db.migrate(conn))
    elif a.cmd == "seed":
        print(rules.seed_rules(conn, None))
    elif a.cmd == "sync":
        for p in a.paths:
            rid = sync.sync_repository(conn, p, with_details=not a.no_details)
            with conn.cursor() as cur:
                cur.execute("SELECT status, added, changed, vanished, warnings FROM sync_run WHERE id=%s", (rid,))
                print(p, dict(cur.fetchone()), file=sys.stderr)
    elif a.cmd == "people":
        print(people.import_people(conn))
    elif a.cmd == "normalize":
        print(normalize.normalize_pending(conn, force=a.redo, doc_type=a.doc_type))
    elif a.cmd == "link":
        print(link.link_pending(conn))
    elif a.cmd == "dedup":
        print(dedup.find_duplicates(conn))
    elif a.cmd == "ai":
        from cris.ai import (  # import muộn: gói lõi không cần onnxruntime
            embed as ai_embed,
        )
        from cris.ai import provider as ai_provider
        if a.ai_cmd == "download":
            from cris.ai.local import ensure_model
            # Cùng thư mục với provider local (CRIS_AI_MODEL_DIR), để tải một lần rồi dùng
            # được ngay trong container/volume thay vì rơi vào cache riêng của người dùng.
            print(ensure_model(model_dir=os.environ.get("CRIS_AI_MODEL_DIR") or None,
                               log=lambda m: print(m, file=sys.stderr)))
        else:
            prov = ai_provider.get_provider()
            if a.ai_cmd == "status":
                print(json.dumps(ai_embed.status(conn, prov), ensure_ascii=False, indent=2, default=str))
            elif a.ai_cmd == "embed":
                prog = lambda done, total: print(f"  {done}/{total}", file=sys.stderr) if done % 200 == 0 or done == total else None
                print(ai_embed.build_embeddings(conn, prov, only_missing=not a.all, progress=prog))
            elif a.ai_cmd == "topics":
                from cris.ai import topics as ai_topics
                print(ai_topics.build_topics(conn, prov, k=a.k))
            elif a.ai_cmd == "suggest":
                from cris.ai import suggest as ai_suggest
                print({"author_link": ai_suggest.suggest_author_links(conn, prov),
                       "duplicate": ai_suggest.suggest_duplicates(conn, prov)})
            elif a.ai_cmd == "screen":
                from cris.ai import screen as ai_screen
                high = a.high if a.high is not None else ai_screen.SCREEN_THRESHOLDS[0]
                mid = a.mid if a.mid is not None else ai_screen.SCREEN_THRESHOLDS[1]
                r = ai_screen.screen_cohort(conn, prov, cohort=a.cohort, k=a.k, thresholds=(high, mid))
                print(f"screened={r['screened']} flagged={r['flagged']}")
            elif a.ai_cmd == "mentors":
                from cris.ai import mentor as ai_mentor
                r = ai_mentor.suggest_mentors(conn, prov, k=a.k, min_votes=a.min_votes, min_score=a.min_score)
                print(f"scanned={r['scanned']} suggested={r['suggested']}")
            elif a.ai_cmd == "experts":
                from cris.ai import expert as ai_expert
                r = ai_expert.find_experts(conn, prov, title=a.title, description=a.description, k=a.k, save=False)
                if r["fallback"]:
                    print(r["note"], file=sys.stderr)
                else:
                    print(f"{'điểm':>8}  {'bài khớp':>8}  giảng viên")
                    for row in r["results"]:
                        print(f"{row['score']:8.3f}  {row['works_matched']:8d}  "
                              f"{row['display_name']} ({row['degree'] or '—'}, {row['unit_code'] or '—'})")
    elif a.cmd == "quality":
        r = quality.report(conn)
        print(json.dumps(r, ensure_ascii=False, indent=None if a.json else 2))
    elif a.cmd == "user":
        if a.user_cmd == "set-password":
            pw = os.environ.get("CRIS_PASSWORD") or getpass.getpass(f"Mật khẩu cho {a.email}: ")
            uid = auth.set_password(conn, a.email, pw)
            print(f"đã đặt mật khẩu cho #{uid} ({a.email})")
        elif a.user_cmd == "list":
            for row in auth.list_users(conn):
                print(json.dumps({k: row[k] for k in
                                  ("id", "email", "display_name", "roles", "unit_id", "active", "has_password")},
                                 ensure_ascii=False))
        elif a.user_cmd == "create":
            roles = [r.strip() for r in a.roles.split(",") if r.strip()]
            unit_id = None
            if a.unit:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM unit WHERE code=%s", (a.unit,))
                    urow = cur.fetchone()
                if urow is None:
                    conn.rollback(); conn.close()
                    print(f"không tìm thấy đơn vị có mã: {a.unit}", file=sys.stderr)
                    sys.exit(1)
                unit_id = urow["id"]
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO app_user(email, display_name, roles, unit_id) VALUES (%s,%s,%s,%s) RETURNING id",
                    (a.email, a.name, roles, unit_id))
                uid = cur.fetchone()["id"]
            conn.commit()
            if a.password:
                auth.set_password(conn, a.email, a.password)
            print(f"đã tạo #{uid} ({a.email}, vai trò: {', '.join(roles)}"
                  f"{', đơn vị: ' + a.unit if a.unit else ''})")
        elif a.user_cmd == "set-unit":
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM unit WHERE code=%s", (a.unit,))
                urow = cur.fetchone()
            if urow is None:
                conn.rollback(); conn.close()
                print(f"không tìm thấy đơn vị có mã: {a.unit}", file=sys.stderr)
                sys.exit(1)
            with conn.cursor() as cur:
                cur.execute("UPDATE app_user SET unit_id=%s WHERE email=%s RETURNING id", (urow["id"], a.email))
                urow2 = cur.fetchone()
            if urow2 is None:
                conn.rollback(); conn.close()
                print(f"không tìm thấy người dùng: {a.email}", file=sys.stderr)
                sys.exit(1)
            conn.commit()
            print(f"đã gán #{urow2['id']} ({a.email}) vào đơn vị {a.unit}")
        elif a.user_cmd == "create-lecturers":
            result = auth.create_lecturers(conn, unit_code=a.unit, dry_run=a.dry_run)
            verb = "sẽ tạo" if a.dry_run else "đã tạo"
            print(f"{verb} {result['created']} tài khoản lecturer, bỏ qua {result['skipped']} (đã có tài khoản)")
    conn.close()

if __name__ == "__main__":
    main()
