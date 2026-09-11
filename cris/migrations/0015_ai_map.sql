-- Copyright (c) 2026 ICTU-CRIS contributors
-- SPDX-License-Identifier: Apache-2.0

-- Lát cắt J2: bản đồ tri thức 2 chiều (PCA trên vector ngữ nghĩa) — bảng cache,
-- tính bởi `python -m cris ai map` (cris/ai/map.py). Giữ đúng 1 dòng mới nhất
-- mỗi `model` (map.py xoá dòng cũ của model đó trước khi ghi dòng mới, cùng cách
-- `ai_topic` được xây lại trong topics.py) — không có UNIQUE(model) vì `id` vẫn
-- cần tăng dần để "mới nhất" (`built_at`) không mơ hồ khi có nhiều model.
CREATE TABLE ai_map (
  id        bigserial PRIMARY KEY,
  model     text NOT NULL,
  built_at  timestamptz NOT NULL DEFAULT now(),
  method    text NOT NULL DEFAULT 'pca',
  points    jsonb NOT NULL,
  topics    jsonb NOT NULL
);

CREATE INDEX ai_map_model ON ai_map(model);
