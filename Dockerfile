# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml LICENSE NOTICE ./
COPY cris ./cris
RUN pip install --no-cache-dir .
ENTRYPOINT ["python", "-m", "cris"]
CMD ["quality"]
