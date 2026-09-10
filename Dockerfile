# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
FROM python:3.12-slim
ARG EXTRAS=""
LABEL org.opencontainers.image.title="ICTU-CRIS" \
      org.opencontainers.image.source="https://github.com/maiychrus25/CRIS" \
      org.opencontainers.image.licenses="Apache-2.0"
WORKDIR /app
COPY pyproject.toml LICENSE NOTICE README.md ./
COPY cris ./cris
# EXTRAS="[ai]" cài thêm onnxruntime/tokenizers/numpy; mặc định chỉ psycopg
RUN pip install --no-cache-dir ".${EXTRAS}"
RUN useradd --system --create-home --uid 10001 cris && mkdir -p /models && chown cris /models
USER cris
ENV CRIS_AI_MODEL_DIR=/models
EXPOSE 8000
ENTRYPOINT ["python", "-m", "cris"]
CMD ["quality"]
