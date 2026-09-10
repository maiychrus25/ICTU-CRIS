-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0
CREATE TABLE period (
  id bigserial PRIMARY KEY,
  code text NOT NULL UNIQUE,
  name text NOT NULL,
  scope jsonb NOT NULL,
  criteria text,
  rule_set_id bigint REFERENCES rule_set(id),
  opens_at timestamptz,
  due_at timestamptz NOT NULL,
  state text NOT NULL DEFAULT 'ChuanBi' CHECK (state IN ('ChuanBi','DangMo','DaDongNop','Huy')),
  created_by bigint REFERENCES app_user(id),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE declaration (
  id bigserial PRIMARY KEY,
  period_id bigint NOT NULL REFERENCES period(id),
  work_id bigint NOT NULL REFERENCES work(id),
  unit_id bigint NOT NULL REFERENCES unit(id),
  state text NOT NULL DEFAULT 'Nhap' CHECK (state IN ('Nhap','ChoBoSung','Rut')),
  note text,
  created_by bigint REFERENCES app_user(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (period_id, work_id, unit_id)
);
CREATE INDEX declaration_period_unit ON declaration(period_id, unit_id);
CREATE INDEX declaration_work ON declaration(work_id);

CREATE TABLE evidence (
  id bigserial PRIMARY KEY,
  declaration_id bigint NOT NULL REFERENCES declaration(id) ON DELETE CASCADE,
  kind text NOT NULL,
  url text,
  file_name text,
  note text,
  added_by bigint REFERENCES app_user(id),
  added_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX evidence_declaration ON evidence(declaration_id);

CREATE TABLE declaration_event (
  id bigserial PRIMARY KEY,
  declaration_id bigint NOT NULL REFERENCES declaration(id) ON DELETE CASCADE,
  from_state text,
  to_state text NOT NULL,
  actor_id bigint REFERENCES app_user(id),
  reason text,
  at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX declaration_event_declaration ON declaration_event(declaration_id, at);
