-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Đăng nhập cục bộ (NFR-01, lát cắt G/G2): mật khẩu băm PBKDF2-HMAC-SHA256 lưu
-- trong app_user (cris/auth.py chỉ dùng hashlib/secrets/hmac chuẩn, không thêm
-- dependency). Chưa ai có password_hash = "chế độ mở": API không bắt buộc đăng
-- nhập, hành vi cũ (header X-CRIS-User / rd_officer mặc định) giữ nguyên.
ALTER TABLE app_user ADD COLUMN password_hash text;

CREATE TABLE session (
  id            text PRIMARY KEY,               -- token ngẫu nhiên 32 byte urlsafe
  user_id       bigint NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
  created_at    timestamptz NOT NULL DEFAULT now(),
  expires_at    timestamptz NOT NULL,
  last_seen_at  timestamptz NOT NULL DEFAULT now(),
  user_agent    text
);

CREATE INDEX session_user_id ON session(user_id);   -- "session_user" là từ khoá dành riêng của PostgreSQL
CREATE INDEX session_expires ON session(expires_at);
