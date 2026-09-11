-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Minh chứng dạng tệp thật (lát cắt I2, xem docs/superpowers/plans/2026-09-11-lat-cat-i.md
-- mục I2): với evidence.kind='file', lưu đường dẫn trên đĩa, kích thước, băm
-- SHA-256 và loại nội dung nhận diện qua chữ ký byte (cris.declare.sniff_content_type,
-- không tin phần mở rộng tên tệp gửi lên) cùng tên tệp gốc.
ALTER TABLE evidence
  ADD COLUMN storage_path text,
  ADD COLUMN size_bytes int,
  ADD COLUMN sha256 text,
  ADD COLUMN content_type text,
  ADD COLUMN original_name text;
