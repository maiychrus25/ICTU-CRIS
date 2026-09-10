# Giao diện mới: FastAPI + Next.js — Kế hoạch triển khai

Quyết định 11/09/2026 sau khi chạy thử v0.1.0: giao diện server-render HTML thuần xấu và
khó dùng; ba tiêu chí chấm "hoàn thiện", "thân thiện", "trình diễn" (30/100 điểm) phụ
thuộc trực tiếp vào giao diện. **Bỏ HTML thuần**, làm lại bằng Next.js trên một API JSON.
Mức tham chiếu về độ chuyên nghiệp: `CuongKenn/ICTU_Proteus-os` — tham khảo cách tổ chức,
không sao chép cấu trúc; mục tiêu là bằng hoặc hơn.

Hạn: nộp kho mã nguồn **30/09/2026**, chung kết **10/10/2026**. Còn 19 ngày.

## Quyết định kiến trúc

| Vấn đề | Chọn | Vì sao | Thay thế đã cân nhắc |
|---|---|---|---|
| API | **FastAPI** + `uvicorn`, `pydantic` | OpenAPI/Swagger tự sinh — giám khảo thấy được "tài liệu kỹ thuật"; kiểm thử bằng `TestClient`; pydantic kiểm dữ liệu vào | Mở rộng WSGI stdlib thành JSON: phải tự viết CORS, validation, docs — không đáng |
| Frontend | **Next.js** (App Router, TypeScript) + Tailwind + shadcn/ui, `output: "export"` | Xuất tĩnh → FastAPI phục vụ tại `/` → **một container, một cổng**, `deploy/` gần như không đổi; shadcn cho giao diện chuyên nghiệp nhanh, tiếng Việt tốt | Vite + React: nhẹ hơn; Next.js được chọn vì định tuyến theo tệp, xuất tĩnh, và hệ sinh thái shadcn/ui |
| Trạng thái/dữ liệu | TanStack Query (fetch + cache), `fetch` gốc | Đủ cho CRUD + hàng đợi; không Redux | — |
| Bảng | TanStack Table qua shadcn `DataTable` | Hàng đợi cần chọn nhiều, sắp, lọc | — |
| Xác thực | **Chưa** (NFR-01 ngoài phạm vi) — API giữ hành vi người dùng mặc định + header `X-CRIS-User` | Không đổi phạm vi giữa cuộc thi | — |
| Tầng nghiệp vụ | **Không đổi** `cris/*.py` | 209 test, đã chạy trên dữ liệu thật; API chỉ gọi vào | — |
| UI cũ `cris/web/` | Giữ tới khi UI mới ngang màn, rồi gỡ trong một commit | Sản phẩm không bị gãy giữa chừng | — |

Nguyên tắc "một dependency runtime" của v0.1.0 **thôi áp dụng cho tầng web**; tầng
nghiệp vụ vẫn chỉ `psycopg`. Ghi vào `DEPENDENCIES.md` đầy đủ giấy phép (FastAPI MIT,
uvicorn BSD-3, pydantic MIT, httpx BSD-3 cho test) và ghi quyết định này vào CHANGELOG.

## Global Constraints

1. **Không sửa** `cris/link.py`, `dedup.py`, `normalize.py`, `people.py`, `sync.py`,
   `quality.py`, `period.py`, `cris/ai/*`. API là lớp mỏng gọi vào chúng. Thấy cần sửa →
   dừng, ghi báo cáo.
2. **Mọi quyết định qua API vẫn đi qua `decide_link` / `decide_group`** với `actor_id`
   thật; lô nhiều id một transaction (dùng lại lớp bọc hoãn commit trong `views_queue.py`,
   chuyển thành hàm dùng chung ở `cris/api/deps.py`).
3. **AI gợi ý, người quyết** (BR-18): không endpoint nào tự động gộp/nối. Không hiện
   điểm % tương đồng tổng hợp (BR-17); mọi trang đối chiếu có dòng "không phải toàn văn".
4. **Escape do React lo**, nhưng API không trả HTML; mọi chuỗi là dữ liệu thô.
5. **Test API** bằng `fastapi.testclient` trên PostgreSQL thật, fixture `conn` sẵn có;
   provider `fake` cho AI. **Frontend**: `tsc --noEmit`, `next lint`, `next build` phải
   xanh; test tương tác bằng Playwright cho 3 luồng chính (tra cứu → chi tiết; xác nhận
   liên kết; đối chiếu đề tài).
6. **Cả hai biến DB** trong test như trước; DB riêng mỗi tác vụ song song; pytest tiền cảnh.
7. Tiếng Việt có dấu trong giao diện; mã tiếng Anh. Header SPDX trên `.py`, `.ts`, `.tsx`
   (mở rộng `test_spdx.py` sang `.ts/.tsx/.js` với `//`).
8. Thông điệp commit tiếng Anh, conventional-commit, không trailer ghi công AI.
9. Không đưa `node_modules`, `.next`, `out/` vào repo; `package-lock.json` có.

## Cấu trúc

```
cris/api/__init__.py
cris/api/app.py            # create_app(): FastAPI, CORS (dev), mount static UI ở "/"
cris/api/deps.py           # kết nối DB mỗi request, actor_id, lô transaction
cris/api/schemas.py        # pydantic: Work, Person, Link, DupGroup, Suggestion, CompareResult…
cris/api/routes/search.py  # /api/works, /api/works/{id}, /api/persons/{id}
cris/api/routes/queue.py   # /api/queue/authors, /api/queue/duplicates, quyết định
cris/api/routes/compare.py # /api/compare, /api/compare/{id}
cris/api/routes/quality.py # /api/quality, /api/about
tests/test_api_*.py
frontend/                  # Next.js
  app/(layout, page=/tra-cuu, doi-soat/tac-gia, doi-soat/trung-lap/[id], tra-cuu/cong-trinh/[id],
       tra-cuu/giang-vien/[id], doi-chieu, doi-chieu/[id], chat-luong-du-lieu, ve)
  components/ui/           # shadcn
  components/…             # DataTable, AspectMatrix, ProvenanceTable, QueueActions
  lib/api.ts               # client typed từ OpenAPI (openapi-typescript)
  e2e/                     # Playwright
Dockerfile                 # multi-stage: node build → python runtime phục vụ out/
```

## Hợp đồng API (tóm tắt — chi tiết sinh ra ở `/docs`)

| Method | Đường dẫn | Trả về | Gọi vào |
|---|---|---|---|
| GET | `/api/about` | nguồn, lần đồng bộ, đếm theo loại, provider AI, giới hạn | `views_about._stats/_provider_info` → chuyển sang `cris/api` |
| GET | `/api/quality` | `quality.report` + nhãn + link hàng đợi | `quality.report` |
| GET | `/api/works?q&doc_type&year&unit&topic&page` | danh sách + tổng | truy vấn `v_work_current`, `v_work_unit`, `ai_topic*` (lấy từ `views_search.py`) |
| GET | `/api/works/{id}` | công trình + `fields[]` {name, value, raw, source} + tác giả + trạng thái liên kết | `field_provenance`, `author_mention/link` |
| GET | `/api/persons/{id}` | hồ sơ + đếm theo loại + theo năm + công trình + `pending_count` + `last_sync` | `v_person_publications` |
| GET | `/api/queue/authors?state&q&page` | nhóm theo `raw_name`, ứng viên, độ tin cậy, gợi ý AI | `views_queue` SQL |
| POST | `/api/queue/authors/decide` | `{link_ids[], decision, reason?, person_id?}` → kết quả từng id, **lô một transaction** | `link.decide_link` |
| GET | `/api/queue/duplicates` / `/{gid}` | nhóm, thành viên, `diff`, `hint`, tương đồng AI | `duplicate_*`, `ai_suggestion` |
| POST | `/api/queue/duplicates/{gid}/decide` | `{decision: merge\|keep\|skip, survivor_id?, field_choices?, reason?}` | `dedup.decide_group` |
| POST | `/api/compare` | `{title, description, aspects, doc_types?}` → kết quả + `query_id` | `compare_topic` |
| GET | `/api/compare/{id}` | kết quả đã lưu | `ai_query` |
| GET | `/api/topics` | cụm chủ đề cho bộ lọc | `ai_topic` |

Lỗi trả JSON `{detail}` với mã HTTP đúng (400 thiếu lý do, 404, 409 trạng thái không hợp
lệ, 503 chưa có người dùng). Mọi endpoint có `response_model` để OpenAPI đầy đủ.

## Thiết kế giao diện — quyết định trước khi code

- **Bố cục**: thanh bên trái cố định (Tra cứu · Đối chiếu đề tài · Hàng đợi tác giả · Hàng
  đợi nghi trùng · Chất lượng dữ liệu · Về hệ thống), nội dung rộng, đọc được ở 1280 và
  co được ở 768 (UX-10: lãnh đạo mở trên điện thoại chỉ ở màn duyệt — lát cắt sau).
- **Màu**: nền trung tính lệch xanh lam nhẹ; một màu nhấn xanh lam đậm; ba màu trạng thái
  (xanh lá / vàng / đỏ) chỉ cho trạng thái, không dùng làm màu nhấn. Chế độ tối có sẵn
  qua shadcn.
- **Kiểu chữ**: Inter hoặc Be Vietnam Pro (hỗ trợ dấu tiếng Việt đầy đủ), số dùng
  `tabular-nums` trong bảng.
- **Ngôn ngữ giao diện**: tiếng Việt; thuật ngữ khớp bộ BA (hàng đợi, xác nhận, bác bỏ,
  giữ riêng, xuất xứ…).
- **Ba màn phải "ăn điểm" khi trình diễn**: đối chiếu đề tài (bảng khía cạnh có màu trạng
  thái, thẻ kết quả), nghi trùng (so cạnh nhau, chỗ khác tô đậm, nút Giữ riêng nổi bật
  khi có cảnh báo đồ án nhóm), chi tiết công trình (ba cột xuất xứ).
- **Trạng thái rỗng, đang tải, lỗi** có thiết kế — không để trang trắng.

---

### Task 1: API FastAPI đủ 12 endpoint + OpenAPI

Chặn Task 2–4. Chuyển logic truy vấn từ `cris/web/views_*.py` sang `cris/api/routes/*`
(copy SQL, bỏ HTML). `create_app()` mount `frontend/out` ở `/` nếu thư mục tồn tại.
`python -m cris serve` chuyển sang chạy `uvicorn` (giữ tên lệnh). Test: mỗi endpoint
có ít nhất một test hạnh phúc và một test lỗi; rào chắn "API không đổi bảng nghiệp vụ"
cho `POST /api/compare`; `POST decide` lô có một id sai → không id nào đổi.
`DEPENDENCIES.md` + `pyproject` (`api` không phải extra — là runtime) trong cùng commit.

### Task 2: Scaffold Next.js + hệ thống giao diện + 3 màn lõi

`create-next-app` (TypeScript, Tailwind, App Router, `src/` không), shadcn init, client
API sinh từ OpenAPI (`openapi-typescript`), layout + thanh bên, và ba màn: tra cứu +
chi tiết công trình (ba cột xuất xứ), đối chiếu đề tài (biểu mẫu + kết quả với bảng
khía cạnh), về hệ thống. `next build` với `output: "export"` chạy được; FastAPI phục vụ
`out/` — chạy thật một container.

### Task 3: Hàng đợi tác giả, hàng đợi nghi trùng, hồ sơ giảng viên, chất lượng dữ liệu

DataTable chọn nhiều + hành động lô; trang nghi trùng so cạnh nhau với `diff`; hồ sơ
giảng viên có biểu đồ theo năm (Recharts, MIT); chất lượng dữ liệu là bảng chỉ số bấm
được. Playwright cho ba luồng chính.

### Task 4: Đóng gói, CI, tài liệu, gỡ UI cũ

Dockerfile multi-stage (node:22-alpine build → python:3.12-slim runtime, `out/` sao chép
vào, uvicorn); `deploy/docker-compose.yml` giữ cổng 8000; CI thêm job `frontend` (npm ci,
tsc, lint, build, Playwright); `docker.yml` không đổi. README: ảnh chụp màn hình mới,
badge; BUILDING.md mục frontend; `docs/ba/07-screens.md` cập nhật theo màn thật. Gỡ
`cris/web/` và test của nó khi mọi màn đã có bản mới; `test_spdx` mở rộng sang `.ts/.tsx`.

## Ngoài kế hoạch này

- Đăng nhập, phân quyền (NFR-01/02). Lát cắt K/D/R. Nhập Excel. Provider AI ngoài.

## Tự rà

`pytest -q -m "not slow"` xanh · `npm run build` xanh · `docker build` một ảnh chạy được cả
API lẫn UI · `git diff --stat` không đụng tầng nghiệp vụ · `DEPENDENCIES.md` có đủ
fastapi/uvicorn/pydantic/httpx và mọi gói npm runtime có giấy phép MIT/ISC/Apache.
