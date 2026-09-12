-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Lát cắt L1: bản báo cáo kỳ đóng băng, có phiên bản (BA điểm "P" — phiên bản
-- báo cáo được đóng băng sau khi chốt). `payload` lưu toàn bộ danh sách hồ sơ +
-- công trình + tác giả + minh chứng TẠI THỜI ĐIỂM SINH (cris/report.py,
-- build_report) — không đổi về sau dù declaration/work/author_link có đổi
-- tiếp; `summary` là bản tóm tắt theo đơn vị/loại/tổng, tách riêng để liệt kê
-- (GET .../reports) không phải tải cả payload đầy đủ. `sha256` băm JSON
-- canonical của payload, chứng minh không bị sửa sau khi sinh.
-- UNIQUE(period_id, version): version tăng dần theo từng kỳ (build_report tính
-- max+1), một kỳ có thể có nhiều phiên bản báo cáo qua thời gian.
CREATE TABLE period_report (
  id bigserial PRIMARY KEY,
  period_id bigint NOT NULL REFERENCES period(id),
  version int NOT NULL,
  generated_at timestamptz NOT NULL DEFAULT now(),
  generated_by bigint REFERENCES app_user(id),
  note text,
  summary jsonb NOT NULL,
  payload jsonb NOT NULL,
  sha256 text NOT NULL,
  UNIQUE (period_id, version)
);
CREATE INDEX period_report_period ON period_report(period_id, version DESC);
