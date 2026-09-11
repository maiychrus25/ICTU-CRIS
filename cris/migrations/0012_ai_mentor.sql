-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Gợi ý người hướng dẫn cho đồ án ICTU_TEACHER (lát cắt I3, xem
-- docs/superpowers/plans/2026-09-11-lat-cat-i.md mục I3): thêm loại gợi ý
-- 'mentor' vào ai_suggestion — vẫn chỉ là bảng GỢI Ý, không đổi work/author_link.
ALTER TABLE ai_suggestion DROP CONSTRAINT IF EXISTS ai_suggestion_kind_check;
ALTER TABLE ai_suggestion
  ADD CONSTRAINT ai_suggestion_kind_check CHECK (kind IN ('author_link', 'duplicate', 'topic_overlap', 'mentor'));

-- Ứng viên do AI đề xuất, chuyên viên đưa vào hàng đợi xác nhận
-- (cris.link.add_candidate) mang confidence riêng để phân biệt với các nguồn
-- ứng viên do cris.link.candidates() sinh ra (so tên) — quyết định cuối vẫn ở
-- hàng đợi tác giả (BR-18), không tự xác nhận.
ALTER TABLE author_link DROP CONSTRAINT IF EXISTS author_link_confidence_check;
ALTER TABLE author_link
  ADD CONSTRAINT author_link_confidence_check
  CHECK (confidence IN ('orcid', 'ten_day_du_duy_nhat', 'ten_day_du_nhieu_ung_vien', 'ten_mot_phan', 'ai_mentor'));
