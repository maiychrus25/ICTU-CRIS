# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import argparse
import json
import sys
from cris import db, dedup, link, normalize, people, quality, rules, sync
from cris.source import repository as R

def main(argv=None):
    ap = argparse.ArgumentParser(prog="cris")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("migrate"); sub.add_parser("seed")
    s = sub.add_parser("sync"); s.add_argument("paths", nargs="*", default=list(R.DOC_TYPES)); s.add_argument("--no-details", action="store_true")
    sub.add_parser("people"); sub.add_parser("normalize"); sub.add_parser("link"); sub.add_parser("dedup")
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
    sv = sub.add_parser("serve"); sv.add_argument("--host", default="127.0.0.1"); sv.add_argument("--port", type=int, default=8000)
    sv.add_argument("--legacy", action="store_true", help="chạy UI HTML cũ (WSGI) thay vì API FastAPI")
    a = ap.parse_args(argv)
    if a.cmd == "serve":
        if a.legacy:
            from cris.web.wsgi import serve
            serve(a.host, a.port)
        else:
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
        print(normalize.normalize_pending(conn))
    elif a.cmd == "link":
        print(link.link_pending(conn))
    elif a.cmd == "dedup":
        print(dedup.find_duplicates(conn))
    elif a.cmd == "ai":
        from cris.ai import embed as ai_embed, provider as ai_provider   # import muộn: gói lõi không cần onnxruntime
        if a.ai_cmd == "download":
            from cris.ai.local import ensure_model
            print(ensure_model(log=lambda m: print(m, file=sys.stderr)))
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
    elif a.cmd == "quality":
        r = quality.report(conn)
        print(json.dumps(r, ensure_ascii=False, indent=None if a.json else 2))
    conn.close()

if __name__ == "__main__":
    main()
