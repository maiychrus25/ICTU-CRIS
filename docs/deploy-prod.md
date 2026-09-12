# Triển khai máy chủ thật

Máy chủ thật: VPS Ubuntu 22.04, IP `103.253.21.139`, phục vụ tại
`https://cris.ahvlabs.com` (Cloudflare proxy trước, DNS trỏ về IP này).

## Kiến trúc

```
Internet → Cloudflare (proxy) → nginx (80/443, chứng chỉ Let's Encrypt)
              → 127.0.0.1:8000 → container "app" (ictu-cris:<phiên bản>-ai)
                                       ↕
                                  container "db" (postgres:16)
```

- `nginx` (`/etc/nginx/sites-available/cris.ahvlabs.com`) chỉ đọc — không nằm
  trong compose, không do CI đụng tới. Chuyển tiếp vào `127.0.0.1:8000`.
- `docker compose` chạy trong `/opt/ictu-cris/deploy`, gồm hai tệp:
  - `docker-compose.yml` — theo repo (dựng ảnh từ mã nguồn nếu không có
    override).
  - `docker-compose.override.yml` — **đặc thù máy chủ, không nằm trong repo**
    (xem `.gitignore`). Trỏ ảnh đã kéo/dựng sẵn (`build: !reset null`), giới
    hạn cổng ra `127.0.0.1` (`ports: !override`), giới hạn log. Mẫu ở
    [`deploy/docker-compose.override.example.yml`](../deploy/docker-compose.override.example.yml);
    `deploy/upgrade.sh` tự tạo tệp thật từ mẫu này nếu chưa có.
- Volume `cris_pg` (dữ liệu PostgreSQL) và `cris_models` (mô hình AI đã tải,
  tránh tải lại mỗi lần dựng ảnh) — cả hai giữ nguyên qua các lần nâng cấp.
- Người vận hành compose/cron là user hệ thống `deploy` (không sudo, thuộc
  nhóm `docker`), sở hữu toàn bộ `/opt/ictu-cris`. `root` vẫn còn để vận hành
  tay khi cần (vá hệ điều hành, nginx, ...) nhưng CI chỉ SSH bằng `deploy`.
- Cron của `deploy` (`crontab -u deploy -l`):
  - `0 2 * * 1-6` — đường ống dữ liệu đêm (thứ Hai–thứ Bảy):
    `deploy/pipeline.sh --nightly` (bỏ hai bước nặng `ai topics`/`ai map`, chỉ
    chạy đủ vào đêm chủ nhật), log vào `/opt/ictu-cris/sync-nightly.log`.
  - `0 2 * * 0` — đêm chủ nhật: `deploy/pipeline.sh` (không có `--nightly`) —
    chạy đủ cả `ai topics`/`ai map`, cùng log trên.
  - `30 3 * * *` — sao lưu `pg_dump | gzip` vào `/opt/ictu-cris/backups/`,
    xoá bản cũ hơn 7 ngày (`find -mtime +7 -delete`).
  - Cron của `root` (giám sát các dự án khác trên máy — `openclaw`, ...)
    không đụng tới; chỉ hai dòng ICTU-CRIS ở trên đã chuyển sang `deploy`.

## Secrets GitHub cần tạo

Tạo ở **Settings → Secrets and variables → Actions** (khuyến nghị đặt trong
environment `production` để có thể bật bước duyệt thủ công trước khi deploy):

| Secret | Giá trị |
|---|---|
| `PROD_HOST` | `103.253.21.139` |
| `PROD_USER` | `deploy` |
| `PROD_SSH_KEY` | Nội dung khoá **riêng** ed25519 của `deploy` dùng cho CI. Khoá đã tạo sẵn ở máy làm việc, đường dẫn file: xem với người triển khai (không dán khoá vào tài liệu/commit). Khoá công khai tương ứng đã có trong `/home/deploy/.ssh/authorized_keys` trên máy chủ. |
| `PROD_KNOWN_HOSTS` | Host key của `103.253.21.139` (ba dòng `ssh-ed25519`/`ssh-rsa`/`ecdsa-sha2-nistp256`, định dạng như `ssh-keyscan 103.253.21.139` in ra) — người triển khai có sẵn tệp, dán nguyên văn ba dòng đó vào secret. |

`deploy.yml` chỉ SSH thuần (không action bên thứ ba) bằng khoá và known_hosts
ở trên, không có credential nào khác trong workflow.

## Quy trình phát hành

1. Cập nhật `pyproject.toml` (`version`), `CHANGELOG.md`, viết
   `docs/release-notes/vX.Y.Z.md` như các bản trước.
2. Đẩy tag: `git tag vX.Y.Z && git push origin vX.Y.Z`.
   → `docker.yml` dựng và đẩy `ghcr.io/maiychrus25/ictu-cris:X.Y.Z` +
   `:X.Y.Z-ai` lên GHCR; `release.yml` dựng sdist/wheel và tạo GitHub Release.
3. Khi Release được **công bố** (`published`), `deploy.yml` tự chạy:
   - job `wait-image` chờ `docker manifest inspect
     ghcr.io/maiychrus25/ictu-cris:X.Y.Z-ai` có trên GHCR (poll 30 giây/lần,
     tối đa 15 phút — vì `docker.yml` dựng ảnh này song song với lúc tag vừa
     được đẩy, có thể chưa xong ngay khi Release được tạo).
   - job `deploy` (environment `production`, `concurrency: deploy-prod` —
     không chạy chồng hai lượt deploy) SSH vào `deploy@103.253.21.139` chạy
     `bash /opt/ictu-cris/deploy/upgrade.sh vX.Y.Z`, rồi smoke test
     `GET /api/health` và `GET /api/about` (in `works`).
4. Muốn chạy tay (bỏ qua chờ Release, hoặc triển khai lại một tag cũ):
   Actions → **Deploy** → **Run workflow**, nhập `tag`.

## `deploy/upgrade.sh` làm gì

Script `deploy/upgrade.sh <tag>` (idempotent — chạy lại cùng tag không hại,
dùng được cả bằng tay lẫn từ CI):

1. `git fetch --tags && git checkout -q <tag>` trong `/opt/ictu-cris`.
2. `docker pull ghcr.io/maiychrus25/ictu-cris:<phiên bản>-ai`; nếu chưa có
   trên registry thì kiểm ảnh cùng tên đã có sẵn ở máy (bỏ qua dựng lại nếu
   có), ngược lại `docker build --build-arg EXTRAS="[ai]"` tại chỗ.
3. Sao lưu CSDL **trước khi đổi gì**: `pg_dump -Fc` vào
   `backups/pre-<tag>-<ngày>.dump` (cùng thư mục `/opt/ictu-cris/backups/` với bản đêm).
4. Sửa dòng `image:` trong `deploy/docker-compose.override.yml` (giữ bản cũ ở
   `.prev` — cần cho bước quay lui).
5. `docker compose run --rm -T app migrate`, `docker compose up -d app`, chờ
   `GET /api/health` trả 200 tối đa 60 giây.
6. Thất bại → khôi phục `.prev`, `docker compose up -d app` (về lại ảnh cũ),
   thoát mã 1. **CSDL không tự quay lui** — migration trong dự án này chỉ
   thêm (không xoá cột/bảng), nên ảnh cũ vẫn chạy được trên CSDL đã migrate;
   nếu cần lùi hẳn dữ liệu thì khôi phục từ bản sao lưu (xem dưới). Thành
   công → `docker image prune -f`, in phiên bản đang chạy (`GET /api/about`
   nếu có trường `version`, hiện chưa có nên in `docker compose images app`).

`--dry-run` in ra các bước sẽ chạy mà không chạy gì.

## `deploy/pipeline.sh` làm gì

Đường ống dữ liệu đầy đủ (đồng bộ nguồn cho tới các gợi ý AI), gọi bởi cron
đêm ở trên hoặc chạy tay `bash deploy/pipeline.sh [--nightly]` (từ máy chủ,
trong `/opt/ictu-cris`; script tự `cd` vào `deploy/` nên gọi từ đâu cũng
được). Idempotent — mỗi bước tự bỏ qua phần đã làm, chạy lại không hại. Các
bước theo thứ tự, in `date` trước mỗi bước:

1. `sync` → `people` → `normalize` → `link` → `dedup` → `quality` (đồng bộ
   nguồn, chuẩn hoá, liên kết tác giả, gộp trùng, số liệu chất lượng).
2. `ai embed`; `ai topics` (bỏ qua khi `--nightly`); `ai suggest`.
3. Lấy khoá đồ án mới nhất bằng `psql` qua `docker compose exec db` (không
   hard-code như bản cũ), rồi `ai screen --cohort <khoá>` rà trùng đề tài của
   khoá đó với các khoá khác; `normalize --redo --doc-type do_an` chuẩn hoá
   lại đồ án (rà trùng có thể đổi `needs_review`). Bỏ qua hai bước này nếu
   chưa có đồ án nào gắn `cohort`.
4. `ai mentors` gợi ý người hướng dẫn thật; `ai map` dựng lại bản đồ tri thức
   (bỏ qua khi `--nightly`); `quality scan` quét bất thường dữ liệu (K2).

`--nightly` bỏ `ai topics` và `ai map` (hai bước nặng nhất, không đổi nhiều
theo ngày) — dùng cho cron các đêm thường; đêm chủ nhật chạy đủ (không có cờ)
để hai số liệu đó không lệch quá một tuần.

## Quay lui (rollback)

- **Chỉ ảnh bị lỗi** (CSDL vẫn tương thích, ví dụ vừa deploy một bản có lỗi ở
  tầng ứng dụng): chạy lại `deploy/upgrade.sh <tag cũ>` — script tự sao lưu,
  tự sửa override về ảnh của tag cũ, tự kiểm tra health.
- **Cần lùi cả dữ liệu** (hiếm — chỉ khi một migration làm hỏng dữ liệu):
  1. `docker compose stop app`
  2. Khôi phục bản sao lưu gần nhất trước lúc nâng cấp
     (`backups/pre-<tag>-<ngày>.dump` (cùng thư mục `/opt/ictu-cris/backups/` với bản đêm), hoặc bản đêm trong
     `backups/cris-<ngày>.sql.gz` — xem mục Sao lưu):
     ```bash
     cd /opt/ictu-cris/deploy
     docker compose exec -T db dropdb -U cris --if-exists cris
     docker compose exec -T db createdb -U cris cris
     cat deploy/backups/pre-vX.Y.Z-2026-MM-DD.dump | docker compose exec -T db pg_restore -U cris -d cris
     ```
  3. `deploy/upgrade.sh <tag cũ>` để đổi lại ảnh, hoặc `docker compose up -d
     app` nếu override đã trỏ đúng ảnh cũ.

## Nâng cấp bằng tay

Không cần chờ GitHub Actions — SSH vào máy chủ rồi chạy đúng script CI dùng:

```bash
ssh deploy@103.253.21.139
bash /opt/ictu-cris/deploy/upgrade.sh vX.Y.Z
```

## Sao lưu

- **Trước mỗi nâng cấp**: `deploy/upgrade.sh` tự tạo
  `backups/pre-<tag>-<ngày>.dump` (cùng thư mục `/opt/ictu-cris/backups/` với bản đêm) (định dạng `pg_dump -Fc`, dùng
  `pg_restore` để khôi phục).
- **Hàng đêm** (cron `deploy`, 03:30): `deploy/backups/cris-<ngày>.sql.gz`
  (`pg_dump | gzip`, dùng `gunzip | psql` để khôi phục); giữ 7 ngày gần nhất,
  bản cũ hơn tự xoá.
- Sao lưu nằm trên cùng máy chủ (không đẩy đi nơi khác) — nếu cần sao lưu
  ngoài máy chủ (ổ đĩa hỏng, máy chủ mất), đó là việc chưa làm, ghi nhận ở
  đây để làm sau.

## nginx

`nginx` không nằm trong repo (xem mục Kiến trúc) — khối `location` dưới đây
là mẫu khuyến nghị để chỉnh tay trong
`/etc/nginx/sites-available/cris.ahvlabs.com`:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # App đã tự nén (GZipMiddleware, minimum_size=1024 byte) — không nén lại ở
    # đây (tránh nén hai lần); để mặc định (gzip off) là đủ.
    gzip off;

    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options SAMEORIGIN always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;

    client_max_body_size 12m;   # đủ cho minh chứng PDF/ảnh (evidence)
}
```

## Đã biết / giới hạn

- Không có blue-green hay canary — nâng cấp là dừng `app` một khoảng ngắn
  (đo lần đầu tiên ở `BUILDING.md`/`CHANGELOG.md`, mục "Đã kiểm chứng" của
  từng bản), `db` không dừng.
- `docker manifest inspect` trong `wait-image` cần ảnh trên GHCR là công khai
  (không cần đăng nhập); nếu sau này đổi ảnh sang riêng tư, job này cần thêm
  bước `docker login`.
