-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Lát cắt L2: thông báo trong ứng dụng (BA điểm "H" — người dùng biết hồ sơ
-- của mình đổi trạng thái). `notification` là bảng phẳng, không liên kết cứng
-- tới thực thể sinh ra nó (declaration/period/author_link) — `link` đã là một
-- URL tương đối trỏ thẳng tới màn hình liên quan (`cris/notify.py` sinh ra),
-- đủ để giao diện điều hướng mà không cần join ngược. `kind` phân loại để lọc/
-- gắn icon phía giao diện (`declaration_state`, `period_state`, `link_confirmed`).
CREATE TABLE notification (
  id bigserial PRIMARY KEY,
  user_id bigint NOT NULL REFERENCES app_user(id),
  kind text NOT NULL,
  title text NOT NULL,
  body text NOT NULL DEFAULT '',
  link text,
  created_at timestamptz NOT NULL DEFAULT now(),
  read_at timestamptz
);
-- Truy vấn chính: đếm/liệt kê chưa đọc của một người, mới nhất trước.
CREATE INDEX notification_user_read ON notification(user_id, read_at);
CREATE INDEX notification_user_created ON notification(user_id, created_at DESC);
