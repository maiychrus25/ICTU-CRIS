CREATE TABLE app_user (
  id bigserial PRIMARY KEY,
  email text NOT NULL UNIQUE,
  display_name text NOT NULL,
  roles text[] NOT NULL DEFAULT '{}',
  unit_id bigint,
  person_id bigint,
  active boolean NOT NULL DEFAULT true
);

CREATE TABLE unit (
  id bigserial PRIMARY KEY,
  code text NOT NULL UNIQUE,
  name text NOT NULL,
  aliases text[] NOT NULL DEFAULT '{}',
  parent_id bigint REFERENCES unit(id),
  active boolean NOT NULL DEFAULT true
);
ALTER TABLE app_user ADD FOREIGN KEY (unit_id) REFERENCES unit(id);

CREATE TABLE catalog (
  id bigserial PRIMARY KEY,
  kind text NOT NULL,
  code text NOT NULL,
  label text NOT NULL,
  parent_code text,
  valid_from date,
  valid_to date,
  draft boolean NOT NULL DEFAULT true,
  extra jsonb,
  UNIQUE (kind, code)
);

CREATE TABLE rule_set (
  id bigserial PRIMARY KEY,
  kind text NOT NULL CHECK (kind IN ('name_norm','pub_type_map','dedup','year_rule','field_map')),
  version int NOT NULL,
  body jsonb NOT NULL,
  active boolean NOT NULL DEFAULT false,
  created_by bigint REFERENCES app_user(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (kind, version)
);
CREATE UNIQUE INDEX rule_set_one_active ON rule_set(kind) WHERE active;

CREATE TABLE sync_run (
  id bigserial PRIMARY KEY,
  source text NOT NULL CHECK (source IN ('repository','excel_faculty','sheet_registration','manual')),
  scope text NOT NULL,
  started_at timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz,
  expected_count jsonb,
  fetched_count jsonb,
  added int NOT NULL DEFAULT 0,
  changed int NOT NULL DEFAULT 0,
  vanished int NOT NULL DEFAULT 0,
  errors jsonb NOT NULL DEFAULT '[]',
  warnings jsonb NOT NULL DEFAULT '[]',
  status text NOT NULL DEFAULT 'running' CHECK (status IN ('running','ok','warning','failed')),
  triggered_by bigint REFERENCES app_user(id)
);

CREATE TABLE source_record (
  id bigserial PRIMARY KEY,
  sync_run_id bigint NOT NULL REFERENCES sync_run(id),
  source text NOT NULL,
  source_key text NOT NULL,
  doc_type text NOT NULL CHECK (doc_type IN ('bai_bao','do_an','luan_van','luan_an','giang_vien','hoc_lieu','dang_ky_do_an')),
  version int NOT NULL DEFAULT 1,
  content_hash text NOT NULL,
  raw jsonb NOT NULL,
  first_seen_at timestamptz NOT NULL DEFAULT now(),
  last_seen_at timestamptz NOT NULL DEFAULT now(),
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','vanished')),
  UNIQUE (source, source_key, content_hash)
);
CREATE INDEX source_record_key ON source_record(source, source_key);

CREATE TABLE work (
  id bigserial PRIMARY KEY,
  doc_type text NOT NULL,
  primary_source_record_id bigint NOT NULL REFERENCES source_record(id),
  title text NOT NULL,
  title_norm text NOT NULL,
  doi text,
  journal text,
  volume text,
  date_doi date,
  date_online_first date,
  year_issue int,
  abstract text,
  keywords_raw text,
  pub_type_raw text,
  indexes text[] NOT NULL DEFAULT '{}',
  quartile text,
  venue_kind text,
  score numeric(3,2),
  needs_review boolean NOT NULL DEFAULT false,
  cohort text,
  direction_code text,
  lead_unit_id bigint REFERENCES unit(id),
  state text NOT NULL DEFAULT 'Tho' CHECK (state IN ('Tho','DaChuanHoa','NghiTrung','DaGop','GiuRieng','DaXacNhan')),
  merged_into_id bigint REFERENCES work(id),
  rule_set_id bigint REFERENCES rule_set(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CHECK ((state = 'DaGop') = (merged_into_id IS NOT NULL))
);
CREATE UNIQUE INDEX work_primary_source ON work(primary_source_record_id);
CREATE UNIQUE INDEX work_doi_live ON work(doi) WHERE doi IS NOT NULL AND merged_into_id IS NULL;
CREATE INDEX work_title_norm ON work(title_norm);
CREATE INDEX work_type_year ON work(doc_type, year_issue);

CREATE TABLE field_provenance (
  id bigserial PRIMARY KEY,
  work_id bigint NOT NULL REFERENCES work(id),
  field text NOT NULL,
  raw_value text,
  value text NOT NULL,
  source_record_id bigint REFERENCES source_record(id),
  set_kind text NOT NULL CHECK (set_kind IN ('sync','normalize','merge','manual')),
  set_by bigint REFERENCES app_user(id),
  set_at timestamptz NOT NULL DEFAULT now(),
  CHECK (set_kind NOT IN ('merge','manual') OR set_by IS NOT NULL)
);
CREATE INDEX field_provenance_lookup ON field_provenance(work_id, field, set_at DESC);

CREATE TABLE author_mention (
  id bigserial PRIMARY KEY,
  work_id bigint NOT NULL REFERENCES work(id),
  role text NOT NULL CHECK (role IN ('author','mentor','student')),
  position int NOT NULL,
  raw_name text NOT NULL,
  name_norm text NOT NULL,
  name_key text NOT NULL,
  degree_raw text,
  is_placeholder boolean NOT NULL DEFAULT false,
  is_truncated boolean NOT NULL DEFAULT false,
  UNIQUE (work_id, role, position)
);
CREATE INDEX author_mention_key ON author_mention(name_key);

CREATE TABLE person (
  id bigserial PRIMARY KEY,
  kind text NOT NULL CHECK (kind IN ('lecturer','student','external')),
  source_record_id bigint REFERENCES source_record(id),
  display_name text NOT NULL,
  name_norm text NOT NULL,
  name_keys text[] NOT NULL DEFAULT '{}',
  email text UNIQUE,
  orcid text UNIQUE CHECK (orcid ~ '^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$'),
  orcid_verified boolean NOT NULL DEFAULT false,
  scholar_url text,
  unit_id bigint REFERENCES unit(id),
  degree_raw text,
  student_code text,
  class_code text,
  phone text,
  dob date,
  active boolean NOT NULL DEFAULT true
);
CREATE INDEX person_name_keys ON person USING gin(name_keys);
ALTER TABLE app_user ADD FOREIGN KEY (person_id) REFERENCES person(id);

CREATE TABLE author_link (
  id bigserial PRIMARY KEY,
  mention_id bigint NOT NULL REFERENCES author_mention(id),
  person_id bigint NOT NULL REFERENCES person(id),
  confidence text NOT NULL CHECK (confidence IN ('orcid','ten_day_du_duy_nhat','ten_day_du_nhieu_ung_vien','ten_mot_phan')),
  basis jsonb,
  state text NOT NULL CHECK (state IN ('DaNoiTuDong','ChoXacNhan','DaXacNhan','DaBacBo')),
  degree_conflict boolean NOT NULL DEFAULT false,
  decided_by bigint REFERENCES app_user(id),
  decided_at timestamptz,
  reason text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (mention_id, person_id),
  CHECK (state <> 'DaBacBo' OR reason IS NOT NULL)
);
CREATE UNIQUE INDEX author_link_one_live ON author_link(mention_id) WHERE state IN ('DaNoiTuDong','DaXacNhan');

CREATE TABLE duplicate_group (
  id bigserial PRIMARY KEY,
  doc_type text NOT NULL,
  basis text NOT NULL CHECK (basis IN ('doi','title_norm','title_student_cohort')),
  hint text,
  state text NOT NULL DEFAULT 'NghiTrung' CHECK (state IN ('NghiTrung','DaGop','GiuRieng','BoQua')),
  survivor_work_id bigint REFERENCES work(id),
  decided_by bigint REFERENCES app_user(id),
  decided_at timestamptz,
  reason text,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (state <> 'GiuRieng' OR reason IS NOT NULL),
  CHECK (state <> 'DaGop' OR survivor_work_id IS NOT NULL)
);

CREATE TABLE duplicate_member (
  group_id bigint NOT NULL REFERENCES duplicate_group(id),
  work_id bigint NOT NULL REFERENCES work(id),
  diff jsonb,
  PRIMARY KEY (group_id, work_id)
);

CREATE TABLE audit_log (
  id bigserial PRIMARY KEY,
  at timestamptz NOT NULL DEFAULT now(),
  actor_id bigint REFERENCES app_user(id),
  action text NOT NULL,
  entity text NOT NULL,
  entity_id bigint NOT NULL,
  before jsonb,
  after jsonb,
  sync_run_id bigint REFERENCES sync_run(id)
);

CREATE FUNCTION audit_log_immutable() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'audit_log là bảng chỉ thêm'; END $$;
CREATE TRIGGER audit_log_no_update BEFORE UPDATE OR DELETE ON audit_log
  FOR EACH ROW EXECUTE FUNCTION audit_log_immutable();

CREATE VIEW v_work_unit AS
  SELECT DISTINCT m.work_id, p.unit_id
  FROM author_link l
  JOIN author_mention m ON m.id = l.mention_id
  JOIN person p ON p.id = l.person_id
  WHERE l.state IN ('DaNoiTuDong','DaXacNhan') AND p.unit_id IS NOT NULL;

CREATE VIEW v_person_publications AS
  SELECT l.person_id, m.work_id, l.state, l.confidence
  FROM author_link l JOIN author_mention m ON m.id = l.mention_id
  WHERE l.state <> 'DaBacBo';
