-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Lát cắt J1: ai_query trước đây chỉ ghi lượt đối chiếu đề tài (compare_topic).
-- Thêm 'kind' để cùng bảng còn lưu được lượt tìm chuyên gia ('experts') mà
-- không phải tạo bảng riêng — cùng hình dạng input/results/provider/created_by.
ALTER TABLE ai_query ADD COLUMN kind text NOT NULL DEFAULT 'compare';

CREATE INDEX ai_query_kind_created ON ai_query(kind, created_at);
