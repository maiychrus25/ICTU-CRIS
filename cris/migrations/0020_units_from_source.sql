-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Lát cắt M: đơn vị thật (khoa/trung tâm) đọc từ bộ lọc `dept` của kho nguồn
-- (`/bai-bao/?dept=`), tách khỏi chức vụ ("Hiệu trưởng", "Trưởng khoa"…) vốn bị
-- nhập nhầm thành đơn vị ở migration 0013. `work_unit` ghi đơn vị suy từ nguồn
-- (`source='source'`, từ `archive.depts` — xem cris/normalize.py) hoặc gán tay
-- (`source='manual'`, xem cris/units.py); đơn vị suy từ tác giả đã liên kết vẫn
-- tính trong `v_work_unit` như trước (không lưu bảng, chỉ hợp trong view).
CREATE TABLE work_unit (
  work_id bigint NOT NULL REFERENCES work(id),
  unit_id bigint NOT NULL REFERENCES unit(id),
  source text NOT NULL CHECK (source IN ('source', 'manual')),
  PRIMARY KEY (work_id, unit_id, source)
);
CREATE INDEX work_unit_unit ON work_unit(unit_id);

-- `jobTitle` ở kho nguồn là CHỨC VỤ — tách khỏi đơn vị hẳn (cris.people không
-- còn suy unit_id từ đó, xem unit_from_job_title cũ đã bỏ). `unit_source` phân
-- biệt đơn vị suy tự động theo đa số công trình (`assign_units_by_works`) với
-- đơn vị do quản trị gán tay (`cris.units.set_person_unit`) — chỉ hàng 'auto'
-- mới bị ghi đè ở lần suy tiếp theo.
ALTER TABLE person ADD COLUMN position text;
ALTER TABLE person ADD COLUMN unit_source text NOT NULL DEFAULT 'auto' CHECK (unit_source IN ('auto', 'manual'));

-- 10 khoa theo mã lọc `dept` của kho nguồn (khảo sát 09/2026, xem kế hoạch lát cắt M).
-- Tên chính thức theo ictu.edu.vn (13/09/2026): trường hiện có 5 khoa — CNTT, KT&CN,
-- KT&QT, NT&TT và Khoa Khoa học liên ngành (chưa có mã ở nguồn). Các mã còn lại là
-- khoa/bộ môn tiền thân, còn xuất hiện ở bản ghi cũ: ĐTVT/ĐTTT → KT&CN, TĐH → KT&CN,
-- HTTTKT → KT&QT (đổi tên 2011), KHCB → Khoa học liên ngành, TTĐPT → NT&TT.
INSERT INTO unit(code, name) VALUES
  ('CNTT',   'Khoa Công nghệ thông tin'),
  ('ĐTVT',   'Khoa Công nghệ điện tử và truyền thông'),
  ('ĐTTT',   'Khoa Điện tử truyền thông'),
  ('HTTTKT', 'Khoa Hệ thống thông tin kinh tế'),
  ('KHCB',   'Khoa Khoa học cơ bản'),
  ('KT&CN',  'Khoa Kỹ thuật và Công nghệ'),
  ('KT&QT',  'Khoa Kinh tế và Quản trị'),
  ('NT&TT',  'Khoa Nghệ thuật và Truyền thông'),
  ('TĐH',    'Khoa Công nghệ tự động hoá'),
  ('TTĐPT',  'Khoa Truyền thông đa phương tiện')
ON CONFLICT (code) DO NOTHING;

-- Nguồn còn ghi biến thể "HTTKT" ở một số bản ghi cũ — bí danh về HTTTKT.
UPDATE unit SET aliases = array_append(aliases, 'HTTKT')
WHERE code = 'HTTTKT' AND NOT ('HTTKT' = ANY(aliases));

-- Ban Giám hiệu (mã BGH, xem 0013) không phải khoa/trung tâm → tắt, gỡ khỏi
-- person.unit_id; chức vụ hiệu trưởng/phó hiệu trưởng suy lại từ jobTitle gốc
-- (source_record.raw->archive->jobTitle) ghi vào person.position.
UPDATE person p
SET unit_id = NULL,
    position = CASE WHEN sub.job_title ILIKE '%phó%' THEN 'Phó Hiệu trưởng' ELSE 'Hiệu trưởng' END
FROM (
  SELECT p2.id AS person_id, sr.raw -> 'archive' ->> 'jobTitle' AS job_title
  FROM person p2
  JOIN unit u ON u.id = p2.unit_id AND u.code = 'BGH'
  LEFT JOIN source_record sr ON sr.id = p2.source_record_id
) sub
WHERE p.id = sub.person_id;

UPDATE unit SET active = false WHERE code = 'BGH';

-- `v_work_unit` giờ hợp cả đơn vị suy từ nguồn/gán tay (work_unit) lẫn đơn vị
-- của tác giả đã liên kết (điều kiện cũ, không đổi) — `v_data_quality` phụ
-- thuộc view này nên phải gỡ/dựng lại theo đúng thứ tự như 0005.
DROP VIEW v_data_quality;
DROP VIEW v_work_unit;

CREATE VIEW v_work_unit AS
  SELECT wu.work_id, wu.unit_id
  FROM work_unit wu
  WHERE wu.source IN ('source', 'manual')
  UNION
  SELECT DISTINCT m.work_id, p.unit_id
  FROM author_link l
  JOIN author_mention m ON m.id = l.mention_id
  JOIN person p ON p.id = l.person_id
  WHERE l.state IN ('DaNoiTuDong','DaXacNhan') AND p.unit_id IS NOT NULL AND m.position > 0;

CREATE VIEW v_data_quality AS
  SELECT
    (SELECT count(*) FROM work WHERE merged_into_id IS NULL) AS works,
    (SELECT count(*) FROM work WHERE merged_into_id IS NULL AND needs_review) AS works_needs_review,
    (SELECT count(*) FROM author_mention) AS mentions,
    (SELECT count(*) FROM author_mention WHERE is_placeholder) AS mentions_placeholder,
    (SELECT count(*) FROM author_mention WHERE is_truncated) AS mentions_truncated,
    (SELECT count(*) FROM author_link WHERE state='DaNoiTuDong') AS links_auto,
    (SELECT count(DISTINCT mention_id) FROM author_link WHERE state='ChoXacNhan') AS links_queued,
    (SELECT count(*) FROM author_link WHERE state='DaXacNhan') AS links_confirmed,
    (SELECT count(DISTINCT m.work_id) FROM author_mention m JOIN author_link l ON l.mention_id=m.id AND l.state IN ('DaNoiTuDong','DaXacNhan') JOIN work w ON w.id=m.work_id AND w.merged_into_id IS NULL WHERE m.position > 0) AS works_with_link,
    (SELECT count(*) FROM work w WHERE w.merged_into_id IS NULL AND NOT EXISTS (SELECT 1 FROM v_work_unit u WHERE u.work_id=w.id)) AS works_without_unit,
    (SELECT count(*) FROM duplicate_group WHERE state='NghiTrung') AS dup_groups_open;
