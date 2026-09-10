#!/usr/bin/env python3
"""
Harvester cho repository.ictu.edu.vn (DSpace-ICTU, WordPress + CPT tự viết).

Site khong co REST API cho cac CPT hoc thuat -> parse HTML archive (?pg=N).
  bai-bao   1907  20/trang   96 trang   (bang <table class="bb-table">)
  do-an     5375  20/trang  269 trang   (card .lv-card)
  luan-van   323  10/trang   33 trang   (card .lv-card)
  luan-an     11  10/trang    2 trang   (card .lv-card)
  hoc-lieu-so  2                        (card .lv-card)
  giang-vien 410  1 trang               (article .gv-card, co microdata)

Usage:
  python3 harvest.py archives            # kéo toàn bộ danh mục -> out/*.jsonl
  python3 harvest.py details <type> [N]  # kéo trang chi tiết (N = giới hạn)
  python3 harvest.py csv                 # xuất CSV từ jsonl
"""
import json, re, sys, time, html, pathlib, urllib.parse
import urllib.request

BASE = "https://repository.ictu.edu.vn"
UA = "Mozilla/5.0 (X11; Linux x86_64) research-harvester/1.0"
OUT = pathlib.Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)
DELAY = 0.35  # lịch sự: ~3 req/s

TYPES = {
    "bai-bao":     {"per": 20, "parser": "table"},
    "do-an":       {"per": 20, "parser": "card"},
    "luan-van":    {"per": 10, "parser": "card"},
    "luan-an":     {"per": 10, "parser": "card"},
    "hoc-lieu-so": {"per": 20, "parser": "card"},
    "giang-vien":  {"per": 10**9, "parser": "gv"},
}

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                    "Accept-Language": "vi,en;q=0.8"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))

def text(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s or "", flags=re.S)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"[ \t ]+", " ", html.unescape(s)).strip()

def main_block(h):
    m = re.search(r'<main class="site-main" id="main">(.*?)</main>', h, re.S)
    return m.group(1) if m else h

def total_of(h):
    m = re.search(r'dl-info-bar[^>]*>(.*?)</div>', h, re.S)
    if not m:
        return None
    m2 = re.search(r"tổng số\s*<strong>([\d.,]+)</strong>", m.group(1))
    return int(re.sub(r"\D", "", m2.group(1))) if m2 else None

# ---------- parsers ----------
def parse_table(b):          # bai-bao
    out = []
    for tr in re.findall(r'<tr class="bb-row">(.*?)</tr>', b, re.S):
        def td(cls):
            m = re.search(r'<td class="%s">(.*?)</td>' % cls, tr, re.S)
            return m.group(1) if m else ""
        a = re.search(r'<a class="bb-title-link" href="([^"]+)"[^>]*title="([^"]*)"', td("bb-col-title"))
        j = td("bb-col-journal")
        out.append({
            "url":      a.group(1) if a else None,
            "title":    html.unescape(a.group(2)) if a else None,
            "authors":  text(re.search(r'bb-authors-line">(.*?)</div>', tr, re.S).group(1))
                        if "bb-authors-line" in tr else None,
            "pub_type": text(td("bb-col-type")) or None,
            "keywords": text(td("bb-col-keywords")) or None,
            "journal":  text(re.search(r'bb-journal-name">(.*?)</span>', j, re.S).group(1))
                        if "bb-journal-name" in j else None,
            "volume":   text(re.search(r'bb-vip">(.*?)</span>', j, re.S).group(1))
                        if "bb-vip" in j else None,
            "year":     text(td("bb-col-year")) or None,
        })
    return out

def parse_card(b):           # do-an / luan-van / luan-an / hoc-lieu-so
    out = []
    for c in re.findall(r'<div class="lv-card dl-card">(.*?)(?=<div class="lv-card dl-card">|<div class="dl-pagination|\Z)', b, re.S):
        a = re.search(r'<a class="lv-card-title" href="([^"]+)"[^>]*title="([^"]*)"', c)
        meta = {}
        mb = re.search(r'lv-card-meta">(.*?)</div>\s*(?:<div class="lv-card-(?:abstract|keywords)"|</div>)', c, re.S)
        for it in re.findall(r'<span class="dl-meta-item">(.*?)</span>\s*(?=<span class="dl-meta-item"|\Z)', mb.group(1) if mb else "", re.S):
            lb = re.search(r'dl-meta-label">(.*?)</span>(.*)', it, re.S)
            if lb:
                meta[text(lb.group(1)).rstrip(":")] = text(lb.group(2))
        mentors = [{"name": text(n), "url": u} for u, n in
                   re.findall(r'href="([^"]+)" class="lv-mentor-link">([^<]*)</a>', c)]
        ab = re.search(r'lv-card-abstract">(.*?)</div>', c, re.S)
        kw = re.search(r'lv-card-keywords">(.*?)</div>', c, re.S)
        out.append({
            "url":       a.group(1) if a else None,
            "title":     html.unescape(a.group(2)) if a else None,
            "meta":      meta,
            "mentors":   mentors,
            "abstract":  text(ab.group(1)) if ab else None,
            "keywords":  text(kw.group(1)).removeprefix("Từ khóa").strip() if kw else None,
        })
    return out

def parse_gv(b):             # giang-vien: microdata + data-* attrs
    out = []
    for c in re.findall(r'<article class="gv-card dl-card"(.*?)</article>', b, re.S):
        a = re.search(r'<a href="([^"]+)" itemprop="url">(.*?)</a>', c, re.S)
        rec = {
            "url":       a.group(1) if a else None,
            "display":   text(a.group(2)) if a else None,
            "name":      (re.search(r'data-name="([^"]*)"', c) or [None, None])[1] if 'data-name' in c else None,
            "rank":      (re.search(r'data-rank="([^"]*)"', c) or [None, None])[1] if 'data-rank' in c else None,
            "degree":    (re.search(r'data-degree="([^"]*)"', c) or [None, None])[1] if 'data-degree' in c else None,
            "position":  (re.search(r'data-position="([^"]*)"', c) or [None, None])[1] if 'data-position' in c else None,
            "avatar":    (re.search(r'class="gv-avatar-img"', c) and
                          re.search(r'<img src="([^"]+)"', c).group(1)) or None,
            "email":     (re.search(r'href="mailto:([^"]+)"', c) or [None, None])[1] if 'mailto:' in c else None,
        }
        for prop in ("jobTitle", "knowsAbout", "honorificPrefix"):
            m = re.search(r'itemprop="%s">(.*?)</span>' % prop, c, re.S)
            rec[prop] = text(m.group(1)) if m else None
        out.append(rec)
    return out

PARSERS = {"table": parse_table, "card": parse_card, "gv": parse_gv}

# ---------- drivers ----------
def harvest_archive(t):
    cfg = TYPES[t]
    fn = OUT / f"{t}.jsonl"
    seen, rows, pg, total = set(), [], 1, None
    while True:
        url = f"{BASE}/{t}/" + (f"?pg={pg}" if pg > 1 else "")
        h = get(url)
        b = main_block(h)
        if total is None:
            total = total_of(h)
            print(f"  [{t}] tổng: {total}", file=sys.stderr)
        batch = PARSERS[cfg["parser"]](b)
        new = [r for r in batch if r.get("url") and r["url"] not in seen]
        for r in new:
            seen.add(r["url"])
            r["_type"], r["_page"] = t, pg
        rows += new
        print(f"  [{t}] pg={pg} +{len(new)} (Σ{len(rows)})", file=sys.stderr)
        if not new or (total and len(rows) >= total) or pg > 400:
            break
        pg += 1
        time.sleep(DELAY)
    with fn.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  [{t}] -> {fn} ({len(rows)}/{total})", file=sys.stderr)
    return len(rows), total

def parse_detail(h, url):
    b = main_block(h)
    rec = {"url": url}
    m = re.search(r'<(h1)[^>]*>(.*?)</h1>', b, re.S)
    rec["title"] = text(m.group(2)) if m else None
    # bảng meta chi tiết (label/value)
    for lab, val in re.findall(r'class="[^"]*(?:dl-meta-label|bb-meta-label|detail-label)[^"]*"[^>]*>(.*?)</\w+>\s*(?:<[^>]+>)?(.*?)(?=<)', b, re.S)[:40]:
        k, v = text(lab).rstrip(":"), text(val)
        if k and v:
            rec.setdefault("meta", {})[k] = v
    rec["pdf"]  = sorted(set(re.findall(r'href="([^"]*\.pdf)"', b)))
    rec["doi"]  = sorted(set(re.findall(r'href="(https://doi\.org/[^"]+)"', b)))
    rec["mentors"] = sorted(set(re.findall(r'href="(%s/giang-vien/[^"]+)"' % re.escape(BASE), b)))
    ab = re.search(r'(?:Tóm tắt|Abstract)\s*</\w+>(.*?)(?:<h[23]|<div class="[^"]*cite)', b, re.S)
    rec["abstract"] = text(ab.group(1))[:4000] if ab else None
    bib = re.search(r'@\w+\{.*?\n\}', text(b), re.S)
    rec["bibtex"] = bib.group(0) if bib else None
    return rec

def harvest_details(t, limit=None):
    src = OUT / f"{t}.jsonl"
    urls = [json.loads(l)["url"] for l in src.open(encoding="utf-8") if l.strip()]
    if limit:
        urls = urls[:int(limit)]
    fn = OUT / f"{t}.details.jsonl"
    with fn.open("w", encoding="utf-8") as f:
        for i, u in enumerate(urls, 1):
            try:
                f.write(json.dumps(parse_detail(get(u), u), ensure_ascii=False) + "\n")
            except Exception as e:
                f.write(json.dumps({"url": u, "_error": str(e)}, ensure_ascii=False) + "\n")
            if i % 25 == 0:
                print(f"  [{t}] detail {i}/{len(urls)}", file=sys.stderr); f.flush()
            time.sleep(DELAY)
    print(f"  [{t}] -> {fn} ({len(urls)})", file=sys.stderr)

def to_csv():
    import csv
    for p in sorted(OUT.glob("*.jsonl")):
        rows = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
        if not rows:
            continue
        flat = []
        for r in rows:
            d = {}
            for k, v in r.items():
                if isinstance(v, dict):
                    for k2, v2 in v.items():
                        d[f"{k}.{k2}"] = v2
                elif isinstance(v, list):
                    d[k] = " | ".join(x if isinstance(x, str) else json.dumps(x, ensure_ascii=False) for x in v)
                else:
                    d[k] = v
            flat.append(d)
        cols = list(dict.fromkeys(k for d in flat for k in d))
        out = p.with_suffix(".csv")
        with out.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(flat)
        print(f"  {out.name}: {len(flat)} dòng, {len(cols)} cột", file=sys.stderr)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "archives"
    if cmd == "archives":
        which = sys.argv[2:] or list(TYPES)
        for t in which:
            harvest_archive(t)
    elif cmd == "details":
        harvest_details(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "csv":
        to_csv()
