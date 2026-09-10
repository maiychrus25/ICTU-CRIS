# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import html
import re
import time
import urllib.parse
import urllib.request

BASE = "https://repository.ictu.edu.vn"
UA = "Mozilla/5.0 (X11; Linux x86_64) ictu-cris/0.1"
DELAY = 0.35

DOC_TYPES = {
    "bai-bao":     {"doc_type": "bai_bao",    "parser": "table"},
    "do-an":       {"doc_type": "do_an",      "parser": "card"},
    "luan-van":    {"doc_type": "luan_van",   "parser": "card"},
    "luan-an":     {"doc_type": "luan_an",    "parser": "card"},
    "hoc-lieu-so": {"doc_type": "hoc_lieu",   "parser": "card"},
    "giang-vien":  {"doc_type": "giang_vien", "parser": "gv"},
}

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "vi,en;q=0.8"})
            with urllib.request.urlopen(req, timeout=40) as r:
                body = r.read().decode("utf-8", "replace")
            time.sleep(DELAY)
            return body
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))

# --- sao chép nguyên văn từ harvest.py: text, main_block, total_of, parse_table, parse_card, parse_gv ---
def text(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s or "", flags=re.S)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"[ \t\xa0]+", " ", html.unescape(s)).strip()

def main_block(h):
    m = re.search(r'<main class="site-main" id="main">(.*?)</main>', h, re.S)
    return m.group(1) if m else h

def total_of(h):
    m = re.search(r'dl-info-bar[^>]*>(.*?)</div>', h, re.S)
    if not m:
        return None
    m2 = re.search(r"tổng số\s*<strong>([\d.,]+)</strong>", m.group(1))
    return int(re.sub(r"\D", "", m2.group(1))) if m2 else None

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

def archive_total(h):
    return total_of(h)

PARSERS = {"table": parse_table, "card": parse_card, "gv": parse_gv}

def parse_archive(path, h):
    return PARSERS[DOC_TYPES[path]["parser"]](main_block(h))

AUTHOR_LABELS = ("Tác giả", "Authors", "Author")

def parse_detail(h, url):
    b = main_block(h)
    rec = {"url": url}
    m = re.search(r'<(h1)[^>]*>(.*?)</h1>', b, re.S)
    rec["title"] = text(m.group(2)) if m else None
    rec["meta"] = {}
    for lab, val in re.findall(r'class="[^"]*(?:dl-meta-label|bb-meta-label|detail-label)[^"]*"[^>]*>(.*?)</\w+>\s*(?:<[^>]+>)?(.*?)(?=<)', b, re.S)[:40]:
        k, v = text(lab).rstrip(":"), text(val)
        if k and v:
            rec["meta"][k] = v
    rec["authors"] = None
    for lab in AUTHOR_LABELS:
        if lab in rec["meta"]:
            rec["authors"] = [a.strip() for a in re.split(r"[,;]", rec["meta"][lab]) if a.strip()]
            break
    # trang chi tiết thật không đưa tác giả vào bảng meta mà đặt trong
    # <div class="bb-authors-inline"> với mỗi tác giả là <a class="bb-author-link">
    if rec["authors"] is None:
        m = re.search(r'bb-authors-inline">(.*?)</div>\s*</section>', b, re.S)
        if m:
            names = [text(n) for n in re.findall(r'<a[^>]*class="bb-author-link"[^>]*>(.*?)</a>', m.group(1), re.S)]
            rec["authors"] = names or None
    rec["pdf"] = sorted(set(re.findall(r'href="([^"]*\.pdf)"', b)))
    rec["doi"] = sorted(set(re.findall(r'href="(https://doi\.org/[^"]+)"', b)))
    rec["mentors"] = sorted(set(re.findall(r'href="(%s/giang-vien/[^"]+)"' % re.escape(BASE), b)))
    ab = re.search(r'(?:Tóm tắt|Abstract)\s*</\w+>(.*?)(?:<h[23]|<div class="[^"]*cite)', b, re.S)
    rec["abstract"] = text(ab.group(1))[:4000] if ab else None
    return rec

def extract_orcid(h):
    m = re.search(r'orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])', h)
    return m.group(1) if m else None

# S-04 quét bù phân trang.
# Kho nguồn sắp xếp theo cột không duy nhất, nên LIMIT/OFFSET trả kết quả không
# ổn định ở chỗ có giá trị bằng nhau: một số bản ghi hiện lặp ở hai trang liền
# nhau và số khác không bao giờ lọt vào trang nào. Đo 09/2026: duyệt hết 269
# trang /do-an/ chỉ ra 5.364 trên 5.375 bản ghi. Bộ lọc phân hoạch kho theo
# trục khác nên chạm được phần bị bỏ sót.
FACET = {
    "bai-bao":  "dept",
    "do-an":    "cohort",
    "luan-van": "cohort",
    "luan-an":  "cohort",
}

def facet_options(h, name):
    """Giá trị bộ lọc trong <select name=...>, đã giải mã thực thể HTML.

    Giải mã là bắt buộc: value="KT&amp;CN" phải thành "KT&CN" trước khi mã hoá
    vào URL, nếu không kho trả về 0 kết quả.
    """
    m = re.search(r'<select[^>]*name="%s"[^>]*>(.*?)</select>' % re.escape(name), h, re.S)
    if not m:
        return []
    vals = (html.unescape(v) for v in re.findall(r'<option[^>]*value="([^"]*)"', m.group(1)))
    return [v for v in dict.fromkeys(vals) if v]

def _iter_facet(path, facet, value, fetch, max_pages):
    """Duyệt hết các trang của một giá trị bộ lọc."""
    q = urllib.parse.quote(value, safe="")
    seen, pg, total = set(), 1, None
    while pg <= max_pages:
        url = f"{BASE}/{path}/?{facet}={q}" + (f"&pg={pg}" if pg > 1 else "")
        h = fetch(url)
        if total is None:
            total = archive_total(h)
        fresh = [r for r in parse_archive(path, h) if r.get("url") and r["url"] not in seen]
        if not fresh:
            return
        for r in fresh:
            seen.add(r["url"])
            r["_page"] = pg
            yield r
        if total and len(seen) >= total:
            return
        pg += 1

def iter_archive(path, fetch=get, max_pages=400, backfill=True):
    seen, pg, total, first = set(), 1, None, None
    while pg <= max_pages:
        url = f"{BASE}/{path}/" + (f"?pg={pg}" if pg > 1 else "")
        h = fetch(url)
        if first is None:
            first = h
        if total is None:
            total = archive_total(h)
        new = [r for r in parse_archive(path, h) if r.get("url") and r["url"] not in seen]
        for r in new:
            seen.add(r["url"])
            r["_page"] = pg
            yield r
        if not new or (total and len(seen) >= total):
            break
        pg += 1

    # Lật trang xong mà vẫn thiếu so với số kho tự công bố: quét bù theo bộ lọc.
    facet = FACET.get(path)
    if not (backfill and facet and total and first is not None and len(seen) < total):
        return
    for value in facet_options(first, facet):
        if len(seen) >= total:
            return
        for r in _iter_facet(path, facet, value, fetch, max_pages):
            if r["url"] in seen:
                continue
            seen.add(r["url"])
            r["_backfill"] = {facet: value}
            yield r
