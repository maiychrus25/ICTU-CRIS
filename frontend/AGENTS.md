<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

# ICTU-CRIS — frontend (Next.js) brief

Giao diện của **ICTU-CRIS**, hệ thống thông tin nghiên cứu của Trường CNTT&TT – ĐH Thái Nguyên.
Một nguồn sự thật cho dữ liệu công bố khoa học: mỗi con số truy ngược được về bản ghi gốc;
**AI gợi ý, người quyết**. Người dùng: chuyên viên phòng KHCN (làm hàng đợi cả ngày), giảng viên
(xem hồ sơ, đối chiếu đề tài), lãnh đạo (xem số liệu). Giao diện này sẽ được chấm trong cuộc thi
phần mềm mã nguồn mở — nó phải trông chuyên nghiệp, đáng tin, không giống mẫu (template) tạo sẵn.

## Ràng buộc bắt buộc

- Chỉ ghi trong thư mục `frontend/`. Backend (`../cris/`) là của người khác — chỉ đọc.
- **Ngôn ngữ giao diện: tiếng Việt có dấu**, thuật ngữ cố định: *tra cứu, công trình, giảng viên,
  hàng đợi, xác nhận, bác bỏ, chuyển cho người khác, nghi trùng, gộp, giữ riêng, bỏ qua,
  xuất xứ (provenance), đối chiếu đề tài, khía cạnh, chất lượng dữ liệu, đồng bộ*.
  Mã nguồn, tên biến, commit: tiếng Anh.
- Mỗi file `.ts`/`.tsx` mới bắt đầu bằng hai dòng:
  ```ts
  // Copyright (c) 2026 ICTU-CRIS contributors
  // SPDX-License-Identifier: Apache-2.0
  ```
- Next.js App Router, TypeScript strict, Tailwind v4, shadcn/ui (đã cài các component trong
  `components/ui/`; thêm bằng `npx shadcn@latest add <name>` nếu cần), TanStack Query,
  TanStack Table, Recharts, lucide-react, sonner. Không thêm thư viện UI khác.
- **Xuất tĩnh**: `next.config.ts` phải có `output: "export"`, `trailingSlash: true`,
  `images: { unoptimized: true }`. FastAPI phục vụ `out/` tại `/`. Vì vậy **không dùng
  đoạn đường dẫn động `[id]`** — trang chi tiết nhận id qua query string
  (`/cong-trinh/?id=123`), đọc bằng `useSearchParams` trong client component bọc `<Suspense>`.
  Không dùng Server Actions, không dùng route handlers, không dùng `next/image` remote.
- Gọi API qua **một** client `lib/api.ts`: base URL = `process.env.NEXT_PUBLIC_API_BASE ?? ""`
  (rỗng = cùng gốc khi chạy trong FastAPI; dev dùng `http://localhost:8001`). Lỗi HTTP →
  ném `ApiError { status, detail }` (backend trả JSON `{detail}`); hiển thị `detail` nguyên
  văn cho người dùng bằng toast hoặc `<Alert>`.
- Kiểu dữ liệu TypeScript trong `lib/types.ts` viết tay theo đúng hợp đồng bên dưới (sau này
  sẽ sinh từ OpenAPI bằng `openapi-typescript`; giữ tên trường y hệt).
- `npm run lint`, `npx tsc --noEmit`, `npm run build` phải xanh trước khi kết thúc. Không được
  bỏ qua lỗi bằng `// @ts-ignore` hay tắt rule eslint.
- Trạng thái **đang tải** (skeleton), **rỗng** (thông điệp + việc nên làm tiếp), **lỗi** (detail +
  nút thử lại) phải có ở mọi trang. Không để trang trắng.
- Không hiển thị "điểm % tương đồng tổng hợp" ở đối chiếu đề tài (quy tắc nghiệp vụ BR-17);
  mọi trang đối chiếu có dòng `note` từ API ("… không phải toàn văn").
- Không có luồng nào để máy tự quyết; mọi nút quyết định đều là hành động của người dùng
  và có xác nhận khi không hoàn tác được (gộp bản ghi).

## Thiết kế — quyết định đã chốt, không bàn lại

- **Bố cục**: thanh bên trái cố định 240px (thu gọn thành icon ở < 1024px, Sheet ở mobile) với
  6 mục: Tra cứu · Đối chiếu đề tài · Hàng đợi tác giả · Hàng đợi nghi trùng · Chất lượng dữ liệu ·
  Về hệ thống. Thanh trên mỏng: tiêu đề trang + breadcrumb + ô tìm nhanh (⌘K không bắt buộc).
  Nội dung rộng tối đa 1440px, padding 24px; đọc tốt ở 1280, co được ở 768.
- **Màu**: nền trung tính **lệch xanh lam nhẹ** (không xám thuần, không cream); một màu nhấn
  xanh lam đậm (~ `oklch(0.45 0.13 255)`); ba màu trạng thái xanh lá/vàng/đỏ **chỉ** cho trạng
  thái nghiệp vụ (đã xác nhận / chờ / bác bỏ; khía cạnh trùng cao / vừa / thấp), không dùng làm
  nhấn. Chế độ tối có sẵn (next-themes + `dark:`), cùng độ chăm chút như sáng.
- **Chữ**: `Be Vietnam Pro` (next/font/google, subsets `latin`, `vietnamese`) cho toàn bộ;
  số trong bảng `tabular-nums`. Tiêu đề trang 24px/600, thân 14px, chú thích 12px.
- **Không** dùng gradient hero, không emoji làm icon, không card-hoá mọi thứ; bảng là bảng
  (viền mảnh, hàng cao 40px, hover nhẹ). Badge trạng thái có icon + chữ, không chỉ màu.
- Ba màn phải "ăn điểm" khi trình diễn:
  1. **Đối chiếu đề tài**: form bên trái (tiêu đề, mô tả, 4 khía cạnh: bài toán, đối tượng,
     phạm vi, phương pháp; lọc loại tài liệu), kết quả bên phải: mỗi công trình một thẻ với
     **ma trận khía cạnh** 4 ô tô màu trạng thái theo ngưỡng (cao ≥ 0.55, vừa ≥ 0.35, thấp),
     kèm giải thích ngắn; dòng `note` nổi bật ở đầu kết quả.
  2. **Nghi trùng (chi tiết)**: các bản ghi thành viên **so cạnh nhau theo cột**, hàng là các
     trường trong `compare_fields`; ô khác nhau (`diff_fields`) tô nền vàng nhạt; `hint`
     (ví dụ "đồ án nhóm") hiển thị thành cảnh báo và khi có hint thì nút **Giữ riêng** là nút
     chính. Gộp: chọn bản sống sót (radio) + chọn giá trị từng trường khác nhau (`field_choices`).
  3. **Chi tiết công trình**: bảng xuất xứ ba cột *Trường · Giá trị đang dùng · Giá trị gốc*
     và cột thứ tư *Nguồn* (chuỗi `source` từ API); tác giả với trạng thái liên kết và số
     ứng viên đang chờ.

## Đường dẫn trang (App Router, tất cả là client-side data fetching)

| Đường dẫn | Nội dung |
|---|---|
| `/` | chuyển hướng (client) sang `/tra-cuu/` |
| `/tra-cuu/` | ô tìm, bộ lọc (loại tài liệu, năm, chủ đề từ `/api/topics`), bảng kết quả phân trang 50 |
| `/cong-trinh/?id=` | chi tiết công trình (xuất xứ + tác giả) |
| `/giang-vien/?id=` | hồ sơ giảng viên: thẻ số liệu theo loại, biểu đồ cột theo năm (Recharts), bảng công trình, `pending_count`, `last_sync` |
| `/doi-chieu/` | form + kết quả; sau khi POST, đẩy `?id=<query_id>` vào URL để chia sẻ được |
| `/doi-chieu/?id=` | kết quả đã lưu (`GET /api/compare/{id}`) |
| `/doi-soat/tac-gia/` | hàng đợi liên kết tác giả: tab theo `state`, tìm theo tên, bảng chọn nhiều (checkbox), hành động lô: Xác nhận / Bác bỏ (bắt buộc lý do) / Chuyển cho người khác (nhập `person_id`); cột gợi ý AI (hạng, lý do) chỉ là gợi ý |
| `/doi-soat/trung-lap/` | danh sách nhóm nghi trùng (tab trạng thái), bấm vào → `/doi-soat/trung-lap/chi-tiet/?id=` |
| `/doi-soat/trung-lap/chi-tiet/?id=` | so cạnh nhau + quyết định |
| `/chat-luong-du-lieu/` | các chỉ số từ `/api/quality` dạng danh sách (nhãn – giá trị – nút "Mở hàng đợi" khi có `queue_url`), biểu đồ theo loại tài liệu |
| `/ve/` | Về hệ thống: nguồn, lần đồng bộ, đếm theo loại, khối "AI trong hệ thống" (provider, mô hình, giấy phép, số vector/chủ đề/gợi ý), danh sách **giới hạn** (`limits`) hiển thị trang trọng |

`queue_url` trong `/api/quality` là đường dẫn UI cũ (`/doi-soat/tac-gia`, `/doi-soat/trung-lap`) — trùng với đường dẫn mới, dùng trực tiếp.

## Hợp đồng API (JSON, prefix `/api`) — trích từ `../cris/api/schemas.py` (nguồn chuẩn, hãy đọc file đó)

- `GET /api/works?q&doc_type&year&unit&topic&page` → `{ items: WorkSummary[], page: {page, per_page, total} }`
  `WorkSummary { id, title, doc_type, doc_type_label, year, doi, state, needs_review }`
- `GET /api/works/{id}` → `WorkDetail { id, title, doc_type, doc_type_label, state, needs_review, has_manual, fields: FieldRow[], mentions: MentionRow[] }`
  `FieldRow { field, label, value, raw, source }`; `MentionRow { mention_id, role, role_label, position, raw_name, is_placeholder, is_truncated, linked_person_id, linked_person_name, link_state, pending_count }`
- `GET /api/persons/{id}` → `PersonProfile { id, display_name, degree, email, orcid, by_type: Record<string,number>, by_year: Record<string,number>, publications: PersonPublication[], pending_count, last_sync }`
  `PersonPublication { work_id, title, doc_type, year, doi, link_state, confidence }`; `LastSync { id, source, scope, status, started_at, finished_at }`
- `GET /api/topics` → `Topic[] { id, label, size }`
- `GET /api/queue/authors?state&q&page` → `{ items: AuthorQueueRow[], page, state }`
  `AuthorQueueRow { link_id, raw_name, work_id, work_title, candidate_person_id, candidate_name, confidence, degree_conflict, group_work_count, ai_rank, ai_score, ai_reason }`; `state` ∈ `ChoXacNhan | DaNoiTuDong | DaXacNhan | DaBacBo`
- `POST /api/queue/authors/decide` body `{ link_ids: number[], decision: "confirm"|"reject"|"reassign", reason?, person_id? }` → `{ ok, processed: number[], failed_id?, detail? }`; lỗi 400 `{detail}`
- `GET /api/queue/duplicates?state&page` (`state` = `NghiTrung` mặc định, `DaGop`, `GiuRieng`, `all`) → `{ items: DupGroupSummary[], page }`
  `DupGroupSummary { id, doc_type, basis, basis_label, hint, state, member_count, created_at }`
- `GET /api/queue/duplicates/{gid}` → `DupGroupDetail { id, doc_type, basis, basis_label, hint, state, compare_fields: string[], field_labels: Record<string,string>, diff_fields: string[], members: DupMember[], ai_similarity, decided_by, decided_at, reason, survivor_work_id }`
  `DupMember { id, state, title, fields: Record<string, unknown>, diff }`
- `POST /api/queue/duplicates/{gid}/decide` body `{ decision: "merge"|"keep"|"skip", survivor_id?, field_choices?: Record<string, number>, reason? }` → `{ ok, processed }`; 400/409 `{detail}`
- `POST /api/compare` body `{ title, description, aspects: Record<string,string>, doc_types?: string[], k? }` → `CompareOut { query_id, provider, fallback, note, input, results: CompareResultItem[], created_at }`
  `CompareResultItem { work_id, title, doc_type, year, score, aspects: Record<string,string>, url, explanation, ai_generated }` — `aspects` là nhãn mức theo khía cạnh (giá trị chuỗi như `"cao"|"vua"|"thap"` hoặc số dạng chuỗi; xử lý cả hai: nếu parse được số thì áp ngưỡng 0.55/0.35). Khi `fallback=true` (AI tắt) hiển thị cảnh báo "Đang dùng tìm theo từ khoá vì AI chưa bật".
- `GET /api/compare/{id}` → `CompareOut`
- `GET /api/quality` → `{ metrics: {key,label,value,queue_url}[], works_by_type, works_with_link_pct, last_sync }`
- `GET /api/about` → `{ source_url, repo_url, last_sync, works, works_by_type, ai: {provider, model, dim, repo, licence, size, runs, embeddings, topics, suggestions}, limits: string[] }`
- `GET /api/health` → `{status:"ok"}`

Nhãn loại tài liệu: `bai_bao` Bài báo, `do_an` Đồ án, `luan_van` Luận văn, `luan_an` Luận án, `hoc_lieu` Học liệu.
Trạng thái liên kết: `DaNoiTuDong` Đã nối tự động, `ChoXacNhan` Chờ xác nhận, `DaXacNhan` Đã xác nhận, `DaBacBo` Đã bác bỏ.
Trạng thái nhóm trùng: `NghiTrung` Nghi trùng, `DaGop` Đã gộp, `GiuRieng` Giữ riêng.

## Dữ liệu mẫu

`lib/fixtures.ts` chứa dữ liệu mẫu tiếng Việt thực tế (tiêu đề đồ án ICTU kiểu "Xây dựng website
quản lý thư viện trường THPT…", tên giảng viên kiểu "TS. Nguyễn Văn A") cho mọi endpoint; khi
`NEXT_PUBLIC_MOCK=1` client trả fixture thay vì gọi mạng (dùng cho Playwright và xem giao diện
khi backend chưa chạy). Backend thật đang chạy ở `http://localhost:8001` (có thể chưa lên khi bạn
bắt đầu — đừng chặn vì nó).
