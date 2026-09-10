# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""API JSON (FastAPI) — lớp mỏng gọi vào tầng nghiệp vụ `cris/*.py` và `cris/ai/*`.

Không chứa quy tắc nghiệp vụ: mọi quyết định đi qua `link.decide_link` /
`dedup.decide_group` với `actor_id` thật; AI chỉ gợi ý. Giao diện Next.js ở
`frontend/` gọi các endpoint `/api/*`; bản xuất tĩnh của nó được phục vụ ở `/`.
"""
