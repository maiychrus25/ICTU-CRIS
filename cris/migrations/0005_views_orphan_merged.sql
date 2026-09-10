-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0
DROP VIEW v_data_quality;
DROP VIEW v_person_publications;
DROP VIEW v_work_unit;

CREATE VIEW v_work_unit AS
  SELECT DISTINCT m.work_id, p.unit_id
  FROM author_link l
  JOIN author_mention m ON m.id = l.mention_id
  JOIN person p ON p.id = l.person_id
  WHERE l.state IN ('DaNoiTuDong','DaXacNhan') AND p.unit_id IS NOT NULL AND m.position > 0;

CREATE VIEW v_person_publications AS
  SELECT l.person_id, m.work_id, l.state, l.confidence
  FROM author_link l
  JOIN author_mention m ON m.id = l.mention_id
  JOIN work w ON w.id = m.work_id AND w.merged_into_id IS NULL
  WHERE l.state <> 'DaBacBo' AND m.position > 0;

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
