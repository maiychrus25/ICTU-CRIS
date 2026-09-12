#!/usr/bin/env bash
# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
#
# Đường ống dữ liệu đầy đủ: đồng bộ nguồn → chuẩn hoá → liên kết tác giả → gộp
# trùng → chấm chất lượng → các bước AI (embed/topics/suggest), rà trùng đề
# tài của khoá đồ án mới nhất (`ai screen`), chuẩn hoá lại đồ án (rà trùng có
# thể đổi `needs_review`), gợi ý người hướng dẫn, dựng lại bản đồ tri thức,
# rồi quét bất thường dữ liệu. Idempotent — mỗi bước tự bỏ qua phần đã làm
# (`embed`/`normalize` chỉ phần đổi trừ khi ép, v.v.), chạy lại không hại.
#
# Dùng tay hoặc từ cron (xem docs/deploy-prod.md):
#   bash deploy/pipeline.sh              # đủ các bước, kể cả "ai topics"/"ai map" (nặng)
#   bash deploy/pipeline.sh --nightly    # bỏ "ai topics"/"ai map" — dành cho đêm thường,
#                                        # chạy đủ (không --nightly) vào đêm chủ nhật
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

NIGHTLY=false
for arg in "$@"; do
  case "$arg" in
    --nightly) NIGHTLY=true ;;
    *) echo "lỗi: tham số không rõ: $arg" >&2; exit 2 ;;
  esac
done

R="docker compose run --rm -T app"

step() {
  echo "-- $(date '+%F %T') $*"
}

step "sync"
$R sync
step "people"
$R people
step "normalize"
$R normalize
step "link"
$R link
step "dedup"
$R dedup
step "quality"
$R quality

step "ai embed"
$R ai embed

if ! $NIGHTLY; then
  step "ai topics"
  $R ai topics
fi

step "ai suggest"
$R ai suggest

# Khoá đồ án mới nhất: lấy trực tiếp từ CSDL qua psql (không hard-code như bản
# cũ trên VPS) — cohort thường là số dạng chuỗi ("21"), ORDER BY ép kiểu số khi
# thuần chữ số, rơi về so chuỗi nếu không (ví dụ cohort dạng khác "K21").
set -a
# shellcheck disable=SC1091
[ -f .env ] && . ./.env
set +a
COHORT="$(docker compose exec -T db psql -U "${POSTGRES_USER:-cris}" -d "${POSTGRES_DB:-cris}" -tAc "
  SELECT cohort FROM work
  WHERE doc_type='do_an' AND cohort IS NOT NULL
  ORDER BY (CASE WHEN cohort ~ '^[0-9]+$' THEN cohort::int END) DESC NULLS LAST, cohort DESC
  LIMIT 1
" | tr -d '[:space:]')"

if [ -z "$COHORT" ]; then
  echo "   không có đồ án nào có cohort — bỏ qua 'ai screen' và 'normalize --redo --doc-type do_an'" >&2
else
  step "ai screen --cohort $COHORT"
  $R ai screen --cohort "$COHORT"
  step "normalize --redo --doc-type do_an"
  $R normalize --redo --doc-type do_an
fi

step "ai mentors"
$R ai mentors

if ! $NIGHTLY; then
  step "ai map"
  $R ai map
fi

step "quality scan"
$R quality scan

echo PIPELINE-DONE
