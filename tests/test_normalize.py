import json
import pytest
from cris import normalize, rules, sync

def q(conn, sql, *args):
    with conn.cursor() as cur:
        cur.execute(sql, args)
        return cur.fetchall()

@pytest.fixture
def seeded(conn):
    rules.seed_rules(conn, None)
    return rules.load_active(conn)

BAI_BAO = {
    "archive": {"url": "https://r/bai-bao/a/", "title": "Cocktail Party Effect", "authors": "The-Vinh Nguyen, Trung-Nghia P…",
                "pub_type": "Scopus Q2", "keywords": None, "journal": "ACS Omega", "volume": "Vol 9", "year": "2025"},
    "detail": {"url": "https://r/bai-bao/a/", "title": "Cocktail Party Effect",
               "authors": ["The-Vinh Nguyen", "Trung-Nghia Phung", "Nguyen Van Tao"],
               "doi": ["https://doi.org/10.1000/ABC"], "pdf": [], "mentors": [], "abstract": "x", "meta": {}},
}
DO_AN = {
    "archive": {"url": "https://r/do-an/b/", "title": "Xây dựng website bán hàng",
                "meta": {"Sinh viên": "Trần Văn A", "Khóa": "K18", "Năm": "2024"},
                "mentors": [{"name": "TS. Nguyễn Văn Tảo", "url": "https://r/giang-vien/tao/"}],
                "abstract": "tóm tắt", "keywords": "website; bán hàng"},
}

def load(conn, doc_type, raw, key):
    sync.run_sync(conn, source="repository", scope="t", doc_type=doc_type, records=[(key, raw)], expected=None, full=False)

def test_extract_fields_bai_bao(seeded):
    f = normalize.extract_fields({"doc_type": "bai_bao", "raw": BAI_BAO}, seeded)
    assert f["title_norm"] == "cocktail party effect"
    assert f["doi"] == "10.1000/abc"
    assert f["year_issue"] == 2025 and f["indexes"] == ["Scopus"] and f["quartile"] == "Q2"
    assert [m["raw_name"] for m in f["mentions"]] == ["The-Vinh Nguyen", "Trung-Nghia Phung", "Nguyen Van Tao"]
    assert f["authors_truncated"] is False      # trang chi tiết đủ, không cắt cụt

def test_extract_fields_do_an_student_cohort_mentor(seeded):
    f = normalize.extract_fields({"doc_type": "do_an", "raw": DO_AN}, seeded)
    assert f["cohort"] == "K18" and f["year_issue"] == 2024
    roles = [(m["role"], m["raw_name"]) for m in f["mentions"]]
    assert ("student", "Trần Văn A") in roles and ("mentor", "TS. Nguyễn Văn Tảo") in roles

def test_normalize_pending_writes_work_provenance_mentions(conn, seeded):
    load(conn, "bai_bao", BAI_BAO, "https://r/bai-bao/a/")
    out = normalize.normalize_pending(conn)
    assert out["created"] == 1
    w = q(conn, "SELECT * FROM work")[0]
    assert w["state"] == "DaChuanHoa" and w["doi"] == "10.1000/abc" and w["rule_set_id"] is not None
    prov = {r["field"]: r for r in q(conn, "SELECT * FROM field_provenance WHERE work_id=%s", w["id"])}
    assert prov["title"]["set_kind"] == "normalize" and prov["title"]["source_record_id"] is not None
    assert prov["pub_type_raw"]["raw_value"] == "Scopus Q2"
    ms = q(conn, "SELECT role, position, raw_name, name_key, degree_raw FROM author_mention WHERE work_id=%s ORDER BY position", w["id"])
    assert [m["raw_name"] for m in ms] == ["The-Vinh Nguyen", "Trung-Nghia Phung", "Nguyen Van Tao"]
    assert ms[2]["name_key"] == "nguyen tao van"

def test_normalize_is_idempotent_and_follows_new_version(conn, seeded):
    load(conn, "bai_bao", BAI_BAO, "https://r/bai-bao/a/")
    normalize.normalize_pending(conn)
    assert normalize.normalize_pending(conn)["skipped"] == 1
    changed = json.loads(json.dumps(BAI_BAO)); changed["archive"]["year"] = "2026"
    load(conn, "bai_bao", changed, "https://r/bai-bao/a/")
    out = normalize.normalize_pending(conn)
    assert out["updated"] == 1
    assert q(conn, "SELECT year_issue FROM work")[0]["year_issue"] == 2026
    years = q(conn, "SELECT value FROM field_provenance WHERE field='year_issue' ORDER BY set_at")
    assert [r["value"] for r in years] == ["2025", "2026"]
    assert len(q(conn, "SELECT 1 FROM work")) == 1

def test_placeholder_and_truncation_flags(conn, seeded):
    raw = {"archive": {"url": "https://r/do-an/c/", "title": "Đề tài X", "meta": {"Sinh viên": "Lê B", "Khóa": "K17"},
                       "mentors": [{"name": "ICTU_TEACHER", "url": ""}], "abstract": None, "keywords": None}}
    load(conn, "do_an", raw, "https://r/do-an/c/")
    normalize.normalize_pending(conn)
    m = q(conn, "SELECT is_placeholder FROM author_mention WHERE role='mentor'")[0]
    assert m["is_placeholder"] is True
    raw2 = {"archive": {"url": "https://r/bai-bao/d/", "title": "T", "authors": "A B, C D…", "pub_type": None, "year": "2020",
                        "journal": None, "volume": None, "keywords": None}, "detail_error": "timeout"}
    load(conn, "bai_bao", raw2, "https://r/bai-bao/d/")
    normalize.normalize_pending(conn)
    ms = q(conn, "SELECT is_truncated FROM author_mention WHERE work_id=(SELECT id FROM work WHERE title='T')")
    assert all(m["is_truncated"] for m in ms)

def test_unknown_pub_type_sets_needs_review_not_guess(conn, seeded):
    raw = json.loads(json.dumps(BAI_BAO)); raw["archive"]["pub_type"] = "Chưa xác định"; raw["archive"]["url"] = "https://r/bai-bao/e/"
    raw["detail"]["doi"] = []
    load(conn, "bai_bao", raw, "https://r/bai-bao/e/")
    normalize.normalize_pending(conn)
    w = q(conn, "SELECT needs_review, venue_kind, indexes FROM work")[0]
    assert w["needs_review"] is True and w["venue_kind"] is None and w["indexes"] == []
