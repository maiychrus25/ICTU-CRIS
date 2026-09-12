#!/usr/bin/env bash
# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
#
# Nâng cấp máy chủ thật lên một phiên bản đã phát hành. Idempotent — chạy lại
# với cùng tag không gây hại. Dùng được bằng tay:
#   deploy/upgrade.sh v0.3.1
#   deploy/upgrade.sh v0.3.1 --dry-run   # chỉ in các bước, không chạy gì
# hoặc từ .github/workflows/deploy.yml qua SSH:
#   ssh deploy@<host> 'bash /opt/ictu-cris/deploy/upgrade.sh v0.3.1'
#
# Các bước: (1) git fetch --tags && checkout <tag>; (2) docker pull ảnh
# "-ai" từ GHCR, dựng tại chỗ nếu chưa có trên registry (bỏ qua dựng nếu ảnh
# cùng tên đã có sẵn ở máy này); (3) sao lưu CSDL bằng pg_dump -Fc trước khi
# đổi gì; (4) sửa deploy/docker-compose.override.yml trỏ ảnh mới (giữ bản cũ
# ở .prev để quay lui); (5) migrate rồi khởi động lại app, chờ /api/health;
# (6) thất bại → khôi phục ảnh cũ và thoát mã 1 (CSDL KHÔNG tự quay lui — xem
# docs/deploy-prod.md), thành công → dọn ảnh cũ và in phiên bản đang chạy.
set -euo pipefail

IMAGE_REPO="ghcr.io/maiychrus25/ictu-cris"
HEALTH_URL="http://127.0.0.1:8000/api/health"
ABOUT_URL="http://127.0.0.1:8000/api/about"
HEALTH_TIMEOUT=60

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DEPLOY_DIR="$REPO_DIR/deploy"
OVERRIDE_FILE="$DEPLOY_DIR/docker-compose.override.yml"
OVERRIDE_EXAMPLE="$DEPLOY_DIR/docker-compose.override.example.yml"

# Toàn bộ logic nằm trong một hàm rồi gọi ở cuối tệp (main "$@") — bước 1/6 tự
# `git checkout` chính thư mục chứa script này; nếu chạy thẳng từ ngoài hàm,
# bash có thể đọc tiếp tệp đã đổi nội dung giữa chừng và hỏng theo những cách
# khó dò. Gói trong hàm thì bash phân tích trọn hàm vào bộ nhớ trước khi chạy.
main() {

DRY_RUN=false
TAG=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    -*) echo "lỗi: tham số không rõ: $arg" >&2; exit 2 ;;
    *) TAG="$arg" ;;
  esac
done
if [ -z "$TAG" ]; then
  echo "dùng: $0 <tag> [--dry-run]" >&2
  echo "  ví dụ: $0 v0.3.1" >&2
  exit 2
fi
VER="${TAG#v}"
IMAGE_TAG="${IMAGE_REPO}:${VER}-ai"
LOCAL_IMAGE="ictu-cris:${VER}-ai"
NGAY="$(date +%F)"
BACKUP_FILE="$REPO_DIR/backups/pre-${TAG}-${NGAY}.dump"   # cùng chỗ với cron pg_dump

echo "== ICTU-CRIS upgrade → ${TAG} (ảnh ${IMAGE_TAG}) =="

if $DRY_RUN; then
  cat <<EOF
[dry-run] không chạy gì, chỉ in các bước sẽ thực hiện:

1/6 Mã nguồn
    git -C "$REPO_DIR" fetch --tags
    git -C "$REPO_DIR" checkout -q "$TAG"

2/6 Ảnh ${IMAGE_TAG}
    docker pull "$IMAGE_TAG" && docker tag "$IMAGE_TAG" "$LOCAL_IMAGE"
    # không kéo được (404/không có mạng):
    #   nếu "$LOCAL_IMAGE" đã có sẵn ở máy này → bỏ qua, dùng ảnh đó
    #   ngược lại → docker build -t "$LOCAL_IMAGE" --build-arg EXTRAS="[ai]" "$REPO_DIR"

3/6 Sao lưu CSDL trước khi đổi
    mkdir -p "$REPO_DIR/backups"
    docker compose exec -T db pg_dump -U \$POSTGRES_USER -d \$POSTGRES_DB -Fc > "$BACKUP_FILE"

4/6 Ghi ảnh mới vào override (giữ bản cũ ở .prev)
    cp "$OVERRIDE_FILE" "$OVERRIDE_FILE.prev"   # nếu đã có tệp
    sed -i "s|^\\(\\s*image:\\s*\\).*|\\1$LOCAL_IMAGE|" "$OVERRIDE_FILE"

5/6 Migrate và khởi động lại
    docker compose run --rm -T app migrate
    # có migration mới → nhắc xem "Nâng cấp" trong docs/release-notes/$TAG.md
    docker compose up -d app
    curl -fs "$HEALTH_URL"   # chờ tối đa ${HEALTH_TIMEOUT}s

6/6 Dọn dẹp
    thành công → docker image prune -f, in phiên bản (GET $ABOUT_URL hoặc docker compose images app)
    thất bại   → khôi phục "$OVERRIDE_FILE.prev", docker compose up -d app, exit 1
EOF
  exit 0
fi

# 1/6 — mã nguồn
echo "-- 1/6 lấy mã nguồn theo tag ${TAG}"
git -C "$REPO_DIR" fetch --tags
# Tệp máy chủ tự thêm (chưa theo dõi) mà tag mới bắt đầu quản lý (vd deploy/pipeline.sh
# từng chép tay) sẽ chặn checkout — cất sang <tệp>.local.bak rồi mới checkout.
git -C "$REPO_DIR" ls-tree -r --name-only "$TAG" | while IFS= read -r f; do
  if [ -e "$REPO_DIR/$f" ] && ! git -C "$REPO_DIR" ls-files --error-unmatch -- "$f" >/dev/null 2>&1; then
    echo "   cất tệp chưa theo dõi bị tag mới ghi đè: $f -> $f.local.bak"
    mv "$REPO_DIR/$f" "$REPO_DIR/$f.local.bak"
  fi
done
git -C "$REPO_DIR" checkout -q "$TAG"

# 2/6 — ảnh
echo "-- 2/6 lấy ảnh ${IMAGE_TAG}"
pull_ok=false
if docker pull "$IMAGE_TAG"; then
  pull_ok=true
  docker tag "$IMAGE_TAG" "$LOCAL_IMAGE"
else
  echo "   không kéo được ${IMAGE_TAG} từ registry (chưa có hoặc lỗi mạng)"
fi
if ! $pull_ok; then
  if docker image inspect "$LOCAL_IMAGE" >/dev/null 2>&1; then
    echo "   ảnh ${LOCAL_IMAGE} đã có sẵn ở máy này — bỏ qua dựng lại"
  else
    echo "   dựng ảnh tại chỗ: ${LOCAL_IMAGE}"
    docker build -t "$LOCAL_IMAGE" --build-arg EXTRAS="[ai]" "$REPO_DIR"
  fi
fi

cd "$DEPLOY_DIR"
set -a
# shellcheck disable=SC1091
[ -f .env ] && . ./.env
set +a

# 3/6 — sao lưu CSDL trước khi đổi gì
echo "-- 3/6 sao lưu CSDL vào ${BACKUP_FILE}"
mkdir -p "$REPO_DIR/backups"
docker compose exec -T db pg_dump -U "${POSTGRES_USER:-cris}" -d "${POSTGRES_DB:-cris}" -Fc > "$BACKUP_FILE"
echo "   $(du -h "$BACKUP_FILE" | cut -f1) — ${BACKUP_FILE}"

# 4/6 — trỏ ảnh mới trong override (giữ bản cũ để quay lui)
echo "-- 4/6 ghi ảnh mới vào deploy/docker-compose.override.yml"
if [ ! -f "$OVERRIDE_FILE" ]; then
  echo "   deploy/docker-compose.override.yml chưa có — tạo từ mẫu deploy/docker-compose.override.example.yml"
  cp "$OVERRIDE_EXAMPLE" "$OVERRIDE_FILE"
fi
cp -f "$OVERRIDE_FILE" "$OVERRIDE_FILE.prev"
sed -i "s|^\(\s*image:\s*\).*|\1${LOCAL_IMAGE}|" "$OVERRIDE_FILE"

# 5/6 — migrate rồi khởi động lại, chờ health
echo "-- 5/6 migrate và khởi động lại app"
migrate_out="$(docker compose run --rm -T app migrate)"
echo "   $migrate_out"
if [ "$migrate_out" != "[]" ]; then
  echo "   có migration mới — xem \"Nâng cấp\" trong docs/release-notes/${TAG}.md, có thể cần chạy thêm bước dữ liệu" >&2
fi
docker compose up -d app

echo -n "   chờ ${HEALTH_URL}"
ok=false
for _ in $(seq 1 "$HEALTH_TIMEOUT"); do
  if curl -fs "$HEALTH_URL" >/dev/null 2>&1; then ok=true; break; fi
  echo -n "."
  sleep 1
done
echo

if ! $ok; then
  echo "lỗi: ${HEALTH_URL} không trả 200 sau ${HEALTH_TIMEOUT}s — khôi phục ảnh cũ" >&2
  mv -f "$OVERRIDE_FILE.prev" "$OVERRIDE_FILE"
  docker compose up -d app
  echo "   đã khôi phục deploy/docker-compose.override.yml và khởi động lại app với ảnh cũ" >&2
  echo "   CSDL KHÔNG tự quay lui (migration chỉ thêm) — xem docs/deploy-prod.md nếu cần khôi phục từ ${BACKUP_FILE}" >&2
  exit 1
fi

# 6/6 — thành công: dọn ảnh cũ, in phiên bản
echo "-- 6/6 dọn ảnh không dùng, in phiên bản đang chạy"
docker image prune -f >/dev/null
about_json="$(curl -fs "$ABOUT_URL" 2>/dev/null || true)"
ver="$(printf '%s' "$about_json" | python3 -c 'import json,sys
try:
    v = json.load(sys.stdin).get("version")
except Exception:
    v = None
print(v or "", end="")' 2>/dev/null || true)"
if [ -n "$ver" ]; then
  echo "   phiên bản đang chạy: $ver"
else
  docker compose images app
fi

echo "== xong: ${TAG} =="

}

main "$@"
