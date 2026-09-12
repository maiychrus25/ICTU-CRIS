# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/); dự
án tuân theo [Semantic Versioning](https://semver.org/lang/vi/).

## [Unreleased]

## [0.6.0] - 2026-09-12

### Fixed (giao diện)

- Footer nguồn dữ liệu cố định ở đáy khung nhìn trên mọi bố cục (`frontend/components/data-notice-footer.tsx`).

### Added

- Bản báo cáo kỳ đóng băng, có phiên bản (lát cắt L1, điểm BA "P"): `POST
  /api/periods/{id}/reports` (`rd_officer`) chụp lại toàn bộ hồ sơ kê khai của
  kỳ (mọi trạng thái) cùng công trình/tác giả/minh chứng tại thời điểm gọi
  thành một phiên bản mới, không đổi về sau (`cris/report.py`, `build_report`,
  migration `0018_period_report.sql`); `sha256` băm payload để kiểm lại report
  không bị sửa. `GET /api/periods/{id}/reports` liệt kê các phiên bản,
  `GET /api/reports/{id}` xem đầy đủ một phiên bản, `GET
  /api/reports/{id}/export?format=csv|xlsx` tải CSV (BOM UTF-8) hoặc XLSX
  (`openpyxl`, sheet "Tổng hợp" đơn vị × trạng thái + tổng theo loại, sheet
  "Chi tiết") — cấp khoa chỉ thấy hồ sơ của đơn vị mình trong một báo cáo.
  `POST /api/periods/{id}/finalize` (chốt kỳ) nay tự sinh một bản báo cáo,
  trả thêm `report_id`.
- Thông báo trong ứng dụng (lát cắt L2, điểm BA "H"): người dùng biết hồ sơ
  của mình đổi trạng thái (`cris/notify.py`, migration `0019_notification.sql`).
  Móc gọi từ route sau khi nghiệp vụ thành công (không sửa `cris.declare`/
  `cris.link`): hồ sơ chuyển `ChoKhoaDuyet` → báo `faculty_head` cùng đơn vị;
  `KhoaDaDuyet`/`ChoPhongKiemTra` → mọi `rd_officer`; `DatYeuCau`/`DaChot`/trả
  về `Nhap`/`ChoBoSung`/`Rut` → người tạo hồ sơ (cộng `faculty_officer` cùng
  đơn vị khi trả về); kỳ báo cáo mở/đóng nộp/huỷ/chốt → `faculty_officer`/
  `faculty_head` mọi đơn vị (chốt kỳ trỏ thẳng tới bản báo cáo vừa sinh); liên
  kết tác giả được xác nhận → giảng viên có tài khoản. Không bao giờ báo cho
  chính người thao tác; lỗi khi gửi thông báo không làm hỏng thao tác chính.
  `GET /api/notifications?unread=&page=`, `POST /api/notifications/{id}/read`,
  `POST /api/notifications/read-all` (`cris/api/routes/notifications.py`).
- Vận hành (lát cắt L3): `GZipMiddleware` (`minimum_size=1024`) cho mọi
  `/api/*` — bản đồ tri thức ~1,5 MB còn ~300 KB. Provider AI cục bộ
  (`CRIS_AI_PROVIDER=local`) nay nạp ở luồng nền lúc khởi động thay vì chặn
  request đầu tiên ~1,8 s. `GET /api/health` mở rộng: `db` (503 khi CSDL lỗi),
  `model` (`loaded|missing|disabled|loading`), `last_sync_age_h` (giờ từ lần
  đồng bộ gần nhất), `version`. `GET /api/units/{id}/overview?period_id=` góc
  nhìn khoa: số công trình theo loại/5 năm gần nhất, 10 giảng viên nhiều công
  trình nhất, lượt tác giả đang chờ xác nhận, hồ sơ kê khai theo trạng thái
  của một kỳ (mặc định kỳ đang mở mới nhất), số giảng viên chưa có công trình
  liên kết — cấp khoa chỉ xem đơn vị mình (403 khác), `rd_officer`/
  `school_leader` xem mọi đơn vị (`cris/api/routes/units.py`). `deploy/pipeline.sh`
  gộp toàn bộ đường ống dữ liệu (trước chỉ có tay trên máy chủ) thành một
  script trong repo, cờ `--nightly` bỏ hai bước nặng `ai topics`/`ai map`;
  `deploy/upgrade.sh` nhắc xem release notes khi migrate có bản ghi mới;
  `docs/deploy-prod.md` thêm khối `nginx` khuyến nghị (header bảo mật,
  `client_max_body_size 12m`, tắt nén ở nginx vì app đã tự nén) và lịch cron
  đêm mới (`--nightly` các đêm thường, đủ vào chủ nhật).

## [0.5.0] - 2026-09-12

### Added

- Tìm kiếm ngữ nghĩa, tìm chuyên gia, cổng công khai kiểm tra đề tài (lát cắt J1):
  `GET /api/works?mode=semantic` tìm theo nghĩa trên tiêu đề đã gõ (`cris/ai/search.py`,
  `semantic_works`), rơi về từ khoá kèm giải thích khi AI chưa bật; `POST /api/ai/experts`
  / `GET /api/ai/experts/{id}` gợi ý giảng viên gần chuyên môn với một đề tài đề xuất
  (`cris/ai/expert.py`, `find_experts` — điểm `Σ s_i·0,8^hạng` trên top-200 công trình gần
  nghĩa nhất, gộp theo người qua `v_person_publications`, hệ số ×1,1 cho công trình gần
  đây, lọc học vị/đơn vị/loại trừ), lưu `ai_query(kind='experts')` (migration
  `0014_ai_query_kind.sql`); `POST /api/public/check-topic` cổng công khai không cần đăng
  nhập cho sinh viên trước khi đăng ký đề tài (đề tài tương tự các khoá trước + giảng viên
  gần chuyên môn), rate-limit 20 lượt/5 phút/IP, không lưu lịch sử tra cứu, không lộ email/
  điện thoại giảng viên. CLI `python -m cris ai experts "<đề tài>" [--k 10]`. Đo trên DB
  thật bằng `scripts/eval_experts.py` — số liệu ở `docs/ai.md`.
- Bản đồ tri thức, xu hướng chủ đề, đồ thị đồng tác giả (lát cắt J2): `GET /api/ai/map`
  chiếu 2 chiều PCA (SVD, numpy) của toàn bộ vector ngữ nghĩa (`cris/ai/map.py`,
  `build_map`) — mỗi điểm kèm `topic_id` (khớp cụm từ khoá mới nhất bằng một truy vấn SQL
  gộp cho toàn bộ kho, không lặp theo từng công trình), `unit_id`, năm, loại, tiêu đề cắt
  120 ký tự; tâm cụm là trung bình toạ độ; kèm `units` (đơn vị active có điểm, để hiện tên);
  cache trong `ai_map` (migration `0015_ai_map.sql`, giữ 1 dòng mới nhất mỗi mô hình), 404
  khi chưa dựng. CLI `python -m cris ai map`. `GET /api/ai/trends?by=cohort|year` đếm công
  trình sống theo (cụm, khoá|năm) (`cris/ai/trends.py`), 12 cụm lớn nhất + gộp "khác",
  `share` cộng ≈ 1 mỗi khoá/năm. `GET /api/ai/coauthors?min_works=` đồ thị giảng viên cùng
  đứng tên công trình đã liên kết (`cris/ai/coauthors.py`), `weight` = số công trình chung,
  cắt tối đa 300 nút theo số công trình.
- Trích dẫn, bộ lọc/facets công trình, lý lịch khoa học, mới cập nhật và RSS (lát cắt K1):
  `GET /api/works/{id}/citation?style=apa|ieee|bibtex` dựng từ metadata đã chuẩn hoá
  (`cris/cite.py`, tác giả theo vai trong `author_mention`; đồ án/luận văn/luận án ghi
  sinh viên là tác giả, GVHD là người hướng dẫn; `download=1` tải `.bib` kèm
  `Content-Disposition`). `GET /api/works/{id}` thêm `pdf_url`/`source_url` (từ bản ghi
  nguồn hiện hành) và `keywords` (tách `keywords_raw`); `WorkSummary` thêm `keywords` (tối
  đa 6) cho chip ở danh sách. `GET /api/works` thêm bộ lọc `pub_type` (khớp `indexes`),
  `quartile`, `cohort`, `keyword` (ranh giới `[,;]`, không phân biệt hoa/thường — "AI"
  không khớp "AIoT"); `GET /api/works/facets` đếm theo từng giá trị trên công trình sống.
  `GET /api/persons/{id}` thêm `rank` (học hàm — cột mới `person.rank`, migration
  `0016_person_rank.sql`, `cris.people.import_people` cập nhật từ `archive.rank`) và
  `scholar_url`. `GET /api/persons/{id}/cv?format=html` sinh lý lịch khoa học tự chứa
  (`cris/cv.py`, escape toàn bộ, A4, tái dùng `cris.cite.apa`). `GET /api/recent?limit=`
  công trình thêm/đổi ở lượt đồng bộ gần nhất đã xong (`cris/api/routes/recent.py`).
  `GET /api/feed.xml` RSS 2.0 công khai 20 công trình mới nhất (`cris/api/routes/feed.py`,
  đường dẫn công khai đọc từ `CRIS_PUBLIC_URL`).
- Cảnh báo bất thường dữ liệu (lát cắt K2): `python -m cris quality scan`
  (`cris/anomaly.py`, `scan`) quét sáu loại bất thường chỉ đọc `work`/`person` —
  ghi Scopus/WoS (nhóm ISI) nhưng không có DOI; năm ngoài khoảng 1990–năm hiện
  tại+1; luận văn/đồ án trùng tiêu đề chuẩn hoá với một bài báo; hai giảng viên
  cùng ORCID (bình thường bị chặn bởi `UNIQUE(orcid)`, cờ này phòng khi ràng
  buộc bị nới); DOI sai định dạng `10.xxxx/…`; bài báo không có tóm tắt — ghi/
  đóng `quality_flag` (migration `0017_quality_flag.sql`, UNIQUE theo
  `COALESCE(work_id,0), COALESCE(person_id,0)` vì NULL không bị ràng buộc UNIQUE
  thường của PostgreSQL chặn trùng); quét idempotent, cờ `dismissed` không bao
  giờ bị đụng lại, cờ `resolved` mở lại nếu bất thường tái xuất hiện.
  `GET /api/quality/anomalies?kind=&state=&severity=&page=` (lọc, `summary`
  đếm cờ đang mở theo loại) và `POST /api/quality/anomalies/{id}/dismiss
  {reason}` (vai trò `rd_officer`, lý do bắt buộc — 400 nếu thiếu, 404 nếu
  không có cờ, ghi audit `quality.dismiss`); `GET /api/quality` thêm chỉ số
  `anomalies_open`. Quét trên DB thật (7.618 công trình, 400 giảng viên):
  `scopus_no_doi` 64, `thesis_title_equals_article` 2, `missing_abstract_article`
  1.697; `year_out_of_range`, `orcid_duplicate`, `doi_invalid` đều 0 — ORCID
  trùng không xảy ra được trong dữ liệu hiện có vì bị `UNIQUE(orcid)` chặn từ
  lúc nhập (xem mục Known issues bản 0.4.0: 10/410 hồ sơ bị từ chối vì lý do
  này), không phải cờ chưa quét đúng.

### Fixed

- `jobTitle` ở kho nguồn là chức vụ, không phải đơn vị: hiệu trưởng/hiệu phó nay thuộc
  đơn vị thật **Ban Giám hiệu** (`BGH`), "Trưởng khoa" không còn bị nhập thành đơn vị;
  migration `0013_units_from_positions.sql` gom dữ liệu đã có, giữ id để hồ sơ kê khai
  và tài khoản không đổi (`cris/people.py`).

## [0.4.0] - 2026-09-11

### Added

- Lượt tên vai `mentor` giữ chỗ từ `meta.GVHD` (lát cắt I4): `cris/normalize.py`
  (`extract_fields`) nay đọc `archive.meta["GVHD"]` khi `archive.mentors` rỗng — nguồn
  không dựng được thẻ `lv-mentor-link` khi trang chỉ ghi người hướng dẫn giữ chỗ — và tạo
  một lượt tên vai `mentor` (`ICTU_TEACHER` → `is_placeholder=true`; tên thật, có thể nhiều
  người tách bằng `,`/`;` → `is_placeholder=false` từng người), đúng cách nó đã đọc
  `meta["Sinh viên"]` cho vai `student`. CLI mới `python -m cris normalize --redo
  [--doc-type do_an]` chuẩn hoá lại toàn bộ bản ghi sống (không chỉ phần đang chờ) để vá
  hồi tố các `work` đã chuẩn hoá trước khi có nhánh này — trường `manual`/`merge` vẫn được
  bảo vệ như thường. Chạy trên DB thật: 4.621 lượt tên giữ chỗ mới (khớp số liệu README
  "Ba số liệu"), `python -m cris ai mentors` (lát cắt I3) từ `scanned=0 suggested=0` lên
  `scanned=4621 suggested=1381` — xem `docs/ai.md` mục 6.

- CI/CD triển khai máy chủ thật (lát cắt I1): `.github/workflows/deploy.yml`
  chạy khi một GitHub Release được công bố (hoặc chạy tay, input `tag` bắt
  buộc) — job `wait-image` chờ ảnh `ghcr.io/maiychrus25/ictu-cris:<phiên
  bản>-ai` có trên GHCR (`docker manifest inspect`, tối đa 15 phút vì
  `docker.yml` dựng ảnh song song), job `deploy` (`environment: production`,
  `concurrency: deploy-prod`) SSH thuần (không action bên thứ ba) chạy
  `deploy/upgrade.sh <tag>` trên máy chủ rồi smoke test `/api/health` +
  `/api/about`. `deploy/upgrade.sh` (chạy được cả bằng tay): sao lưu CSDL
  (`pg_dump -Fc`) trước khi đổi gì, kéo hoặc dựng ảnh `-ai`, sửa
  `deploy/docker-compose.override.yml` trỏ ảnh mới (giữ bản cũ ở `.prev`),
  `migrate` rồi khởi động lại, chờ `/api/health`; thất bại thì tự khôi phục
  ảnh cũ và thoát mã lỗi. Mẫu
  `deploy/docker-compose.override.example.yml` (tệp thật đặc thù máy chủ,
  không commit). Tài liệu mới [docs/deploy-prod.md](docs/deploy-prod.md).

- Minh chứng dạng tệp thật (lát cắt I2): `cris/declare.py` —
  `sniff_content_type` nhận diện pdf/png/jpeg/docx qua chữ ký byte (không tin
  phần mở rộng tên tệp gửi lên), `add_evidence_file` kiểm kích thước (tối đa
  10 MB) và loại, băm SHA-256, ghi tệp vào `CRIS_DATA_DIR/evidence/<id
  hồ sơ>/<sha256 rút gọn><đuôi>` (ghi tạm rồi `os.replace`), `get_evidence`
  kiểm phạm vi đơn vị (NFR-02) khi tải về. Migration
  `0011_evidence_file.sql` thêm `evidence.storage_path/size_bytes/sha256/
  content_type/original_name`. API `POST /api/declarations/{id}/evidence/file`
  (multipart, vai trò `rd_officer` như minh chứng dạng liên kết/ghi chú hiện
  có) → 201, 413 nếu quá khổ, 415 nếu loại không hợp lệ; `GET
  /api/evidence/{id}/file` trả `FileResponse` kèm `Content-Disposition`, cần
  đăng nhập khi auth bật và 403 nếu khác đơn vị (cấp khoa), 404 nếu không có
  minh chứng dạng tệp. Thêm phụ thuộc `python-multipart` (MIT) để FastAPI
  phân tích `multipart/form-data`. `Dockerfile` tạo `/data`
  (`ENV CRIS_DATA_DIR=/data`) — triển khai thật cần thêm volume `cris_data:/data`
  vào `deploy/docker-compose.yml`.

- Gợi ý người hướng dẫn cho đồ án `ICTU_TEACHER` (lát cắt I3, FR-AI):
  `cris/ai/mentor.py` — `suggest_mentors(conn, provider, *, k=5, min_votes=2,
  min_score=0.70)`: với mỗi đồ án có lượt tên vai `mentor` giữ chỗ và chưa có
  liên kết, lấy `k` đồ án láng giềng gần nhất (cosine) trong tập đồ án đã có
  người hướng dẫn thật đã liên kết, gộp theo `person_id` (`votes` = số láng
  giềng, `score` = tổng cosine), ghi `ai_suggestion(kind='mentor', ...)` —
  UPSERT, xoá gợi ý cũ khi không còn ứng viên qua ngưỡng. Migration
  `0012_ai_mentor.sql` mở CHECK `ai_suggestion.kind` thêm `mentor` và
  `author_link.confidence` thêm `ai_mentor`. `cris/link.py` thêm
  `add_candidate(conn, mention_id, person_id, confidence, basis)` (dùng
  `_insert` sẵn có) để xếp một ứng viên vào hàng đợi tác giả từ nguồn ngoài
  so tên. API `GET /api/ai/mentors?unit=&min_votes=&page=`,
  `POST /api/ai/mentors/{work_id}/accept {person_id}` (vai trò `rd_officer`)
  tạo `author_link` **`ChoXacNhan`** (đang chờ, không tự xác nhận — BR-18),
  409 nếu lượt tên đã có liên kết đang chờ/đã xác nhận; `ACTION_LABELS` thêm
  `link.ai_candidate`. CLI `python -m cris ai mentors [--k --min-votes
  --min-score]`. Thử trên DB thật: `scanned=0 suggested=0` — nguồn
  (`cris/source/repository.py`) chỉ dựng `archive.mentors` từ thẻ liên kết
  giảng viên trên trang, trang giữ chỗ `ICTU_TEACHER` không có thẻ này nên
  không có lượt tên vai `mentor` nào được tạo (giữ chỗ hay không) cho 4.655/
  5.375 đồ án; thuật toán đã kiểm đủ bằng `FakeProvider` (13 test,
  `tests/test_ai_mentor.py`, dựng lượt tên giữ chỗ trực tiếp bằng SQL) —
  chi tiết và việc cần làm tiếp ở [docs/ai.md](docs/ai.md) mục 6.

### Fixed

- `python -m cris ai download` nay tải vào `CRIS_AI_MODEL_DIR` (nếu đặt) như provider
  `local`, thay vì luôn vào cache người dùng — trong container `docker compose run --rm
  app ai download` từng bị mất tệp khi container bị xoá (phát hiện khi triển khai thật).
- `docker.yml` publish thêm biến thể ảnh `:<version>-ai` (extra `[ai]` cài sẵn).

### Added

- Chỉnh tay có xuất xứ (lát cắt H2, BR-23): `cris/edit.py` — `EDITABLE`
  (`title`, `doi`, `year_issue`, `journal`, `volume`, `pub_type_raw`,
  `cohort`, `abstract`, `keywords_raw`; **không** gồm tác giả/đơn vị/minh
  chứng) và `set_field(conn, work_id, field, value, actor_id, reason)`: một
  giao dịch, lý do bắt buộc, công trình phải còn sống (`merged_into_id IS
  NULL`), `year_issue` ép int (rỗng → NULL), `title` cập nhật lại
  `title_norm` (`rules.norm_title`), ghi `field_provenance(set_kind='manual',
  set_by)` và `audit.log('work.edit')`.
- `PATCH /api/works/{id}/fields` (vai trò `rd_officer`) body
  `{field, value, reason}` → `{field, old, new}`; 400 nếu `field` ngoài
  `EDITABLE` (kèm danh sách trường cho phép), 404 nếu không có công trình,
  409 cho lỗi nghiệp vụ (`cris/api/routes/search.py`). `ACTION_LABELS` thêm
  `work.edit` "Chỉnh tay trường dữ liệu".
- Kê khai hai cấp theo `docs/ba/03-state.md` §3.2 (lát cắt H1, NFR-02/NFR-03):
  hồ sơ kê khai đi qua `Nhap → ChoKhoaDuyet → KhoaDaDuyet → ChoPhongKiemTra →
  DatYeuCau → DaChot`, mỗi bước gắn vai trò (`faculty_officer`, `faculty_head`,
  `rd_officer`) và có thể trả về `Nhap` kèm lý do bắt buộc
  (`cris/declare.py` — `_TRANSITIONS`, `set_state(..., actor_roles,
  actor_unit_id)`); nhánh chuẩn bị cũ `ChoBoSung`/`Rut` giữ nguyên, chỉ chạy
  được khi kỳ chưa đóng nộp. Migration `0010_declaration_states.sql` mở CHECK
  `declaration.state` cho đủ 8 trạng thái; `period.DECLARATION_STATES` cập
  nhật cùng bộ.
- Phạm vi đơn vị (NFR-02): vai trò cấp khoa chỉ kê khai, xem và chuyển trạng
  thái được hồ sơ của đơn vị mình — lọc ở tầng SQL (`add_declaration`,
  `list_declarations` nhận `actor_roles`/`actor_unit_id`), không chỉ ẩn trên
  giao diện; sai vai trò hoặc khác đơn vị → `PermissionError` (API 403).
- `finalize_period(conn, period_id, actor_id)` — `POST
  /api/periods/{id}/finalize` (vai trò `rd_officer`): kỳ phải `DaDongNop`,
  mọi hồ sơ `DatYeuCau` → `DaChot`, trả `{finalized, skipped: [{id, state}]}`;
  ghi `audit_log('declaration.DaChot')` từng hồ sơ được chốt và một
  `audit_log('period.finalize')` cho kỳ.
- `cris.api.deps.current_user(conn, request)` → `{id, roles, unit_id,
  unit_code}` (chế độ mở vẫn dùng được header `X-CRIS-User` để thử vai);
  `GET /api/auth/me` và `POST /api/auth/login` trả thêm `unit_code`. CLI
  `python -m cris user create --email --name --roles a,b [--unit CODE]
  [--password]` và `user set-unit --email --unit CODE`. `ACTION_LABELS` thêm
  `declaration.ChoKhoaDuyet`, `declaration.KhoaDaDuyet`,
  `declaration.ChoPhongKiemTra`, `declaration.DatYeuCau`, `declaration.DaChot`,
  `period.finalize`.
- Giảng viên tự kê khai (lát cắt H3): vai trò `lecturer` được kê khai hồ sơ
  cho công trình của chính mình (`v_person_publications` của
  `app_user.person_id`, trạng thái liên kết `DaNoiTuDong`/`DaXacNhan`) vào
  đơn vị của mình (`app_user.unit_id`, hoặc `person.unit_id` nếu `NULL`), và
  chuyển `Nhap → ChoKhoaDuyet`/`Nhap`, `ChoBoSung → Rut` hồ sơ do chính mình
  tạo (`cris/declare.py` — `_assert_owner`, `_assert_own_work`,
  `list_my_declarations`). CLI `python -m cris user create-lecturers [--unit
  CODE] [--dry-run]` tạo tài khoản `lecturer` không mật khẩu từ mỗi `person`
  giảng viên có email, khớp với `app_user` cùng email để idempotent
  (`cris.auth.create_lecturers`). API `GET /api/me/works` (công trình của tôi,
  kèm cờ `declared_in`), `GET /api/me/declarations`, `POST /api/me/declarations
  {period_id, work_id, note?}`; `GET /api/auth/me` trả thêm `person_id`.
  `GET /api/me/works` với tài khoản chưa gắn hồ sơ giảng viên → 409.

### Changed

- Tìm kiếm công trình (`_works_query`, `GET /api/works`) khớp thêm
  `w.title_norm ILIKE` với từ khoá đã bỏ dấu (`rules.strip_accents`), cạnh
  hai điều kiện cũ (`w.title ILIKE`, `m.raw_name ILIKE`) — gõ không dấu vẫn
  ra kết quả đúng.

## [0.3.0] - 2026-09-11

### Added

- `GET /api/persons?q=&kind=&limit=` (lát cắt G, G1): tìm giảng viên/sinh
  viên theo tên, khớp qua `person.name_keys` (có/không dấu, đủ họ tên) hoặc
  `display_name ILIKE` (một phần); `works` đếm trên `v_person_publications`
  ở trạng thái liên kết sống (`cris/api/routes/persons.py`).
- `GET /api/topics` thêm `keywords` (8 từ khoá nặng nhất) và `built_at`;
  `GET /api/topics/{id}` (mới): từ khoá đầy đủ kèm trọng số và tối đa 50
  công trình khớp cụm, cùng cách khớp với bộ lọc `topic` ở `/api/works`
  (`cris/api/routes/search.py`).
- `GET /api/sync/runs?page=` và `GET /api/sync/runs/{id}`: lịch sử các lượt
  đồng bộ (mới nhất trước) với số thêm/đổi/mất, thời lượng, cảnh báo, và 20
  `source_record` mới/đổi gần nhất của lượt (`cris/api/routes/sync.py`).
- Đăng nhập cục bộ (lát cắt G, G2, NFR-01): `cris/auth.py` băm mật khẩu bằng
  `hashlib.pbkdf2_hmac` (PBKDF2-HMAC-SHA256, 260.000 vòng, salt riêng mỗi
  người) và quản lý phiên trong bảng `session` mới (`cris/migrations/
  0009_auth.sql`) — chỉ thư viện chuẩn, không thêm dependency. CLI `python -m
  cris user set-password <email>` (đọc `CRIS_PASSWORD` hoặc hỏi qua `getpass`)
  và `python -m cris user list`.
- `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
  (`cris/api/routes/auth.py`): cookie phiên `cris_session` (`HttpOnly`,
  `SameSite=Lax`, `Secure` khi `CRIS_COOKIE_SECURE=1`, hết hạn 12 giờ, gia hạn
  khi dùng tối đa 1 lần/5 phút); giới hạn 5 lần đăng nhập sai/5 phút theo
  email (bộ nhớ tiến trình) → 429. `GET /api/about` thêm `auth_required: bool`.
- **Chế độ mở** (chưa `app_user` nào có mật khẩu): hành vi cũ giữ nguyên —
  không bắt buộc đăng nhập, nhận actor qua header `X-CRIS-User` hoặc
  `rd_officer` đầu tiên. Ngay khi có người đặt mật khẩu, `deps.Actor` bắt buộc
  cookie phiên hợp lệ; `deps.require_role("rd_officer")` áp cho mọi POST ở
  `cris/api/routes/queue.py` và `periods.py`; `POST /api/compare` cần đăng
  nhập (mọi vai trò) khi bật; `GET /api/audit` cần đăng nhập khi bật, các GET
  khác giữ công khai.
- `deploy/setup.sh`, `deploy/.env.example`: biến `CRIS_ADMIN_PASSWORD` tuỳ
  chọn (đặt mật khẩu cho người dùng mặc định lúc cài) và `CRIS_COOKIE_SECURE`.
- Kê khai công trình vào kỳ báo cáo (lát cắt K, G3, FR-K-04..09 một phần):
  `cris/declare.py` (mới) — `add_declaration` (kỳ phải `DangMo`, công trình
  phải còn sống, một (kỳ, công trình, đơn vị) chỉ kê khai một lần),
  `set_state` (`Nhap`↔`ChoBoSung`, `Nhap`/`ChoBoSung`→`Rut`, bắt buộc lý do
  khi chuyển sang `ChoBoSung`/`Rut`, từ chối khi kỳ đã `DaDongNop`/`Huy`),
  `add_evidence` (`kind` ∈ `link`/`file`/`note`), `list_declarations`,
  `get_declaration`; mỗi thao tác ghi `declaration_event` và `audit_log`.
  API (`cris/api/routes/declarations.py`): `GET`/`POST
  /api/periods/{pid}/declarations`, `GET /api/declarations/{id}`, `POST
  /api/declarations/{id}/state`, `POST /api/declarations/{id}/evidence`;
  `ValueError` → 409, kỳ/hồ sơ không tìm thấy → 404, POST cần vai trò
  `rd_officer`.

## [0.2.0] - 2026-09-11

### Added

- API JSON FastAPI 13 endpoint (`/api/*`, OpenAPI tại `/docs`): tra cứu công
  trình và hồ sơ giảng viên, hàng đợi liên kết tác giả, hàng đợi nghi trùng,
  đối chiếu đề tài, chất lượng dữ liệu — lớp mỏng gọi vào tầng nghiệp vụ hiện
  có (`cris/api/`).
- `GET /api/stats` (tổng quan cho lãnh đạo): công trình theo năm × loại, theo
  đơn vị, top giảng viên, hàng đợi và tỉ lệ đã liên kết tác giả
  (`cris/api/routes/stats.py`).
- `GET /api/works.csv` và `GET /api/persons/{id}/publications.csv` (SC-05,
  UX-07): xuất danh sách công trình đã lọc ra CSV UTF-8 có BOM, tối đa 20.000
  dòng (`cris/api/routes/export.py`).
- `GET /api/audit` (SC-08): nhật ký thao tác đọc từ `audit_log`, nhãn tiếng
  Việt theo hành động, lọc theo thực thể và người thao tác
  (`cris/api/routes/audit.py`).
- `GET/POST /api/periods` và `POST /api/periods/{id}/close|cancel`: mở, đóng
  nộp, huỷ kỳ báo cáo và xem tiến độ theo đơn vị qua `cris/period.py`
  (`cris/api/routes/periods.py`).
- Rà soát trùng đề tài theo khoá (lát cắt E5): `cris/ai/screen.py`
  (`screen_cohort`), lệnh `python -m cris ai screen --cohort <mã>`,
  `GET /api/ai/screen` và `GET /api/ai/screen/cohorts` — so đồ án của một
  khoá với các khoá khác, ghi gợi ý `ai_suggestion(kind='topic_overlap')`,
  không đổi dữ liệu nghiệp vụ.
- Giao diện Next.js (`frontend/`, App Router, TypeScript, Tailwind, shadcn/ui,
  xuất tĩnh): tra cứu công trình và hồ sơ giảng viên, hàng đợi liên kết tác
  giả và nghi trùng, tổng quan cho lãnh đạo, xuất CSV, nhật ký thao tác, kỳ
  báo cáo, đối chiếu và rà soát trùng đề tài theo khoá, chất lượng dữ liệu —
  gọi `/api/*`, không có server-render phía Node lúc chạy.

### Changed

- `serve` nay chạy `uvicorn` phục vụ API FastAPI; giao diện Next.js thay UI
  HTML thuần cũ; một container (ảnh Docker đa tầng) phục vụ cả API và giao
  diện, cùng cổng 8000.

### Removed

- `cris/web` (UI HTML thuần, WSGI stdlib) và `tests/test_web_*.py`; cờ
  `python -m cris serve --legacy`.

### Fixed

- Rà soát trùng đề tài theo khoá dùng ngưỡng riêng `SCREEN_THRESHOLDS =
  (0.90, 0.80)`, hiệu chỉnh trên phân bố điểm thật (cohort 21, 529 đồ án:
  p50=0,835 · p90=0,897 · p99=0,928) thay cho ngưỡng khía cạnh 0,55/0,35 kế
  thừa từ `compare.py` — ngưỡng cũ gắn cờ 529/529 (100%), ngưỡng mới gắn cờ
  47/529 (8,9%). `screen_cohort` ghi thêm `max_score`/`level` vào payload;
  CLI có `--high`/`--mid`; `GET /api/ai/screen` thêm `min_score`, trả kết
  quả sắp theo `max_score` giảm dần (`cris/ai/screen.py`,
  `cris/api/routes/screen.py`, `cris/api/schemas.py`, `cris/cli.py`).

## [0.1.0] - 2026-09-10

Bản dự thi "Phát triển phần mềm mã nguồn mở tích hợp AI 2026". Tag `v0.1.0`.

Chưa có trong bản này: đăng nhập và phân quyền thật (NFR-01, NFR-02 — giao
diện hiện chạy với một người dùng mặc định, KHÔNG triển khai lên mạng công
khai), nhập Excel khoa (S-06), kê khai và phê duyệt (phần còn lại của lát cắt
K, toàn bộ D và R), nhà cung cấp AI ngoài (giao diện `explain` đã có chỗ).

### Added

- Lát cắt **S** (đồng bộ — sync): kéo dữ liệu công bố khoa học từ kho
  `repository.ictu.edu.vn`, lưu nguyên bản gốc theo phiên bản trong bảng
  `source_record` (`cris/sync.py`).
- Lát cắt **N** (chuẩn hoá — normalize): chuẩn hoá tên, ghi xuất xứ từng
  trường qua bảng `field_provenance`, nối tác giả, gộp bản ghi trùng, báo
  cáo chất lượng dữ liệu (`cris/normalize.py`, `cris/people.py`,
  `cris/link.py`, `cris/dedup.py`, `cris/quality.py`).
- Quét bù phân trang (**S-04**): kho nguồn sắp xếp theo cột không duy nhất
  nên lật trang tuần tự bỏ sót bản ghi mà không báo lỗi (đo 09/2026: 269
  trang `/do-an/` chỉ ra 5.364 trên 5.375). Khi lật trang xong mà vẫn thiếu
  so với số kho tự công bố, `iter_archive` quét bù theo bộ lọc `?cohort=`
  (đồ án, luận văn, luận án) hoặc `?dept=` (bài báo) — các trục phân hoạch
  kho khác nhau nên chạm được phần bị bỏ sót (`cris/source/repository.py`).
- **Tích hợp AI** (`cris/ai/`, [docs/ai.md](docs/ai.md)) — AI gợi ý, người quyết;
  không có AI vẫn chạy đủ chức năng:
  - Nhà cung cấp chọn bằng `CRIS_AI_PROVIDER`: `none` (mặc định), `fake` (kiểm
    thử), `local` — mô hình `paraphrase-multilingual-MiniLM-L12-v2` ONNX 8-bit
    (118 MB, 384 chiều, có tiếng Việt) chạy CPU qua `onnxruntime`, tải một lần
    và kiểm SHA-256. Thư viện AI là extra tuỳ chọn `pip install -e ".[ai]"`;
    gói lõi vẫn chỉ phụ thuộc `psycopg`.
  - Đối chiếu đề tài `/doi-chieu`: tìm công trình gần về nghĩa trên tiêu đề +
    tóm tắt + từ khoá, bảng so sánh theo bốn khía cạnh (giống / khác / chưa đủ
    thông tin), không hiện điểm phần trăm tổng hợp, luôn ghi "không phải toàn
    văn"; `provider=none` chạy đường lui khớp từ khoá có cảnh báo.
  - Gợi ý cho hàng đợi tác giả (xếp hạng ứng viên theo chủ đề các công trình
    đã xác nhận) và hàng đợi nghi trùng (tương đồng tóm tắt); trục chủ đề từ
    gom cụm 10.951 từ khoá làm bộ lọc `/tra-cuu?topic=`.
  - Rào chắn có test: mã AI chỉ ghi vào bảng `ai_*` (migration `0007`), không
    đổi `work`, `author_link`, `duplicate_group`, `field_provenance`.
  - CLI `python -m cris ai download|embed|topics|suggest|status`.
- Lược đồ kỳ báo cáo (lát cắt K, task 1): `period`, `declaration` (duy nhất
  theo kỳ + công trình + đơn vị), `evidence`, `declaration_event`; mở/đóng/huỷ
  kỳ gắn bộ quy tắc tại thời điểm mở (`cris/period.py`, migration `0006`).
- Giao diện web cho hàng đợi xác nhận và tra cứu — **không thêm thư viện nào**,
  viết bằng WSGI thuần stdlib (`wsgiref`), chạy bằng `python -m cris serve`:
  - Hàng đợi liên kết tác giả (SC-08): nhóm theo tên thô, sắp theo số công trình
    bị ảnh hưởng, xác nhận/bác bỏ/gán lại hàng loạt trong một transaction.
  - Hàng đợi nghi trùng (SC-07): so sánh từng trường cạnh nhau cho mọi thành
    viên, người dùng chọn bản sống sót và giá trị giữ lại cho từng trường mâu
    thuẫn. Nhóm khác sinh viên hiện cảnh báo đồ án nhóm và mặc định Giữ riêng.
  - Tra cứu công trình, hồ sơ công bố giảng viên, báo cáo chất lượng dữ liệu
    (SC-11, SC-12, SC-10). Trang chi tiết công trình hiện đủ ba cột: giá trị
    đang dùng, giá trị gốc, và nguồn.
  (`cris/web/`)
- CLI thống nhất: `python -m cris migrate|seed|sync [paths]|people|normalize|link|dedup|quality [--json]|serve`.
- Bộ tài liệu phân tích nghiệp vụ (BA) bản 1.0 — 18 tệp, `docs/ba/`.
- Mô hình dữ liệu bản 0.1 cho lát cắt S + N + T-01/T-02 —
  `docs/ba/17-mo-hinh-du-lieu.md`.
- Migrations `0001`–`0007` (khởi tạo lược đồ, ràng buộc duy nhất
  `source_record`, ràng buộc DOI, view tra cứu).
- 208 test pytest chạy trên PostgreSQL 16 thật, không mock cơ sở dữ liệu;
  thêm 3 test `slow` chạy mô hình AI thật (`pytest -m slow`).
- Hồ sơ nguồn mở: `LICENSE` (Apache-2.0), `NOTICE`, `DEPENDENCIES.md`,
  `docs/LICENSE_NOTICE.md`, `CODE_OF_CONDUCT.md`, mẫu issue
  (`.github/ISSUE_TEMPLATE/`), mẫu PR, CI (`pytest -v` trên PostgreSQL 16
  qua GitHub Actions).
- `BUILDING.md` — hướng dẫn dịch và chạy từ mã nguồn (Docker và venv).

### Đã kiểm chứng trên dữ liệu thật (10/09/2026)

Toàn kho `repository.ictu.edu.vn` đồng bộ đủ 8.034 bản ghi (đồ án 5.375/5.375 nhờ quét
bù phân trang), 7.618 công trình sau chuẩn hoá. Bài báo đạt 86,6 % có liên kết tác giả
(78,8 % tự nối, 15,9 % chờ xác nhận) so với 8 % ở nguồn. Vector cho toàn bộ công trình
sinh trong 11 phút trên CPU; đối chiếu một đề tài 3,25 s. Chi tiết: BUILDING.md §9.

### Đã biết (Known issues)

- Chỉ số `mentions_placeholder` trên trang chất lượng dữ liệu **chỉ đếm sinh viên**
  (`ICTU_STUDENT`, 302 lượt): bước chuẩn hoá không tạo lượt tên cho giảng viên hướng
  dẫn ghi placeholder `ICTU_TEACHER`, nên 4.655 đồ án không có lượt tên mentor nào và
  không xuất hiện trong chỉ số này. Con số thật của placeholder ở nguồn lớn hơn ~15 lần
  (4.621 + 302). Sẽ bổ sung chỉ số "đồ án không có giảng viên hướng dẫn" ở bản kế.
- Nhập hồ sơ giảng viên tạo 400/410 người: 10 hồ sơ bị từ chối vì trùng ORCID với hồ sơ
  khác ở nguồn (8 cặp cùng người có hai hồ sơ, 2 cặp hai người chung một ORCID). Hệ
  thống ghi lỗi thay vì gộp hay tạo trùng; hai cặp khác người cần người quyết.
- Liên kết tác giả của luận văn chủ yếu vào hàng đợi (68,7 % chờ xác nhận, 5,6 % tự nối)
  vì tên GVHD kèm học vị trùng nhiều ứng viên; đây là việc của hàng đợi, không phải lỗi.

### Fixed

- Siêu dữ liệu tìm thấy (`_page`, `_backfill`) không còn được tính vào băm
  nội dung của `source_record`. Vì kho nguồn sắp xếp không ổn định, số trang
  của một bản ghi trôi giữa các lần đồng bộ; băm cả nó thì mỗi lần chạy lại
  sinh một loạt phiên bản giả cho bản ghi không hề đổi nội dung
  (`cris/sync.py`).
- `count(DISTINCT ...) OVER (...)` trong hàng đợi tác giả: PostgreSQL không
  hỗ trợ `DISTINCT` trong window function nên mọi lần mở hàng đợi đều lỗi 500.
  Thay bằng subquery gộp rồi nối lại theo tên thô (`cris/web/views_queue.py`).

[Unreleased]: https://github.com/maiychrus25/ICTU-CRIS/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/maiychrus25/ICTU-CRIS/releases/tag/v0.6.0
[0.5.0]: https://github.com/maiychrus25/ICTU-CRIS/releases/tag/v0.5.0
[0.4.0]: https://github.com/maiychrus25/ICTU-CRIS/releases/tag/v0.4.0
[0.3.0]: https://github.com/maiychrus25/ICTU-CRIS/releases/tag/v0.3.0
[0.2.0]: https://github.com/maiychrus25/ICTU-CRIS/releases/tag/v0.2.0
[0.1.0]: https://github.com/maiychrus25/ICTU-CRIS/releases/tag/v0.1.0
