-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Rà soát trùng đề tài theo khoá (E5): thêm loại gợi ý 'topic_overlap' vào
-- ai_suggestion — vẫn chỉ là bảng GỢI Ý, không đổi work/author_link/duplicate_group.
ALTER TABLE ai_suggestion DROP CONSTRAINT IF EXISTS ai_suggestion_kind_check;
ALTER TABLE ai_suggestion
  ADD CONSTRAINT ai_suggestion_kind_check CHECK (kind IN ('author_link', 'duplicate', 'topic_overlap'));
