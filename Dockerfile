# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
#
# Ảnh một container: tầng 1 xuất tĩnh giao diện Next.js, tầng 2 Python phục vụ
# API FastAPI và bản xuất đó tại "/". Cùng một ảnh dùng cho mọi lệnh CLI.

FROM node:24-alpine AS ui
WORKDIR /ui
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend ./
RUN npm run build

FROM python:3.12-slim
ARG EXTRAS=""
LABEL org.opencontainers.image.title="ICTU-CRIS" \
      org.opencontainers.image.source="https://github.com/maiychrus25/ICTU-CRIS" \
      org.opencontainers.image.licenses="Apache-2.0"
WORKDIR /app
COPY pyproject.toml LICENSE NOTICE README.md ./
COPY cris ./cris
# EXTRAS="[ai]" cài thêm onnxruntime/tokenizers/numpy; mặc định chỉ web + psycopg
RUN pip install --no-cache-dir ".${EXTRAS}"
COPY --from=ui /ui/out ./frontend/out
RUN useradd --system --create-home --uid 10001 cris && mkdir -p /models && chown cris /models
USER cris
ENV CRIS_AI_MODEL_DIR=/models
EXPOSE 8000
ENTRYPOINT ["python", "-m", "cris"]
CMD ["serve", "--host", "0.0.0.0"]
