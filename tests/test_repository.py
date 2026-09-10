# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import pathlib
from cris.source import repository as R

FX = pathlib.Path(__file__).parent / "fixtures"

def test_archive_total_and_rows_bai_bao():
    h = (FX / "bai-bao-archive.html").read_text(encoding="utf-8")
    assert R.archive_total(h) and R.archive_total(h) > 1000
    rows = R.parse_archive("bai-bao", h)
    assert len(rows) >= 3
    r = rows[0]
    assert r["url"].startswith("https://repository.ictu.edu.vn/bai-bao/")
    assert r["title"] and r["year"]
    assert "authors" in r and "pub_type" in r

def test_parse_archive_do_an_has_meta_and_mentors():
    rows = R.parse_archive("do-an", (FX / "do-an-archive.html").read_text(encoding="utf-8"))
    assert rows and isinstance(rows[0]["meta"], dict) and isinstance(rows[0]["mentors"], list)

def test_parse_archive_giang_vien_has_identity_fields():
    rows = R.parse_archive("giang-vien", (FX / "giang-vien-archive.html").read_text(encoding="utf-8"))
    assert len(rows) == 28
    assert rows[0]["url"] and rows[0]["name"]
    assert "email" in rows[0] and "degree" in rows[0]

def test_parse_detail_bai_bao_authors_and_doi():
    d = R.parse_detail((FX / "bai-bao-detail.html").read_text(encoding="utf-8"),
                       "https://repository.ictu.edu.vn/bai-bao/x/")
    assert d["title"]
    assert d["authors"] == [
        "Thi Minh-Hue Luong", "The-Vinh Nguyen", "Van-Viet Nguyen", "Duc-Quang Vu", "Trung-Nghia Phung",
    ]
    assert isinstance(d["doi"], list) and isinstance(d["pdf"], list)

def test_iter_archive_stops_when_no_new_rows():
    h = (FX / "bai-bao-archive.html").read_text(encoding="utf-8")
    calls = []
    def fetch(url):
        calls.append(url)
        return h                      # mọi trang trả cùng nội dung → trang 2 không có bản ghi mới
    rows = list(R.iter_archive("bai-bao", fetch=fetch, backfill=False))
    assert len(rows) == len(R.parse_archive("bai-bao", h))
    assert len(calls) == 2 and calls[1].endswith("?pg=2")

# ── S-04: quét bù phân trang ────────────────────────────────────────────────

def _card(n):
    return (f'<div class="lv-card dl-card"><a class="lv-card-title" '
            f'href="https://repository.ictu.edu.vn/do-an/d{n}/" title="Đồ án {n}">Đồ án {n}</a>'
            f'<div class="lv-card-meta"></div></div>')

def _archive(items, total, cohorts=("21", "20")):
    opts = '<option value="">— Tất cả khoá —</option>' + "".join(
        f'<option value="{c}">Khoá {c}</option>' for c in cohorts)
    return ('<main class="site-main" id="main">'
            f'<select name="cohort">{opts}</select>'
            f'<div class="dl-info-bar">Hiển thị <strong>1–2</strong> trong tổng số <strong>{total}</strong> đồ án</div>'
            + "".join(_card(i) for i in items) + "</main>")

def _ids(rows):
    return [r["url"].rstrip("/").rsplit("/", 1)[-1] for r in rows]

def test_facet_options_unescapes_html_entities():
    h = '<select name="dept"><option value=""></option><option value="KT&amp;CN">KT&amp;CN</option></select>'
    assert R.facet_options(h, "dept") == ["KT&CN"]

def test_facet_options_absent_select_is_empty():
    assert R.facet_options("<main></main>", "cohort") == []

def test_backfill_recovers_records_paging_never_reaches():
    """Trang 2 lặp lại d2 của trang 1 nên d4 không bao giờ lọt vào trang nào —
    đúng lỗi của kho: 269 trang /do-an/ chỉ ra 5.364 trên 5.375 bản ghi."""
    pages = {
        "https://repository.ictu.edu.vn/do-an/":              _archive([1, 2], 4),
        "https://repository.ictu.edu.vn/do-an/?pg=2":         _archive([2, 3], 4),
        "https://repository.ictu.edu.vn/do-an/?pg=3":         _archive([3], 4),
        "https://repository.ictu.edu.vn/do-an/?cohort=21":    _archive([1, 4], 2),
        "https://repository.ictu.edu.vn/do-an/?cohort=20":    _archive([2, 3], 2),
    }
    calls = []
    def fetch(url):
        calls.append(url)
        return pages[url]
    rows = list(R.iter_archive("do-an", fetch=fetch))
    assert _ids(rows) == ["d1", "d2", "d3", "d4"]
    assert rows[-1]["_backfill"] == {"cohort": "21"}
    assert "https://repository.ictu.edu.vn/do-an/?cohort=20" not in calls  # đủ số thì dừng

def test_backfill_skipped_when_paging_is_complete():
    pages = {
        "https://repository.ictu.edu.vn/do-an/":      _archive([1, 2], 2),
        "https://repository.ictu.edu.vn/do-an/?pg=2": _archive([], 2),
    }
    calls = []
    def fetch(url):
        calls.append(url)
        return pages[url]
    rows = list(R.iter_archive("do-an", fetch=fetch))
    assert _ids(rows) == ["d1", "d2"]
    assert not any("cohort=" in u for u in calls)

def test_backfill_can_be_turned_off():
    pages = {
        "https://repository.ictu.edu.vn/do-an/":      _archive([1, 2], 4),
        "https://repository.ictu.edu.vn/do-an/?pg=2": _archive([2], 4),
    }
    rows = list(R.iter_archive("do-an", fetch=lambda u: pages[u], backfill=False))
    assert _ids(rows) == ["d1", "d2"]

def test_backfill_url_encodes_facet_value():
    seen = []
    def fetch(url):
        seen.append(url)
        if "dept=" in url:
            return _archive([], 0)
        return ('<main class="site-main" id="main">'
                '<select name="dept"><option value="KT&amp;CN">KT&amp;CN</option></select>'
                '<div class="dl-info-bar">tổng số <strong>9</strong> bài báo</div></main>')
    list(R.iter_archive("bai-bao", fetch=fetch))
    assert any("?dept=KT%26CN" in u for u in seen)
