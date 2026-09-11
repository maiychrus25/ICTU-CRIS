-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Lát cắt K2: cảnh báo bất thường dữ liệu. `quality_flag` được ghi/đóng bởi quét
-- định kỳ (`python -m cris quality scan`, cris/anomaly.py) — không có luồng nào
-- khác ghi vào bảng này ngoài `dismiss` (người quyết bỏ qua kèm lý do bắt buộc).
-- UNIQUE thường của PostgreSQL coi NULL là phân biệt (không chặn trùng) nên
-- dùng COALESCE trên work_id/person_id để một cặp (kind, work_id, person_id)
-- — kể cả khi một trong hai cột là NULL — chỉ có một cờ đang mở.
CREATE TABLE quality_flag (
  id bigserial PRIMARY KEY,
  kind text NOT NULL,
  work_id bigint REFERENCES work(id),
  person_id bigint REFERENCES person(id),
  detail jsonb NOT NULL DEFAULT '{}',
  severity text NOT NULL CHECK (severity IN ('cao','vua','thap')),
  state text NOT NULL DEFAULT 'open' CHECK (state IN ('open','dismissed','resolved')),
  dismissed_by bigint REFERENCES app_user(id),
  reason text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX quality_flag_unique ON quality_flag (kind, COALESCE(work_id, 0), COALESCE(person_id, 0));
CREATE INDEX quality_flag_state ON quality_flag(kind, state);
