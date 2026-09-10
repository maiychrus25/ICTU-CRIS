# ĐẶC TẢ YÊU CẦU PHẦN MỀM (SRS) — ICTU-CRIS

Bản 1.0, ngày 10/09/2026. Tài liệu cấp trên: [BRD.md](BRD.md). Tài liệu chi tiết: [ba/](ba/00-README.md).

## 1. Giới thiệu

### 1.1 Mục đích

Đặc tả những gì ICTU-CRIS phải làm để đáp ứng mười yêu cầu nghiệp vụ `YN-01..10` trong BRD, ở mức đủ để lập trình và kiểm thử. Mỗi yêu cầu chức năng ở đây truy vết được về một `YN`, về use case và user story trong bộ BA, và về quy tắc `BR` mà nó thực thi (mục 9).

### 1.2 Phạm vi

Bản dự thi v0.1: đồng bộ (S), chuẩn hoá và đối soát (N), giao diện hàng đợi và tra cứu (Q, T), tích hợp AI (AI), lược đồ kỳ báo cáo (K, một phần), dòng lệnh (C). Những gì ngoài phạm vi ghi ở BRD §5.2.

### 1.3 Định nghĩa

| Thuật ngữ | Nghĩa trong tài liệu này |
|---|---|
| Kho nguồn | `repository.ictu.edu.vn`, WordPress với 6 kiểu bài viết tự viết |
| Bản ghi thô (`source_record`) | Một bản ghi kéo về, giữ nguyên nội dung, có phiên bản và băm nội dung |
| Công trình (`work`) | Thực thể sau chuẩn hoá; nhiều bản ghi thô có thể trỏ về một công trình sau khi gộp |
| Lượt tên (`author_mention`) | Một chuỗi tên tác giả xuất hiện trong một công trình, đúng như nguồn ghi |
| Người (`person`) | Giảng viên hoặc sinh viên, có định danh; nhiều lượt tên nối về một người |
| Liên kết (`author_link`) | Cặp (lượt tên, người) kèm độ tin cậy và trạng thái |
| Xuất xứ (`field_provenance`) | Với mỗi trường của công trình: giá trị gốc, giá trị đang dùng, đến từ đâu, ai đổi |
| Nhóm nghi trùng (`duplicate_group`) | Tập công trình có thể là một; có căn cứ ghép và gợi ý |
| Hàng đợi | Danh sách ca cần người quyết: liên kết mơ hồ, nhóm nghi trùng |
| Nhà cung cấp AI (`provider`) | `none` · `local` (mô hình cục bộ) · tên dịch vụ ngoài; cấu hình, không nhúng mã |
| Tóm tắt | Trường `abstract` của công trình; kho **không có toàn văn** |

### 1.4 Tài liệu tham chiếu

- Thể lệ cuộc thi "Phát triển phần mềm mã nguồn mở tích hợp AI 2026" (Khoa CNTT, ICTU) — bản PDF giữ ở máy, không đưa vào repo.
- Bộ BA: [chức năng](ba/04-functions.md), [use case](ba/11-usecase-spec.md), [user story](ba/13-user-stories.md), [NFR](ba/14-nfr.md), [quy tắc và câu hỏi mở](ba/15-project-rules.md), [mô hình dữ liệu](ba/17-mo-hinh-du-lieu.md).
- Khảo sát nguồn: [README](../khao-sat-nguon/README.md), [kiểm chứng giả định](../khao-sat-nguon/kiem-chung-gia-dinh-de-tai.md).

## 2. Mô tả tổng thể

### 2.1 Bối cảnh

Đường ống dữ liệu, mỗi bước ghi qua PostgreSQL và có thể chạy lại:

```
kho ICTU ──S──▶ source_record ──N──▶ work + field_provenance + author_mention
                                        │
                                        ├──▶ person ◀── hồ sơ giảng viên
                                        ├──▶ author_link  ──▶ hàng đợi tác giả ──▶ người quyết
                                        ├──▶ duplicate_group ──▶ hàng đợi nghi trùng ──▶ người quyết
                                        └──▶ v_data_quality
                                                │
                              ┌─────────────────┴──────────────────┐
                           tra cứu / hồ sơ giảng viên          AI: vector tóm tắt ──▶ đối chiếu đề tài
                                                                    gợi ý xếp hạng ──▶ hai hàng đợi
```

Tầng nghiệp vụ (`cris/*.py`, 978 dòng) không biết gì về web. Tầng web (`cris/web/`, 1.529 dòng) chỉ gọi vào nó. Tầng AI (`cris/ai/`, lát cắt tới) cũng chỉ gọi vào tầng nghiệp vụ và **không bao giờ** ghi trực tiếp vào `work`, `author_link` hay `duplicate_group` — nó chỉ ghi vào bảng gợi ý của riêng mình.

### 2.2 Người dùng

Theo BA [05-permissions.md](ba/05-permissions.md): `rd_officer` (Phòng KH-CN), `faculty_officer` (Văn phòng khoa), `faculty_head`, `lecturer`, `student`, `admin`. Bản dự thi chạy với một người dùng mặc định có vai trò `rd_officer`; header `X-CRIS-User` cho phép thử vai khác. Đăng nhập thật là NFR-01, ngoài phạm vi.

### 2.3 Ràng buộc chung

- Python ≥ 3.12, PostgreSQL 16. Một thư viện chạy: `psycopg`. Lát cắt AI thêm thư viện theo mục 8.3 và phải ghi vào `DEPENDENCIES.md` trước khi commit.
- Không ghi đè giá trị gốc. Không xoá bản ghi. Mọi thay đổi trạng thái ghi `audit_log` với `actor_id`.
- Web: WSGI stdlib, server-render, `POST → 303 → GET`, escape mọi nội suy.
- Test chạy trên PostgreSQL thật, không mock cơ sở dữ liệu; hiện 152 test.

## 3. Yêu cầu chức năng

Mã `FR-<giai đoạn>-<số>` trùng với mã chức năng trong [ba/04-functions.md](ba/04-functions.md) để một mã dùng xuyên suốt. Cột **Trạng thái**: ✅ có và có test · ◐ có một phần · ⏳ chưa.

### 3.1 Đồng bộ (FR-S)

| Mã | Yêu cầu | Trạng thái |
|---|---|---|
| FR-S-01 | Kéo 6 loại nội dung từ kho: bài báo, đồ án, luận văn, luận án, học liệu số, giảng viên | ✅ |
| FR-S-02 | Đọc trang chi tiết từng công trình để lấy đủ danh sách tác giả — trang danh mục cắt cụt 17 % bài báo | ✅ |
| FR-S-03 | Sau mỗi lần đồng bộ, so số bản ghi lấy được với số kho tự công bố; lệch thì `sync_run.status='warning'` kèm chi tiết | ✅ |
| FR-S-04 | Khi lật trang xong mà vẫn thiếu, quét bù theo bộ lọc (`?cohort=`, `?dept=`), giải mã thực thể HTML trước khi mã hoá URL | ✅ |
| FR-S-05 | Lưu bản ghi thô theo phiên bản: nội dung đổi thì tăng `version`, giữ bản cũ; bản ghi biến mất ở nguồn đánh dấu `vanished`, không xoá | ✅ |
| FR-S-06 | Nhập công trình từ tệp Excel khoa | ⏳ chờ Q-05 |
| FR-S-07 | Siêu dữ liệu tìm thấy (`_page`, `_backfill`) không tính vào băm nội dung — số trang trôi giữa các lần chạy vì kho sắp xếp không ổn định | ✅ |

### 3.2 Chuẩn hoá và đối soát (FR-N)

| Mã | Yêu cầu | Trạng thái |
|---|---|---|
| FR-N-01 | Chuẩn hoá tên người: bỏ dấu, hạ chữ, cắt tiền tố học hàm/vị, xử lý dạng đảo họ-tên có gạch nối; giữ `raw_name` | ✅ |
| FR-N-02 | Nối tác giả theo ORCID khi cả hai phía có; độ tin cậy `orcid` | ✅ |
| FR-N-03 | Nối theo tên chuẩn hoá: khớp duy nhất → tự nối (`DaNoiTuDong`); khớp nhiều hoặc một phần → hàng đợi (`ChoXacNhan`) | ✅ |
| FR-N-04 | Người xác nhận / bác bỏ / gán lại trên hàng đợi; bác bỏ bắt buộc lý do; lô nhiều id trong một transaction | ✅ |
| FR-N-05 | Cặp đã bác bỏ không bao giờ được đề xuất lại | ✅ |
| FR-N-06 | Cùng một người ghi hai học vị khác nhau → `degree_conflict`, không tự nối | ✅ |
| FR-N-07 | Nghi trùng theo DOI (tin cậy cao nhất) | ✅ |
| FR-N-08 | Nghi trùng theo tiêu đề chuẩn hoá; với đồ án, khoá là tiêu đề + sinh viên + khoá | ✅ |
| FR-N-09 | Gộp: người chọn bản sống sót và giá trị giữ lại cho từng trường mâu thuẫn; bản gốc và xuất xứ giữ nguyên | ✅ |
| FR-N-10 | Nhóm khác sinh viên mang `hint` "đồ án nhóm", giao diện mặc định Giữ riêng | ✅ |
| FR-N-11 | Tách "loại bài" văn bản tự do thành chỉ mục, loại nơi công bố, điểm; không suy được thì gắn cờ, không đoán | ✅ |
| FR-N-12 | Gom biến thể tên đơn vị về một mã (`unit.aliases`) | ✅ |
| FR-N-13 | Suy đơn vị của công trình từ tác giả đã nối (`v_work_unit`) | ✅ |
| FR-N-14 | Gom cụm từ khoá thành trục chủ đề | ⏳ → FR-AI-05 |
| FR-N-15 | Báo cáo chất lượng dữ liệu: độ phủ, số chờ nối, số chưa có đơn vị, số nghi trùng mở, lần đồng bộ gần nhất | ✅ |
| FR-N-16 | Mọi trường sau chuẩn hoá có dòng `field_provenance` (giá trị gốc, giá trị dùng, `set_kind`, ai, khi nào); chuẩn hoá lại giữ giá trị sửa tay | ✅ |

### 3.3 Giao diện hàng đợi và tra cứu (FR-Q, FR-T)

| Mã | Yêu cầu | Trạng thái |
|---|---|---|
| FR-Q-01 | Hàng đợi liên kết tác giả: nhóm theo tên thô, sắp theo số công trình bị ảnh hưởng, lọc theo trạng thái và tên, chọn cả nhóm | ✅ |
| FR-Q-02 | Hàng đợi nghi trùng: DOI trước tiêu đề; trang chi tiết so từng trường cạnh nhau cho mọi thành viên, tô đậm chỗ khác | ✅ |
| FR-Q-03 | Mọi quyết định đi qua `decide_link` / `decide_group` với `actor_id` thật; `GET` không ghi dữ liệu | ✅ |
| FR-T-01 | Tìm công trình theo tiêu đề và tên tác giả; lọc loại, năm, đơn vị; phân trang | ✅ |
| FR-T-02 | Hồ sơ công bố giảng viên: số đếm theo loại, phân bố theo năm, thời điểm đồng bộ gần nhất, số công trình chưa xác nhận | ✅ |
| FR-T-03 | Chi tiết công trình hiện đủ ba cột cho mỗi trường: giá trị đang dùng, giá trị gốc, nguồn | ✅ |
| FR-T-04 | Trang chất lượng dữ liệu: mỗi chỉ số bấm được dẫn sang hàng đợi tương ứng | ✅ |
| FR-T-05 | Nhập đề tài dự kiến và nhận bảng đối chiếu | ⏳ → FR-AI-02..04 |

### 3.4 Tích hợp AI (FR-AI)

Nguyên tắc: AI **chỉ ghi vào bảng gợi ý của nó** (`ai_embedding`, `ai_suggestion`, `ai_topic`), không bao giờ ghi vào `work`, `author_link`, `duplicate_group`. Người dùng thấy gợi ý trên giao diện đã có và bấm quyết định qua đúng luồng FR-Q-03.

| Mã | Yêu cầu | Trạng thái |
|---|---|---|
| FR-AI-01 | **Nhà cung cấp cấu hình được:** `CRIS_AI_PROVIDER=none\|local\|<tên dịch vụ>`. `none` là mặc định an toàn: mọi FR khác vẫn chạy, các chỗ gợi ý hiện "AI chưa bật". `local` dùng mô hình embedding đa ngữ tải công khai, chạy CPU. Dịch vụ ngoài chỉ dùng cho FR-AI-04 (sinh lời giải thích) và phải có đường lui | ⏳ |
| FR-AI-02 | **Vector ngữ nghĩa:** sinh embedding cho tiêu đề + tóm tắt + từ khoá của mọi công trình có tóm tắt (5.709 đồ án/luận văn/luận án và bài báo có tóm tắt), lưu `ai_embedding(work_id, model, dim, vector, built_at)`; chạy lại chỉ tính phần thiếu hoặc đổi | ⏳ |
| FR-AI-03 | **Đối chiếu đề tài:** người dùng nhập tên đề tài, vấn đề, đối tượng, phương pháp, dữ liệu dự kiến; hệ thống trả về k công trình gần nhất theo cosine trên `ai_embedding`, kèm điểm và loại tài liệu. Với `provider=none`, đường lui là khớp từ khoá chuẩn hoá (đã có trong khảo sát) và nói rõ đang dùng đường lui | ⏳ |
| FR-AI-04 | **Bảng so sánh theo khía cạnh** cho mỗi công trình trả về: bài toán · đối tượng · phạm vi · phương pháp, mỗi ô là *giống* / *khác* / *chưa đủ thông tin*. Với `local`: so sánh từng khía cạnh bằng embedding của câu mô tả khía cạnh với các câu trong tóm tắt, ngưỡng cấu hình. Với dịch vụ ngoài: thêm một đoạn giải thích ngôn ngữ tự nhiên, **luôn kèm** nhãn "do AI sinh, cần kiểm". **Không** hiện điểm phần trăm tương đồng tổng hợp; **luôn** hiện "so trên tiêu đề, tóm tắt và từ khoá — không phải toàn văn" | ⏳ |
| FR-AI-05 | **Gom cụm từ khoá:** embedding cho 10.951 từ khoá phân biệt, gom cụm (số cụm cấu hình), mỗi cụm có nhãn là từ khoá tần suất cao nhất; lưu `ai_topic`; dùng làm bộ lọc chủ đề ở FR-T-01 và làm một khía cạnh ở FR-AI-04 | ⏳ |
| FR-AI-06 | **Gợi ý cho hàng đợi tác giả:** với liên kết `ChoXacNhan` có nhiều ứng viên, xếp hạng ứng viên theo tương đồng giữa vector của công trình và vector các công trình đã xác nhận của từng ứng viên; hiện thứ hạng và lý do ("3 công trình đã xác nhận của người này cùng chủ đề"); người vẫn bấm quyết định | ⏳ |
| FR-AI-07 | **Gợi ý cho hàng đợi nghi trùng:** với nhóm ghép theo tiêu đề, hiện tương đồng tóm tắt giữa các thành viên như một cột thêm trong bảng so sánh; không đổi gợi ý mặc định của FR-N-10 | ⏳ |
| FR-AI-08 | **Minh bạch:** trang `/ve` và tài liệu kỹ thuật ghi rõ mô hình, phiên bản, giấy phép, kích thước, dữ liệu huấn luyện nếu công bố, và giới hạn (chỉ tóm tắt, tiếng Việt lẫn tiếng Anh) | ⏳ |
| FR-AI-09 | **Dòng lệnh:** `python -m cris ai embed\|topics\|suggest` chạy được độc lập, in tiến độ, chạy lại an toàn | ⏳ |

### 3.5 Kỳ báo cáo (FR-K) — một phần

| Mã | Yêu cầu | Trạng thái |
|---|---|---|
| FR-K-01 | Lược đồ `period`, `declaration` (duy nhất theo kỳ + công trình + đơn vị), `evidence`, `declaration_event` | ✅ |
| FR-K-02 | Mở kỳ gắn bộ quy tắc đang hoạt động tại thời điểm mở; đóng nộp; huỷ; mọi chuyển trạng thái ghi `audit_log` | ✅ |
| FR-K-03 | Tiến độ theo đơn vị cho một kỳ | ✅ |
| FR-K-04..09 | Gợi ý theo khoa, lập hồ sơ, minh chứng, kiểm tra hai mức, giao diện | ⏳ ngoài bản dự thi |

### 3.6 Dòng lệnh (FR-C)

| Mã | Yêu cầu | Trạng thái |
|---|---|---|
| FR-C-01 | `python -m cris migrate\|seed\|sync\|people\|normalize\|link\|dedup\|quality\|serve` | ✅ |
| FR-C-02 | `python -m cris ai …` (FR-AI-09) và `period …` | ⏳ |

## 4. Giao diện ngoài

### 4.1 Người dùng

Web server-render tiếng Việt, đọc được trên màn hình hẹp, thao tác hàng loạt cho việc lặp lại. Mô tả từng màn ở [ba/07-screens.md](ba/07-screens.md); đường dẫn đã có đánh dấu ✅ ở [ba/08-sitemap.md](ba/08-sitemap.md). Lát cắt AI thêm `/doi-chieu` và `/doi-chieu/<id>` (SC-13, SC-14).

### 4.2 Phần mềm

| Đối tác | Giao thức | Ghi chú |
|---|---|---|
| Kho ICTU | HTTPS GET, HTML; `/wp-json/wp/v2/media` JSON | Chỉ đọc; ≤ 3 yêu cầu/giây; `User-Agent` có tên sản phẩm |
| PostgreSQL 16 | `psycopg` | Một kết nối mỗi request web |
| Mô hình embedding cục bộ | tệp mô hình tải một lần vào thư mục cấu hình | Giấy phép và nguồn ghi ở `DEPENDENCIES.md` |
| Dịch vụ AI ngoài (tuỳ chọn) | HTTPS, khoá qua biến môi trường | Chỉ FR-AI-04; không gửi dữ liệu cá nhân (email, điện thoại, ngày sinh) |

### 4.3 Truyền thông

Không có. Không gửi email, không webhook trong bản dự thi.

## 5. Mô hình dữ liệu và thuật toán

### 5.1 Lược đồ

Bản 0.1 có 14 bảng + 4 bảng lát cắt K + 4 view, mô tả đầy đủ ở [ba/17-mo-hinh-du-lieu.md](ba/17-mo-hinh-du-lieu.md). Lát cắt AI thêm:

| Bảng | Cột chính | Ghi chú |
|---|---|---|
| `ai_embedding` | `work_id`, `model`, `dim`, `vector` (`double precision[]` — không thêm extension), `text_hash`, `built_at` | Duy nhất `(work_id, model)`; `text_hash` để chạy lại chỉ tính phần đổi |
| `ai_topic` | `id`, `label`, `model`, `size`; `ai_topic_keyword(topic_id, keyword, weight)` | Cụm từ khoá |
| `ai_suggestion` | `id`, `kind` (`author_link` \| `duplicate` \| `topic_match`), `target_id`, `payload` jsonb, `model`, `built_at` | Gợi ý cho hàng đợi; giao diện đọc, người quyết qua luồng cũ |
| `ai_query` | `id`, `input` jsonb, `results` jsonb, `provider`, `created_by`, `created_at` | Lịch sử đối chiếu đề tài để xem lại và gửi giảng viên |

Không dùng `pgvector` trong bản dự thi để không thêm extension phải cài; tìm k gần nhất trên 5.709 vector 384 chiều bằng Python thuần trong dưới một giây, đủ cho NFR-14.

### 5.2 Thuật toán

- **Chuẩn hoá tên** và **khoá gộp**: `cris/rules.py`, dữ liệu `rule_set` v1, có test trên các ca đo được (39 người nhiều biến thể, 34 nhóm đồ án nhóm).
- **Đối chiếu đề tài (FR-AI-03/04):** `q = embed(tên + mô tả)`; `top_k = argmax cosine(q, E)`; khía cạnh: với mỗi khía cạnh `a` có mô tả người dùng nhập, `s_a = max cosine(embed(mô tả a), embed(câu_i))` trên các câu của tóm tắt; `giống` nếu `s_a ≥ θ_hi`, `khác` nếu `≤ θ_lo`, còn lại `chưa đủ thông tin`; `θ` là cấu hình, mặc định chọn trên tập 40 ca gán tay.
- **Gợi ý ứng viên (FR-AI-06):** điểm ứng viên = trung bình cosine giữa vector công trình đang xét và vector các công trình `DaXacNhan` của ứng viên; không có công trình xác nhận nào → không gợi ý, hiện lý do.
- **Gom cụm (FR-AI-05):** k-means trên embedding từ khoá, `k` mặc định 40, nhãn cụm = từ khoá có tần suất cao nhất trong cụm.

## 6. Yêu cầu phi chức năng

Đầy đủ ở [ba/14-nfr.md](ba/14-nfr.md) (NFR-01..37). Bổ sung cho lát cắt AI:

| Mã | Yêu cầu | Mức đạt |
|---|---|---|
| NFR-38 | Chạy không có mạng sau khi đã tải mô hình | Toàn bộ FR-AI với `provider=local` không gọi ra ngoài |
| NFR-39 | Kích thước mô hình cục bộ | ≤ 500 MB; tải một lần, có băm kiểm tra |
| NFR-40 | Thời gian sinh embedding toàn kho | ≤ 15 phút trên CPU 4 nhân cho 5.709 công trình |
| NFR-41 | Đối chiếu một đề tài | ≤ 5 giây (NFR-14), đo cả bước embed câu hỏi |
| NFR-42 | Không gửi dữ liệu cá nhân ra dịch vụ ngoài | Chỉ gửi tiêu đề, tóm tắt, từ khoá; test kiểm payload |
| NFR-43 | Gợi ý AI không tự đổi dữ liệu | 0 dòng ghi vào `work`, `author_link`, `duplicate_group` từ mã trong `cris/ai/`; test kiểm |
| NFR-44 | Giấy phép mô hình và thư viện AI | Apache-2.0 / MIT / tương thích; ghi trong `DEPENDENCIES.md` trước khi commit |

## 7. Ràng buộc thiết kế

- Ba tầng tách bạch: nghiệp vụ (`cris/*.py`) — web (`cris/web/`) — AI (`cris/ai/`). Web và AI chỉ gọi vào nghiệp vụ; AI ghi vào bảng của riêng nó.
- Không thêm framework web trong bản dự thi. Đổi sang Flask được cân nhắc khi làm đăng nhập (NFR-01); chi phí đo được: thay `wsgi.py` và `render.py`, giữ nguyên các `views_*.py`.
- Mọi quy tắc (chuẩn hoá, khoá gộp, ngưỡng AI, số cụm) là cấu hình đọc được, không nhúng trong mã.
- Test không mock cơ sở dữ liệu và không mock mô hình AI: test AI dùng mô hình thật với fixture nhỏ, đánh dấu chạy chậm để CI có thể tách.

## 8. Tích hợp AI — lựa chọn và lý do

### 8.1 Vì sao đặt AI ở ba chỗ này

| Chỗ | Vấn đề đo được | Không có AI thì sao |
|---|---|---|
| Đối chiếu đề tài | 703 đồ án cùng mở đầu "Xây dựng website"; từ khoá 76 % chỉ xuất hiện một lần → khớp tiêu đề và từ khoá gần như vô dụng | Chỉ còn tìm chuỗi; sinh viên tự đọc 5.375 tiêu đề |
| Gợi ý hàng đợi tác giả | 21 tên chưa nối, ca trùng tên khác người | Người xem tay từng ca, không có thứ tự ưu tiên |
| Gom cụm từ khoá | 10.951 từ khoá không kiểm soát | Không có bộ lọc chủ đề dùng được |

Cả ba đều là chỗ **máy xếp hạng, người quyết** — đúng BR-18 và đúng tinh thần cuộc thi: AI giải quyết bài toán thực tế trong học tập.

### 8.2 Vì sao hướng lai

Thể lệ chấm "cài đặt, dịch từ mã nguồn" (10 điểm) và "thư viện, gói đính kèm" (10 điểm). Sản phẩm không chạy khi thiếu khoá dịch vụ đóng sẽ yếu ở cả hai. Mô hình cục bộ giữ được điểm đó; dịch vụ ngoài là tuỳ chọn để nâng chất lượng giải thích khi có.

### 8.3 Thư viện dự kiến cho `provider=local`

Chọn theo hai tiêu chí: giấy phép tương thích Apache-2.0, và chạy CPU không cần GPU. Ứng viên đánh giá ở lát cắt AI, ghi kết quả vào `DEPENDENCIES.md`: thư viện suy luận ONNX + mô hình embedding đa ngữ cỡ nhỏ (~100–500 MB) có tiếng Việt. Không chọn thư viện kéo theo bộ huấn luyện đầy đủ chỉ để suy luận.

## 9. Ma trận truy vết

| YN (BRD) | FR (SRS) | UC (BA) | US (BA) | BR thực thi |
|---|---|---|---|---|
| YN-01 | FR-S-01..05, 07 | UC-01 | US-01..03 | BR-06 |
| YN-02 | FR-N-01, 11, 12, 16 | UC-02 | US-03, 05 | BR-06, BR-10 |
| YN-03 | FR-N-02..06, FR-Q-01 | UC-03 | US-06..12 | BR-07 |
| YN-04 | FR-N-07..10, FR-Q-02 | UC-04 | US-13..16 | BR-08, BR-09, BR-10 |
| YN-05 | FR-Q-03, FR-N-04 | UC-03, UC-04 | US-08, 10, 14 | BR-11, BR-14, BR-18 |
| YN-06 | FR-T-01..03 | UC-15 | US-32 | BR-03 |
| YN-07 | FR-AI-02..04, FR-T-05 | UC-16 | US-33, 34 | BR-16, BR-17 |
| YN-08 | FR-AI-01, 06, 07, 08 | UC-03, UC-04, UC-16 | US-08, 14, 34 | BR-18 |
| YN-09 | FR-N-15, FR-T-04 | UC-05 | US-04 | — |
| YN-10 | hồ sơ nguồn mở, FR-C, release | — | — | — |
| (K) | FR-K-01..03 | UC-06 | — | BR-01, BR-02, BR-05 |
