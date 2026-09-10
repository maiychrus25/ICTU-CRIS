import pytest
from cris import rules

NB = rules.RULES_V1["name_norm"]
PB = rules.RULES_V1["pub_type_map"]

@pytest.mark.parametrize("raw, norm, degree", [
    ("TS. Nguyễn Văn Tảo", "nguyen van tao", "TS"),
    ("T.s Nguyễn Văn Tảo", "nguyen van tao", "TS"),
    ("Ths. Nông Thị Hoa", "nong thi hoa", "ThS"),
    ("PGS.TS Đoàn Văn Ban", "doan van ban", "PGS.TS"),
    ("The-Vinh Nguyen", "the vinh nguyen", None),
    ("Trần Văn-Khánh", "tran van khanh", None),
    ("  Nguyễn   Đình Dũng ", "nguyen dinh dung", None),
])
def test_norm_name(raw, norm, degree):
    assert rules.norm_name(raw, NB) == (norm, degree)

def test_name_key_matches_reordered_names():
    a, _ = rules.norm_name("The-Vinh Nguyen", NB)
    b, _ = rules.norm_name("Nguyễn Thế Vịnh", NB)
    assert rules.name_key(a) == rules.name_key(b) == "nguyen the vinh"

def test_split_names_handles_comma_and_truncation():
    names, trunc = rules.split_names("Phạm Thanh Giang, Trần Duy Minh")
    assert names == ["Phạm Thanh Giang", "Trần Duy Minh"] and trunc is False
    names, trunc = rules.split_names("Minh-Hue Luong Thi, The-Vinh Nguyen, Trung-Nghia P…")
    assert names == ["Minh-Hue Luong Thi", "The-Vinh Nguyen", "Trung-Nghia P"] and trunc is True

@pytest.mark.parametrize("raw, expected", [
    ("ICTU_TEACHER", True), ("ICTU_STUDENT", True), ("ICTU", True), ("Nguyễn Văn Tảo", False),
])
def test_is_placeholder(raw, expected):
    assert rules.is_placeholder(raw, NB) is expected

@pytest.mark.parametrize("raw, indexes, quartile, venue, score, review", [
    ("Scopus Q2", ["Scopus"], "Q2", "journal_intl", None, False),
    ("KYHTGQ", [], None, "conference_natl", None, False),
    ("KYHTQT.", [], None, "conference_intl", None, False),
    ("TC 0,5 điểm", [], None, "journal_domestic", 0.5, False),
    ("0.75", [], None, None, 0.75, False),
    ("Chưa xác định", [], None, None, None, True),
    (None, [], None, None, None, True),
])
def test_map_pub_type(raw, indexes, quartile, venue, score, review):
    out = rules.map_pub_type(raw, PB)
    assert out["indexes"] == indexes
    assert out["quartile"] == quartile
    assert out["venue_kind"] == venue
    assert out["score"] == score
    assert out["needs_review"] is review

def test_norm_title():
    assert rules.norm_title("  Xây dựng  Website bán hàng! ") == "xay dung website ban hang"

def test_seed_and_load(conn):
    ids = rules.seed_rules(conn, None)
    assert set(ids) == {"name_norm", "pub_type_map", "dedup", "field_map", "year_rule"}
    assert rules.seed_rules(conn, None) == ids
    active = rules.load_active(conn)
    assert active["name_norm"][0] == ids["name_norm"]
    assert "prefixes" in active["name_norm"][1]
