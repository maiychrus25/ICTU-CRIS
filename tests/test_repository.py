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
    rows = list(R.iter_archive("bai-bao", fetch=fetch))
    assert len(rows) == len(R.parse_archive("bai-bao", h))
    assert len(calls) == 2 and calls[1].endswith("?pg=2")
