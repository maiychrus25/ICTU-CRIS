-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Lát cắt N: hồ sơ giảng viên còn thiếu thông tin đã có sẵn ở kho nguồn — ảnh
-- đại diện (`archive.avatar`) và lĩnh vực (`archive.knowsAbout`). Giới tính,
-- ngày sinh, điện thoại vẫn không đưa ra API/giao diện (dữ liệu cá nhân).
ALTER TABLE person ADD COLUMN avatar_url text;
ALTER TABLE person ADD COLUMN field text;
