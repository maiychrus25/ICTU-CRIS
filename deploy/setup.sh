#!/usr/bin/env bash
# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
#
# Cài ICTU-CRIS một lệnh trên một máy có Docker:
#   bash deploy/setup.sh            # không AI
#   bash deploy/setup.sh --ai       # cài thư viện AI vào ảnh, tải mô hình, bật provider local
# Việc đồng bộ dữ liệu từ kho nguồn (~2 giờ) KHÔNG chạy tự động — xem cuối script.
set -euo pipefail
cd "$(dirname "$0")"

AI=false; [ "${1:-}" = "--ai" ] && AI=true
for c in docker; do command -v "$c" >/dev/null || { echo "❌ cần cài $c"; exit 1; }; done
docker compose version >/dev/null 2>&1 || { echo "❌ cần Docker Compose v2 (docker compose)"; exit 1; }

# 1. .env
if [ ! -f .env ]; then
  cp .env.example .env
  pw=$(openssl rand -hex 12 2>/dev/null || head -c 24 /dev/urandom | base64 | tr -d '/+=' | head -c 24)
  sed -i.bak "s|POSTGRES_PASSWORD=CHANGE_ME|POSTGRES_PASSWORD=$pw|" .env && rm -f .env.bak
  echo "📄 đã tạo deploy/.env (mật khẩu DB ngẫu nhiên)"
fi
if $AI; then
  sed -i.bak 's|^CRIS_AI_PROVIDER=.*|CRIS_AI_PROVIDER=local|; s|^CRIS_EXTRAS=.*|CRIS_EXTRAS=[ai]|' .env && rm -f .env.bak
  echo "🤖 bật AI: CRIS_AI_PROVIDER=local, CRIS_EXTRAS=[ai]"
fi
set -a; . ./.env; set +a

# 2. dựng và khởi động DB
docker compose build app
docker compose up -d db
echo -n "⏳ chờ PostgreSQL"; for i in $(seq 1 40); do docker compose exec -T db pg_isready -U "$POSTGRES_USER" >/dev/null 2>&1 && break; echo -n .; sleep 2; done; echo

# 3. lược đồ, quy tắc, người dùng mặc định
docker compose run --rm app migrate
docker compose run --rm app seed
docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -c \
  "INSERT INTO app_user(email, display_name, roles) VALUES ('${CRIS_ADMIN_EMAIL}', '${CRIS_ADMIN_NAME}', ARRAY['rd_officer']) ON CONFLICT (email) DO NOTHING;"
echo "👤 người dùng mặc định: ${CRIS_ADMIN_EMAIL} (rd_officer)"

# Đăng nhập cục bộ (NFR-01, tuỳ chọn): đặt CRIS_ADMIN_PASSWORD trong deploy/.env
# TRƯỚC khi chạy script để bật bắt buộc đăng nhập ngay từ lúc cài. Để trống thì
# hệ thống chạy "chế độ mở" (không bắt buộc đăng nhập) như bản trước.
if [ -n "${CRIS_ADMIN_PASSWORD:-}" ]; then
  docker compose run --rm -e CRIS_PASSWORD="${CRIS_ADMIN_PASSWORD}" app user set-password "${CRIS_ADMIN_EMAIL}"
  echo "🔒 đã đặt mật khẩu cho ${CRIS_ADMIN_EMAIL} — đăng nhập bắt buộc từ giờ"
else
  echo "🔓 CRIS_ADMIN_PASSWORD trống — chế độ mở (chưa bắt buộc đăng nhập); đặt sau bằng:"
  echo "    docker compose run --rm app user set-password ${CRIS_ADMIN_EMAIL}"
fi

# 4. AI (tuỳ chọn): tải mô hình vào volume cris_models
if $AI; then docker compose run --rm app ai download; fi

# 5. web
docker compose up -d app
echo
echo "✅ ICTU-CRIS chạy tại http://localhost:${CRIS_PORT:-8000}/ve"
echo
echo "Bước tiếp — nạp dữ liệu từ kho nguồn (đọc cả trang chi tiết, khoảng 2 giờ):"
echo "  docker compose run --rm app sync && docker compose run --rm app people \\"
echo "    && docker compose run --rm app normalize && docker compose run --rm app link \\"
echo "    && docker compose run --rm app dedup && docker compose run --rm app quality"
$AI && echo "  rồi: docker compose run --rm app ai embed && docker compose run --rm app ai topics && docker compose run --rm app ai suggest" || true
echo
if [ -n "${CRIS_ADMIN_PASSWORD:-}" ]; then
  echo "🔐 Đăng nhập đã bắt buộc — ${CRIS_ADMIN_EMAIL} / mật khẩu đã đặt ở CRIS_ADMIN_PASSWORD."
else
  echo "⚠ Chế độ mở (chưa bắt buộc đăng nhập) — chỉ chạy trong mạng nội bộ, không mở ra Internet."
fi
