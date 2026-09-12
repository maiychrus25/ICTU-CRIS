# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Ứng dụng FastAPI: router `/api/*`, tài liệu OpenAPI ở `/docs`, và bản xuất tĩnh của
giao diện Next.js (`frontend/out`) phục vụ ở `/` khi có."""
import os
import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from cris.api.routes import (
    ai_map,
    ai_public,
    anomalies,
    audit,
    auth,
    cite,
    compare,
    declarations,
    export,
    feed,
    me,
    mentors,
    notifications,
    periods,
    persons,
    quality,
    queue,
    recent,
    reports,
    screen,
    search,
    stats,
    sync,
)

FRONTEND_OUT = pathlib.Path(__file__).resolve().parents[2] / "frontend" / "out"


def create_app(static_dir: str | os.PathLike | None = None) -> FastAPI:
    app = FastAPI(
        title="ICTU-CRIS API",
        version="0.6.0",
        description="Một nguồn sự thật cho dữ liệu công bố khoa học — mỗi con số truy ngược được về bản ghi gốc. "
                    "AI gợi ý, người quyết; không có AI vẫn chạy đủ chức năng.",
        license_info={"name": "Apache-2.0", "url": "https://www.apache.org/licenses/LICENSE-2.0"},
    )
    # Dev: Next.js chạy ở cổng 3000 gọi API ở 8000. Sản xuất: cùng gốc, không cần CORS.
    origins = [o for o in (os.environ.get("CRIS_CORS_ORIGINS") or "http://localhost:3000,http://127.0.0.1:3000").split(",") if o]
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])
    for r in (search.router, queue.router, compare.router, quality.router,
              stats.router, export.router, audit.router, periods.router, screen.router,
              persons.router, sync.router, auth.router, declarations.router, me.router,
              mentors.router, ai_public.router, ai_map.router,
              cite.router, recent.router, feed.router, anomalies.router, reports.router,
              notifications.router):
        app.include_router(r)

    @app.get("/api/health", tags=["he-thong"])
    def health():
        return {"status": "ok"}

    static = pathlib.Path(static_dir) if static_dir else FRONTEND_OUT
    if static.is_dir():
        app.mount("/", StaticFiles(directory=str(static), html=True), name="ui")
    return app


app = create_app()
