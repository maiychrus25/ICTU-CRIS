# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Ứng dụng FastAPI: router `/api/*`, tài liệu OpenAPI ở `/docs`, và bản xuất tĩnh của
giao diện Next.js (`frontend/out`) phục vụ ở `/` khi có."""
import contextlib
import importlib.metadata
import logging
import os
import pathlib
import threading
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware

from cris import db
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
    units,
)

FRONTEND_OUT = pathlib.Path(__file__).resolve().parents[2] / "frontend" / "out"

logger = logging.getLogger("cris.api")

# Trạng thái nạp mô hình AI cục bộ (`CRIS_AI_PROVIDER=local`) — cập nhật bởi
# luồng nền khởi động ở `_lifespan`; `_model_status` đọc biến này cho `local`,
# còn `none`/`fake`/khác được tính thẳng từ biến môi trường mỗi lần gọi (không
# cần luồng nền: `none` không nạp gì, `fake` không tải mô hình nặng).
_LOCAL_MODEL_STATE = "loading"


def _warm_up_local_provider():
    """Nạp provider `local` ở luồng nền (ONNX ~1,8 s) để request đầu không phải
    chờ; bắt mọi ngoại lệ — health sẽ báo `missing` thay vì làm sập tiến trình."""
    global _LOCAL_MODEL_STATE
    try:
        from cris.ai.provider import get_provider
        get_provider()
        _LOCAL_MODEL_STATE = "loaded"
        logger.info("AI provider sẵn sàng: local")
    except Exception as exc:  # noqa: BLE001 - health báo "missing", không chặn khởi động
        _LOCAL_MODEL_STATE = "missing"
        logger.info("AI provider không nạp được: %s", exc)


@contextlib.asynccontextmanager
async def _lifespan(app: FastAPI):
    if (os.environ.get("CRIS_AI_PROVIDER") or "none").strip().lower() == "local":
        threading.Thread(target=_warm_up_local_provider, daemon=True).start()
    yield


def _model_status() -> str:
    name = (os.environ.get("CRIS_AI_PROVIDER") or "none").strip().lower()
    if name == "none":
        return "disabled"
    if name == "local":
        return _LOCAL_MODEL_STATE
    # fake (kiểm thử) hoặc tên khác `get_provider` chấp nhận: không tải mô hình
    # nặng, nạp thẳng để biết ngay "loaded"/"missing" (vd thiếu thư viện).
    try:
        from cris.ai.provider import get_provider
        get_provider()
        return "loaded"
    except Exception:
        return "missing"


def _app_version(app: FastAPI) -> str:
    try:
        return importlib.metadata.version("ictu-cris")
    except importlib.metadata.PackageNotFoundError:
        return app.version


def _last_sync_age_h(conn) -> float | None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT finished_at FROM sync_run WHERE finished_at IS NOT NULL "
            "ORDER BY finished_at DESC LIMIT 1")
        row = cur.fetchone()
    if row is None:
        return None
    delta = datetime.now(UTC) - row["finished_at"]
    return round(delta.total_seconds() / 3600, 1)


def create_app(static_dir: str | os.PathLike | None = None) -> FastAPI:
    app = FastAPI(
        title="ICTU-CRIS API",
        version="0.6.0",
        description="Một nguồn sự thật cho dữ liệu công bố khoa học — mỗi con số truy ngược được về bản ghi gốc. "
                    "AI gợi ý, người quyết; không có AI vẫn chạy đủ chức năng.",
        license_info={"name": "Apache-2.0", "url": "https://www.apache.org/licenses/LICENSE-2.0"},
        lifespan=_lifespan,
    )
    # Dev: Next.js chạy ở cổng 3000 gọi API ở 8000. Sản xuất: cùng gốc, không cần CORS.
    origins = [o for o in (os.environ.get("CRIS_CORS_ORIGINS") or "http://localhost:3000,http://127.0.0.1:3000").split(",") if o]
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])
    # Bản đồ tri thức/tra cứu có thể tới ~1,5 MB JSON — nén xuống còn ~300 KB.
    app.add_middleware(GZipMiddleware, minimum_size=1024)
    for r in (search.router, queue.router, compare.router, quality.router,
              stats.router, export.router, audit.router, periods.router, screen.router,
              persons.router, sync.router, auth.router, declarations.router, me.router,
              mentors.router, ai_public.router, ai_map.router,
              cite.router, recent.router, feed.router, anomalies.router, reports.router,
              notifications.router, units.router):
        app.include_router(r)

    @app.get("/api/health", tags=["he-thong"])
    def health():
        """`status`/`db`: "ok" hoặc lỗi (503 nếu không kết nối/truy vấn được
        CSDL); `model`: trạng thái provider AI (`loaded|missing|disabled|loading`);
        `last_sync_age_h`: giờ từ lần đồng bộ gần nhất, `null` nếu chưa có;
        `version`: phiên bản đang chạy."""
        try:
            conn = db.connect()
        except Exception:
            return JSONResponse(status_code=503, content={"status": "error", "db": "error"})
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            last_sync_age_h = _last_sync_age_h(conn)
        except Exception:
            return JSONResponse(status_code=503, content={"status": "error", "db": "error"})
        finally:
            conn.close()
        return {
            "status": "ok",
            "db": "ok",
            "model": _model_status(),
            "last_sync_age_h": last_sync_age_h,
            "version": _app_version(app),
        }

    static = pathlib.Path(static_dir) if static_dir else FRONTEND_OUT
    if static.is_dir():
        app.mount("/", StaticFiles(directory=str(static), html=True), name="ui")
    return app


app = create_app()
