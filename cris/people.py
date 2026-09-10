import hashlib
import re
from datetime import datetime
import psycopg
from cris import rules as RU
from cris.db import tx

def ensure_unit(conn, name):
    name = (name or "").strip()
    if not name:
        return None
    with conn.cursor() as cur:
        cur.execute("""SELECT id FROM unit WHERE name=%s OR code=%s OR %s = ANY(aliases)
                       ORDER BY (name = %s) DESC, (code = %s) DESC LIMIT 1""",
                    (name, name, name, name, name))
        row = cur.fetchone()
        if row:
            return row["id"]
        code = re.sub(r"[^A-Z0-9]", "", RU.strip_accents(name).upper())[:16] or "UNIT"
        cur.execute("SELECT 1 FROM unit WHERE code=%s", (code,))
        if cur.fetchone():
            code = code[:12] + hashlib.sha1(name.encode("utf-8")).hexdigest()[:4].upper()
        cur.execute("INSERT INTO unit(code, name) VALUES (%s,%s) RETURNING id", (code, name))
        return cur.fetchone()["id"]

def _dob(s):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime((s or "").strip(), fmt).date()
        except ValueError:
            pass
    return None

def import_people(conn):
    rules = RU.load_active(conn)
    nb = rules["name_norm"][1]
    out = {"created": 0, "updated": 0, "errors": []}
    with tx(conn), conn.cursor() as cur:
        cur.execute("""SELECT s.* FROM source_record s WHERE s.doc_type='giang_vien' AND s.status='active'
                       AND s.version=(SELECT max(version) FROM source_record x WHERE x.source=s.source AND x.source_key=s.source_key)""")
        for rec in cur.fetchall():
            try:
                with conn.transaction():
                    a = rec["raw"]["archive"]
                    raw_name = a.get("name") or a.get("display") or ""
                    nn, deg = RU.norm_name(raw_name, nb)
                    display = re.sub(r"\s+", " ", raw_name).strip()
                    for canon, variants in nb["prefixes"].items():
                        matched = next((v for v in variants if display.lower().startswith(v + " ")), None)
                        if matched:
                            display = display[len(matched):].strip()
                            break
                    unit_id = ensure_unit(conn, a.get("jobTitle"))
                    vals = dict(display_name=display, name_norm=nn, degree_raw=a.get("degree") or deg,
                                email=a.get("email"), orcid=a.get("orcid"), unit_id=unit_id,
                                phone=a.get("phone"), dob=_dob(a.get("dob")))
                    cur.execute("SELECT id, name_keys FROM person WHERE source_record_id IN (SELECT id FROM source_record WHERE source=%s AND source_key=%s)",
                                (rec["source"], rec["source_key"]))
                    row = cur.fetchone()
                    key = RU.name_key(nn)
                    if row:
                        keys = sorted(set(row["name_keys"]) | {key})
                        cur.execute("""UPDATE person SET display_name=%s, name_norm=%s, degree_raw=%s, email=%s, orcid=%s, unit_id=%s,
                                       phone=%s, dob=%s, name_keys=%s, source_record_id=%s WHERE id=%s""",
                                    (*vals.values(), keys, rec["id"], row["id"]))
                        out["updated"] += 1
                    else:
                        cur.execute("""INSERT INTO person(kind, source_record_id, display_name, name_norm, degree_raw, email, orcid, unit_id, phone, dob, name_keys)
                                       VALUES ('lecturer',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (rec["id"], *vals.values(), [key]))
                        out["created"] += 1
            except psycopg.errors.IntegrityError as e:
                out["errors"].append({"source_key": rec["source_key"], "error": str(e).splitlines()[0]})
    return out
