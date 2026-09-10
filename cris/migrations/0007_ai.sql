-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Lát cắt AI. Mọi bảng ở đây là bảng GỢI Ý: mã trong cris/ai/ chỉ ghi vào chúng,
-- không bao giờ ghi vào work, author_link, duplicate_group hay field_provenance.
-- Người dùng đọc gợi ý trên giao diện và quyết định qua luồng nghiệp vụ sẵn có.

-- Vector ngữ nghĩa của một công trình theo một mô hình. Không dùng pgvector để
-- không thêm extension phải cài; 5.709 x 384 số thực nằm gọn trong RAM.
CREATE TABLE ai_embedding (
  work_id    bigint NOT NULL REFERENCES work(id) ON DELETE CASCADE,
  model      text   NOT NULL,
  dim        int    NOT NULL,
  vector     double precision[] NOT NULL,
  text_hash  text   NOT NULL,          -- SHA-256 của văn bản đã embed, để chạy lại chỉ phần đổi
  built_at   timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (work_id, model)
);

-- Cụm từ khoá (trục chủ đề) sinh từ gom cụm embedding của từ khoá.
CREATE TABLE ai_topic (
  id        bigserial PRIMARY KEY,
  model     text NOT NULL,
  label     text NOT NULL,
  size      int  NOT NULL DEFAULT 0,
  built_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE ai_topic_keyword (
  topic_id  bigint NOT NULL REFERENCES ai_topic(id) ON DELETE CASCADE,
  keyword   text   NOT NULL,
  weight    real   NOT NULL DEFAULT 1,
  PRIMARY KEY (topic_id, keyword)
);

-- Gợi ý cho hàng đợi. target_id trỏ vào author_link.id hoặc duplicate_group.id
-- tuỳ kind; không đặt khoá ngoại vì hai đích khác bảng.
CREATE TABLE ai_suggestion (
  id         bigserial PRIMARY KEY,
  kind       text   NOT NULL CHECK (kind IN ('author_link', 'duplicate')),
  target_id  bigint NOT NULL,
  payload    jsonb  NOT NULL,
  model      text   NOT NULL,
  built_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (kind, target_id, model)
);

-- Lịch sử đối chiếu đề tài, để xem lại và gửi giảng viên.
CREATE TABLE ai_query (
  id          bigserial PRIMARY KEY,
  input       jsonb NOT NULL,
  results     jsonb NOT NULL,
  provider    text  NOT NULL,
  created_by  bigint REFERENCES app_user(id),
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ai_embedding_model ON ai_embedding(model);
CREATE INDEX ai_suggestion_target ON ai_suggestion(kind, target_id);
