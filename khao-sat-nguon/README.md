# Khảo sát kho ICTU — repository.ictu.edu.vn

Khảo sát kỹ thuật ngày 09–10/09/2026. Chỉ đọc, GET công khai, ~3 req/s.
`robots.txt` của site cho phép crawl toàn bộ (`User-agent: * / Disallow:` trống).

**Báo cáo đầy đủ:** mở `report.html` bằng trình duyệt.

---

## Site chạy gì

Không phải DSpace. Tên site đặt là "DSpace" nhưng thực chất là:

- WordPress 7.1 + theme GeneratePress (+ child theme) + Yoast SEO
- 6 custom post type học thuật do đơn vị tự viết
- Không có OAI-PMH, không REST API DSpace, không handle identifier
- Server-rendered PHP, không có AJAX endpoint, không nonce, không rate limit ghi nhận được

## Bề mặt API

| Đường dẫn | Tham số | Trả về |
|---|---|---|
| `/wp-json/wp/v2/media` | `per_page` `page` `_fields` | 5.644 tệp — JSON |
| `/wp-json/wp/v2/cam-nang-so` | `per_page` `_fields` | 6 hướng dẫn — JSON |
| `/{loại}/` | `?pg=N` | HTML, 20/trang (10 với luận văn & luận án) |
| `/bai-bao/` | `?dept=` `?type=` | lọc — hoạt động |
| `/do-an/` `/luan-van/` `/luan-an/` | `?cohort=` | lọc theo khoá — hoạt động |
| `/tim-kiem/` | `?q=` `?pg=` | tìm toàn văn, tách theo loại tài liệu |

6 CPT học thuật đều đăng ký `show_in_rest = false`, nên `wp-json` **không** trả về
tài liệu học thuật. Toàn bộ phải đọc từ HTML.

## Dữ liệu đã trích xuất — 8.034 bản ghi

| Loại | Đường dẫn | Số bản ghi |
|---|---|---|
| Đồ án tốt nghiệp | `/do-an/` | 5.375 |
| Bài báo khoa học | `/bai-bao/` | 1.907 |
| Giảng viên | `/giang-vien/` | 410 |
| Luận văn thạc sĩ | `/luan-van/` | 323 |
| Luận án tiến sĩ | `/luan-an/` | 11 |
| Cẩm nang số | `/cam-nang-so/` | 6 |
| Học liệu số | `/hoc-lieu-so/` | 2 |

Ngoài ra 5.644 tệp đính kèm, phần lớn là PDF toàn văn để công khai không chặn
(mẫu 40 bản ghi: 98% đồ án và 92% luận văn có PDF tải trực tiếp).

## 10 phát hiện

### Nghiêm trọng

1. **4.621 đồ án ghi GVHD là `ICTU_TEACHER`** — 86% cả kho, hiển thị công khai trên
   trang chi tiết. Kèm 302 bản ghi `ICTU_STUDENT`, và cả 11 luận án ghi GVHD là `ICTU`.
   Dữ liệu chưa ánh xạ khi nhập, không phải lỗi hiển thị.
   *Sửa:* khôi phục từ nguồn nhập gốc; trong lúc chờ thì ẩn dòng khi giá trị khớp placeholder.

2. **Phân trang làm 11 đồ án không bao giờ duyệt tới được** — trang 27 và 28 của
   `/do-an/` trùng đúng 11 mục dù STT đánh liên tục 521–540 rồi 541–560.
   Duyệt hết 269 trang chỉ ra 5.364/5.375 bản ghi phân biệt.
   *Sửa:* truy vấn sắp xếp theo cột không duy nhất → `LIMIT/OFFSET` không ổn định.
   Thêm khoá phụ: `orderby => ['meta_value' => 'DESC', 'ID' => 'DESC']`.
   Danh sách 11 URL: `out/_doan_unreachable.json` (đã thu hồi và gộp vào dataset).

3. **Bộ lọc "Năm XB" hỏng 100%** — form gửi tham số tên `year`, trùng query var dành
   riêng của WordPress → `301` sang `/2025/` → `404`. Chọn năm nào cũng ra 404.
   *Sửa:* đổi tên sang `nam_xb` (đã thử, không bị chuyển hướng).

### Cao

4. **Trường "Loại bài" là ô free-text với 48 giá trị** cho 1.907 bài báo, nhồi 2 chiều
   độc lập vào 1 ô: nguồn chỉ mục (Scopus/WoS/DOAJ/kỷ yếu) và điểm HĐGS (0,5/0,75/1,0).
   Lỗi gõ: `KYHTGQ` (đảo chữ), `KYHTQT.` (thừa dấu chấm), 5 cách viết cho "0,5 điểm".
   *Sửa:* tách 3 trường. `normalize.py` đã gom về 7 chỉ mục + 4 loại nơi công bố + 3 mức
   điểm, chỉ còn 15,2% cần rà tay (mà 285/290 vốn đã là "Chưa xác định" ở nguồn).

5. **Liên kết giảng viên đứt** — chỉ 13% đồ án và 67% luận văn nối được tới hồ sơ
   giảng viên. Trừ nhóm placeholder ở mục 1, số tên thật chưa nối chỉ còn 34 bản ghi
   trên 21 tên.
   *Sửa:* chuẩn hoá khoá đối sánh (bỏ dấu, hạ chữ thường, cắt tiền tố `TS`/`ThS`/`PGS.TS`)
   khớp được `"T.s Nguyễn Văn Tảo"`, `"Ths. Nông Thị Hoa"`. Một bản ghi có 2 người trong
   cùng ô (`"Phạm Thanh Giang, Trần Duy Minh"`) cần tách trước. Chi tiết: `out/_gvhd_linkage.json`.

### Trung bình

6. **Cột "Từ khoá" của bài báo trống 99%** — chỉ 14/1.907 bài có dữ liệu, trong khi
   đồ án và luận văn đều phủ 100%.

7. **`/giang-vien/` tải 935 KB một lần** — render cả 410 hồ sơ rồi lọc client-side.
   Các trang danh mục khác chỉ 50–88 KB.

8. **Nhãn phân loại sinh hex CSS không hợp lệ** — ghép mã màu với 2 ký tự alpha, chỉ
   đúng với hex 6 ký tự. Rơi vào màu mặc định `#555` thì ra hex 5 ký tự:
   `style="background:#55518;color:#555;border-color:#55540;"` → trình duyệt bỏ qua.

9. **`/wp-json/wp/v2/users` lộ username admin** — trả về `{"id":1,"name":"hvninh",
   "url":"http://localhost/repository"}`. Nửa đầu của cặp thông tin đăng nhập, kèm
   đường dẫn localhost sót từ lúc phát triển.

10. **Ô tìm kiếm trong danh mục mất ngữ cảnh loại tài liệu** — đặt tên `s`, cũng là
    query var dành riêng của WP (cùng nguyên nhân với mục 3). `/bai-bao/?s=UML` →
    `302 /tim-kiem/?q=UML` → trả cả đồ án lẫn luận văn. Trang tìm kiếm chung cũng
    bỏ qua tham số `type`.

---

## Công cụ

Chỉ dùng thư viện chuẩn Python, không cần cài thêm.

```bash
python3 harvest.py archives          # kéo toàn bộ 6 loại  -> out/*.jsonl  (~4 phút)
python3 harvest.py archives bai-bao  # kéo 1 loại
python3 harvest.py details do-an 50  # kéo trang chi tiết, giới hạn 50
python3 harvest.py csv               # xuất CSV từ jsonl
python3 normalize.py                 # chuẩn hoá trường "Loại bài"
python3 summary.py                   # thống kê nhanh
```

`harvest.py` có 3 bộ parser cho 3 kiểu markup khác nhau trên site: bảng
(`bb-table` của bài báo), thẻ (`lv-card` của đồ án/luận văn/luận án/học liệu),
và microdata (`gv-card` của giảng viên). Giãn cách 0,35 s mỗi yêu cầu.

## Tệp dữ liệu

| Tệp | Nội dung |
|---|---|
| `out/*.jsonl` | 8.034 bản ghi, một dòng JSON mỗi bản ghi, giữ nguyên tiếng Việt có dấu |
| `out/*.csv` | cùng dữ liệu, đã làm phẳng, UTF-8 BOM để mở thẳng bằng Excel |
| `out/bai-bao.normalized.jsonl` | bài báo kèm trường `pub_type_norm` đã chuẩn hoá |
| `out/_doan_unreachable.json` | 11 URL đồ án bị phân trang bỏ sót |
| `out/_doan_duplicates.json` | 11 URL bị render lặp ở trang 28 |
| `out/_gvhd_linkage.json` | 21 tên GVHD chưa nối được, kèm số bản ghi mỗi tên |

---

## Kiểm chứng giả định của đề tài

Xem `kiem-chung-gia-dinh-de-tai.md` — đối chiếu từng giả định trong hai tài liệu đề tài
(tổng quan dịch vụ + phân tích quy trình) với số đo thực tế trên dữ liệu đã kéo.

Kết luận chính:

- Kho **không có toàn văn**. 39/40 PDF là tóm tắt 1 trang do ReportLab sinh.
- Liên kết tác giả hiện chỉ phủ **8%** bài báo; chuẩn hoá tên đưa lên **86%**.
- Trường đơn vị là **đơn trị** — 0 bài thuộc >1 khoa; 37% bài không có khoa.
- 34/43 nhóm đồ án trùng tiêu đề là **đồ án nhóm**, không được gộp.
- **ORCID phủ 91%** hồ sơ giảng viên — khoá nối tác giả tốt nhất đang có, tài liệu chưa nhắc.
