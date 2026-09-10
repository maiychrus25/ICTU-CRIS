# Giao diện hàng đợi xác nhận và tra cứu — Kế hoạch triển khai

Lát cắt tiếp theo sau S + N. Lát cắt N đã chạy đủ ở tầng nghiệp vụ (`decide_link`,
`decide_group` đã có, đã test), nhưng **không có cách nào thao tác ngoài dòng lệnh**.
Hàng đợi xác nhận là nơi con người ra quyết định — theo BR-07, BR-10, BR-18 thì đây
là điểm mà toàn bộ thiết kế dựa vào. Không có giao diện thì lát cắt N chưa dùng được.

Phạm vi: SC-07 (nghi trùng), SC-08 (liên kết tác giả), SC-10 (chất lượng dữ liệu),
SC-11 (tra cứu), SC-12 (hồ sơ công bố giảng viên).

## Global Constraints

1. **Không thêm thư viện chạy.** Dự án giữ đúng một dependency runtime (`psycopg`).
   Web viết bằng **WSGI thuần stdlib** (`wsgiref`). Thêm framework sẽ buộc phải rà
   giấy phép và sửa `DEPENDENCIES.md` — ngoài phạm vi kế hoạch này.
2. **Không sửa tầng nghiệp vụ.** `cris/link.py`, `cris/dedup.py`, `cris/normalize.py`,
   `cris/people.py`, `cris/sync.py` giữ nguyên. Web chỉ gọi vào chúng. Nếu thấy cần
   sửa, dừng lại và ghi vào phần "Phát hiện", không tự sửa.
3. **Mọi quyết định phải ghi `actor_id`.** `decide_link` và `decide_group` đã nhận
   tham số này; web phải truyền người dùng thật, không truyền `None`.
4. **Không tự động hoá quyết định.** Không có route nào gộp bản ghi hay xác nhận liên
   kết mà không có thao tác người (BR-18). Thao tác hàng loạt vẫn là người bấm.
5. **Escape mọi giá trị đưa vào HTML.** Dữ liệu là tên người thật và tiêu đề từ nguồn
   ngoài. Dùng `html.escape(..., quote=True)` cho mọi nội suy, không ngoại lệ.
6. **Ghi–đọc tách bạch.** `GET` không đổi dữ liệu. Mọi thay đổi qua `POST`, sau đó
   `303 See Other` về trang danh sách (post/redirect/get).
7. **Test không được dựng server.** Gọi thẳng WSGI callable với `environ` giả. Test
   chạm DB dùng fixture `conn` sẵn có trong `tests/conftest.py`.
8. **Header SPDX** trên mọi tệp `.py` mới, đúng dạng `tests/test_spdx.py` quét.
9. **Tiếng Việt có dấu** trong nhãn giao diện; mã và tên biến tiếng Anh, khớp phần
   còn lại của `cris/`.
10. **Thông điệp commit tiếng Anh**, conventional-commit, **không có trailer**
    `Co-Authored-By` hay bất kỳ dòng ghi công AI nào.

## Cấu trúc tệp

```
cris/web/__init__.py         # rỗng, header SPDX
cris/web/wsgi.py             # router, Request/Response, chạy app
cris/web/render.py           # escape, layout, thành phần HTML dùng chung
cris/web/views_queue.py      # SC-07, SC-08 — hàng đợi
cris/web/views_search.py     # SC-11, SC-12 — tra cứu, hồ sơ giảng viên
cris/web/views_quality.py    # SC-10 — chất lượng dữ liệu
cris/web/static.py           # CSS nhúng (một chuỗi, không tệp rời)
tests/test_web_wsgi.py
tests/test_web_queue.py
tests/test_web_search.py
tests/test_web_quality.py
```

Đăng ký route bằng decorator trong từng `views_*.py`; `wsgi.py` chỉ import các module
đó. Như vậy ba nhóm màn hình không tranh nhau sửa cùng một bảng route.

---

### Task 1: Khung web WSGI, router, render, `cris serve`

**Chặn các task sau. Phải xong và xanh trước khi bắt đầu Task 2–4.**

Viết `cris/web/wsgi.py`:

- `ROUTES: list[tuple[str, str, callable]]` — (method, mẫu đường dẫn, handler).
- `@route(method, pattern)` decorator đẩy vào `ROUTES`. Mẫu hỗ trợ tham số kiểu
  `/tra-cuu/giang-vien/<int:pid>`; chỉ cần hai kiểu `int` và `str`.
- `class Request`: `method`, `path`, `query` (dict, `parse_qs` đã phẳng hoá lấy giá
  trị cuối), `form` (đọc `wsgi.input` theo `CONTENT_LENGTH`, giới hạn 1 MiB), `conn`,
  `actor_id`. Hỗ trợ nhiều giá trị cùng tên cho thao tác hàng loạt: `req.form_list(k)`.
- `def app(environ, start_response)` — WSGI callable. Khớp route, gọi handler, handler
  trả về `str` (HTML 200), hoặc `(status, headers, body)`, hoặc `Redirect(path)`.
- `404` và `405` trả trang lỗi có layout. Ngoại lệ chưa bắt → `500`, ghi traceback ra
  `stderr`, thân trang **không** lộ traceback.
- Kết nối DB: một `psycopg.connect` cho mỗi request, đóng ở `finally`.
- `actor_id`: lấy từ header `X-CRIS-User` (id số) nếu có, nếu không thì người dùng
  `app_user` đầu tiên có vai trò `rd_officer`. Nếu không có ai → `503` kèm câu tiếng
  Việt chỉ cách tạo. Đăng nhập thật là NFR-01, ngoài phạm vi kế hoạch này — ghi rõ
  giới hạn đó trong docstring của `wsgi.py`.

Viết `cris/web/render.py`:

- `e(x)` — `html.escape(str(x), quote=True)`, `None` thành `""`.
- `layout(title, body, active=None)` — khung trang: `<!doctype html>`, `lang="vi"`,
  `<meta charset>`, `<meta name="viewport">`, thanh điều hướng (Hàng đợi tác giả,
  Hàng đợi nghi trùng, Tra cứu, Chất lượng dữ liệu), CSS nhúng từ `static.py`.
- `table(headers, rows)`, `badge(text, kind)`, `pager(page, total, per, base_url)` —
  các thành phần dùng lại. `pager` sinh liên kết `?page=N`.
- Không dùng thư viện template. Nội suy bằng f-string, luôn qua `e()`.

Viết `cris/web/static.py`: một hằng `CSS` là chuỗi. Yêu cầu tối thiểu — đọc được trên
màn hình hẹp (UX-10: lãnh đạo khoa và giảng viên mở trên điện thoại), bảng cuộn ngang
trong khung riêng, vùng bấm ≥ 44 px, trạng thái focus thấy được.

Thêm `cris/web/__main__.py` và lệnh CLI:

- `python -m cris serve [--host 127.0.0.1] [--port 8000]` dùng
  `wsgiref.simple_server.make_server`. Thêm `serve` vào `cris/cli.py`.
- In ra địa chỉ và một dòng cảnh báo: đây là server phát triển, không dùng cho vận hành.

**Test `tests/test_web_wsgi.py`** (không cần DB cho phần định tuyến):

- `call(app, "GET", "/duong-dan")` helper dựng `environ` giả, trả `(status, headers, body)`.
- Route khớp đúng; tham số `<int:pid>` ép kiểu đúng.
- Đường dẫn không có → `404`, thân có layout, không có traceback.
- Method sai → `405`.
- Handler ném lỗi → `500`, traceback **không** nằm trong thân trang.
- `Redirect` sinh `303` và header `Location`.
- `e()` chặn `<script>`, dấu nháy kép, và `None`.
- `form_list` trả nhiều giá trị cùng tên.

**Nghiệm thu Task 1:** `pytest -q` xanh toàn bộ (99 test cũ + test mới).
`python -m cris serve` chạy được, `curl localhost:8000/` trả 200.

---

### Task 2: Hàng đợi liên kết tác giả (SC-08)

Phụ thuộc Task 1. Tệp `cris/web/views_queue.py` (phần tác giả) và `tests/test_web_queue.py`.

Route:

| Method | Đường dẫn | Việc |
|---|---|---|
| GET | `/doi-soat/tac-gia` | Danh sách lượt tên chờ xác nhận |
| POST | `/doi-soat/tac-gia/quyet-dinh` | Gọi `link.decide_link` cho một hoặc nhiều liên kết |

`GET` hiển thị, mỗi dòng: tên thô trong bản ghi (`author_mention.raw_name`), tiêu đề
công trình, ứng viên đề xuất kèm **độ tin cậy và căn cứ** (`orcid` /
`ten_day_du_duy_nhat` / …), và cảnh báo mâu thuẫn học vị nếu tầng nghiệp vụ đã gắn.
Sắp theo số công trình bị ảnh hưởng giảm dần — màn này tác động lớn nhất tới chất
lượng số liệu nên việc nặng phải lên đầu.

Bộ lọc trên query string: `?state=` (mặc định trạng thái chờ), `?q=` (lọc theo tên thô),
`?page=`. Phân trang 50 dòng.

`POST` nhận `link_id` (nhiều giá trị), `decision` (`confirm` | `reject` | `reassign`),
`person_id` (khi `reassign`), `reason`. Gọi `link.decide_link(conn, link_id, decision,
actor_id, reason=…, person_id=…)` cho từng id **trong một transaction**; một id lỗi thì
cả lô không đổi gì, và trang danh sách hiện thông báo nêu id nào hỏng.

Ràng buộc giao diện:

- **Xử lý hàng loạt cho cùng một chuỗi tên** (UX-08): nhóm các lượt cùng `raw_name`,
  có ô chọn cả nhóm.
- `reject` bắt buộc có `reason` — form không cho gửi rỗng, và server kiểm lại.
- Sau `POST` → `303` về `/doi-soat/tac-gia` giữ nguyên bộ lọc đang xem.

**Test** (dùng fixture `conn`, `user_id`): dựng dữ liệu bằng chính hàm của tầng nghiệp
vụ, không `INSERT` tay khi có hàm sẵn.

- Trang rỗng có câu trạng thái rỗng, không lỗi.
- Một liên kết chờ hiện đúng tên thô, ứng viên, độ tin cậy.
- `confirm` một liên kết → trạng thái đổi thành `DaXacNhan`, `actor_id` được ghi.
- `reject` không lý do → không đổi gì, trang hiện lỗi.
- `reject` có lý do → `DaBacBo`, lý do lưu lại.
- Chọn nhiều id → cả lô đổi trạng thái.
- Một id sai trong lô → **không** id nào đổi (kiểm lại trong DB).
- Tên có `<script>` trong `raw_name` → thân trang không chứa thẻ script sống.

---

### Task 3: Hàng đợi nghi trùng (SC-07)

Phụ thuộc Task 1. Chạy song song được với Task 2. Tệp `cris/web/views_dedup.py` và
`tests/test_web_dedup.py`.

Route:

| Method | Đường dẫn | Việc |
|---|---|---|
| GET | `/doi-soat/trung-lap` | Danh sách nhóm nghi trùng, sắp theo độ tin cậy |
| GET | `/doi-soat/trung-lap/<int:gid>` | So sánh cạnh nhau từng trường |
| POST | `/doi-soat/trung-lap/<int:gid>/quyet-dinh` | Gọi `dedup.decide_group` |

Trang chi tiết là phần khó: hiện **từng trường cạnh nhau cho mọi thành viên nhóm**, tô
đậm chỗ khác nhau (`dedup._diff` đã tính sẵn — đọc nó, đừng tính lại). Khi gộp, người
dùng chọn giá trị giữ lại cho **từng trường mâu thuẫn** (BR-10: hệ thống không tự quyết
giá trị nào đúng) và chọn bản sống sót.

Ràng buộc giao diện — quan trọng nhất của task này:

- Nhóm mà các thành viên **khác sinh viên** (đồ án nhóm) phải hiện cảnh báo
  *"nhiều khả năng là đồ án nhóm"* và **mặc định đề xuất Giữ riêng** (BR-08). Đo
  09/2026: 34 trên 43 nhóm đồ án trùng tiêu đề là đồ án nhóm — gộp theo tiêu đề sẽ
  xoá 52 bản ghi thật.
- `GiuRieng` bắt buộc có `reason`.
- Nhóm ghép theo DOI xếp trên nhóm ghép theo tiêu đề.

**Test**:

- Danh sách sắp DOI trước tiêu đề.
- Trang chi tiết hiện đủ số thành viên và đánh dấu đúng trường khác nhau.
- Gộp với `field_choices` → giá trị chọn được giữ, bản gốc vẫn còn (BR-09).
- Nhóm khác sinh viên → thân trang có cảnh báo đồ án nhóm và nút mặc định là Giữ riêng.
- `GiuRieng` không lý do → không đổi gì.
- `gid` không tồn tại → `404`.

---

### Task 4: Tra cứu, hồ sơ giảng viên, chất lượng dữ liệu (SC-10, SC-11, SC-12)

Phụ thuộc Task 1. Chạy song song được với Task 2 và 3. Tệp `cris/web/views_search.py`,
`cris/web/views_quality.py`, `tests/test_web_search.py`, `tests/test_web_quality.py`.

Route:

| Method | Đường dẫn | Việc |
|---|---|---|
| GET | `/` | Chuyển hướng `303` sang `/tra-cuu` |
| GET | `/tra-cuu` | Tìm công trình |
| GET | `/tra-cuu/cong-trinh/<int:wid>` | Chi tiết công trình |
| GET | `/tra-cuu/giang-vien/<int:pid>` | Hồ sơ công bố giảng viên |
| GET | `/chat-luong-du-lieu` | Báo cáo chất lượng dữ liệu |

`/tra-cuu`: ô tìm `?q=` khớp tiêu đề và tên tác giả; lọc `?doc_type=`, `?year=`,
`?unit=`; phân trang 50. Đọc từ view `v_work_current` và `v_work_unit`, **không** tự
viết lại logic đã có trong view.

`/tra-cuu/cong-trinh/<wid>`: mỗi trường hiện **giá trị đang dùng, giá trị gốc và nguồn**
(bảng `field_provenance`) — đây là lời hứa trung tâm của sản phẩm (UX-09, NFR-24), không
được rút gọn. Kèm danh sách tác giả và trạng thái liên kết từng người.

`/tra-cuu/giang-vien/<pid>`: đọc `v_person_publications`. Hiện số đếm theo loại, phân
bố theo năm, danh sách công trình. **Bắt buộc** hiện thời điểm đồng bộ gần nhất và dòng
*"còn N công trình nghi thuộc người này chưa được xác nhận"* khi có (NFR-25) — hồ sơ
nguồn hiện chỉ phủ 8%, người đọc phải biết con số đang dựa trên cái gì.

`/chat-luong-du-lieu`: gọi `quality.report(conn)` và trình bày. Mỗi chỉ số bấm được,
dẫn sang hàng đợi tương ứng. Hiện cảnh báo lệch số lượng của lần đồng bộ gần nhất.

**Test**:

- Tìm theo tiêu đề và theo tên tác giả đều ra kết quả.
- Bộ lọc `doc_type` thu hẹp đúng.
- Trang công trình hiện đủ ba cột: giá trị dùng, giá trị gốc, nguồn.
- `wid` / `pid` không tồn tại → `404`.
- Hồ sơ giảng viên có dòng thời điểm đồng bộ và dòng "chưa xác nhận" khi có.
- `/chat-luong-du-lieu` hiện đúng số từ `quality.report`.
- `/` chuyển hướng `303` sang `/tra-cuu`.

---

### Task 5: Ráp lại, tài liệu, nghiệm thu

Sau khi Task 2–4 xong.

- `pytest -q` xanh toàn bộ. Ghi số test mới vào `CHANGELOG.md` và `README.md`
  (mục "Lát cắt S + N chạy từ dòng lệnh, N test" và bảng công nghệ).
- `CHANGELOG.md` mục `### Added`: mô tả lát cắt giao diện, nêu rõ **không thêm
  dependency**, và nêu giới hạn: chưa có đăng nhập thật (NFR-01 ngoài phạm vi).
- `README.md` lộ trình: `- [x] Giao diện hàng đợi xác nhận và tra cứu`.
- `BUILDING.md`: thêm mục chạy web (`python -m cris serve`).
- `docs/ba/08-sitemap.md`: đánh dấu đường dẫn nào đã có, đường dẫn nào chưa.

---

## Ngoài kế hoạch này

- Đăng nhập, phiên, phân quyền theo vai trò và phạm vi đơn vị (NFR-01, NFR-02). Bản này
  chạy với một người dùng mặc định; **không triển khai lên mạng công cộng**.
- Kỳ báo cáo, kê khai, phê duyệt (lát cắt K, D, R).
- Nhập Excel khoa (S-06) — còn chờ trả lời Q-05 về biểu mẫu khoa đang dùng.
- Đối chiếu đề tài (T-03..T-06).
- Bất kỳ thay đổi nào ở `cris/link.py`, `cris/dedup.py`, `cris/normalize.py`.

## Tự rà

Trước khi báo xong, tự kiểm:

1. `pytest -q` xanh, không có test nào bị `skip` để cho qua.
2. `grep -rn "Co-Authored" ` trong thông điệp commit → không có.
3. Mọi tệp `.py` mới có header SPDX (chạy `pytest tests/test_spdx.py`).
4. `pyproject.toml` **không** thêm dependency nào.
5. Không có tệp nào trong `cris/link.py`, `cris/dedup.py`, `cris/normalize.py`,
   `cris/people.py`, `cris/sync.py` bị sửa (`git diff --stat main` để kiểm).
6. Mọi giá trị nội suy vào HTML đều qua `e()`.
7. Không route `GET` nào ghi dữ liệu.
