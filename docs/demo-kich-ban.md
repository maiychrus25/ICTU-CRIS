# Kịch bản trình diễn — chung kết 10/10/2026

Thời lượng mục tiêu: **9–12 phút** cho bảy phân đoạn lõi (1–7), cộng tối đa **4–5 phút** cho
tám phân đoạn bổ sung lát cắt J/K/L (8–15, bản đồ tri thức/tìm chuyên gia/cổng sinh
viên/trích dẫn/cảnh báo bất thường/chốt kỳ → báo cáo đóng băng/thông báo/góc nhìn khoa) nếu
chương trình còn thời gian — cắt bớt đoạn 8–15 đầu tiên khi phải rút ngắn, không cắt đoạn
1–7. Cộng phần hỏi đáp riêng (mục cuối). Chạy
trên container đã dựng (`docker compose up`), dữ liệu thật đồng bộ từ
`repository.ictu.edu.vn` (7.618 công trình, 410 giảng viên, 903 liên kết chờ xác nhận, 39
nhóm nghi trùng, khoá 21: 529 đồ án đã rà, 47 gắn cờ). Ảnh tham chiếu: `docs/images/*.png`
(chụp trên cùng dữ liệu, 11/09/2026).

**Trước khi lên trình diễn**, xem mục "Chuẩn bị trước buổi demo" ở cuối tài liệu này.

---

## Mở đầu (30 giây)

Không mở màn hình ngay — nói ba con số trước, lấy từ README §"Ba số liệu chi phối thiết kế":

> "Trước khi xem giao diện, ba con số này quyết định toàn bộ cách chúng tôi thiết kế hệ
> thống. Một: ở kho gốc, chỉ **8% bài báo** nối được với đúng giảng viên đã viết ra nó —
> chuẩn hoá tên đưa con số đó lên **86%**. Hai: kho **không có toàn văn** — 39 trên 40 PDF
> chỉ là tóm tắt một trang do máy sinh, nên AI ở đây không đọc được luận văn, chỉ đọc được
> tóm tắt. Ba: **4.621 trên 5.375 đồ án (86%)** ghi tên giảng viên hướng dẫn là chữ giữ chỗ
> `ICTU_TEACHER` — dữ liệu nguồn hỏng có hệ thống, không phải ngoại lệ hiếm gặp. Mọi màn
> sau đây trả lời trực tiếp một trong ba con số đó."

Mở trình duyệt tới `http://localhost:8000/tong-quan/`.

---

## 1. Tổng quan lãnh đạo (60–75 giây)

**URL**: `/tong-quan/`

**Thao tác**:
1. Trang mở sẵn — chỉ vào hàng bốn thẻ số ở đầu trang: Tổng công trình 5 năm, % đã liên
   kết tác giả, Liên kết chờ xác nhận, Nhóm nghi trùng đang mở.
2. Cuộn xuống biểu đồ cột chồng "Công trình theo năm và loại tài liệu" — chỉ vào dòng chú
   thích dưới biểu đồ ("... công trình không rõ năm").
3. Chỉ vào bảng "Công trình theo đơn vị" và bảng "10 giảng viên có nhiều công trình nhất";
   bấm vào tên một giảng viên trong bảng để mở hồ sơ (chuyển tiếp tự nhiên sang phân đoạn 2).

**Câu nói then chốt**:
> "Đây là màn đầu tiên lãnh đạo thấy khi mở hệ thống — không phải bảng Excel gửi qua
> email, mà một trang sống, mỗi con số bấm được đi tiếp về hàng đợi hay hồ sơ đứng sau nó."

**Con số thật**: tổng công trình sau chuẩn hoá 7.618; bài báo có liên kết tác giả 86,6%
(nguồn: 8%); 903 liên kết tác giả chờ xác nhận; 39 nhóm nghi trùng.

**Lưu ý biểu đồ**: đồ án/luận văn/luận án không có năm xuất bản ở nguồn, nên biểu đồ theo
năm trong bản này **chỉ có bài báo** — 5.734 công trình rơi vào "không rõ năm" (xem mục
"Đã biết" của `docs/release-notes/v0.2.0.md`). Nếu giám khảo hỏi tại sao đồ án không lên
biểu đồ, trả lời thẳng bằng câu này, không né tránh.

**Ảnh**: `docs/images/tong-quan.png`

---

## 2. Tra cứu → chi tiết công trình (75–90 giây)

**Thông điệp chính đoạn này**: *"mỗi con số truy ngược được"*.

**URL**: `/tra-cuu/` → `/cong-trinh/?id=<id>`

**Thao tác**:
1. Ở `/tra-cuu/`, gõ một từ khoá quen thuộc (ví dụ "Android" hoặc tên một giảng viên), lọc
   theo loại tài liệu bằng ô chọn, quan sát bảng kết quả cập nhật.
2. Bấm vào tiêu đề một công trình để mở `/cong-trinh/?id=`.
3. Chỉ vào bảng "Xuất xứ dữ liệu": bốn cột **Trường / Giá trị đang dùng / Giá trị gốc /
   Nguồn** — chọn một dòng mà giá trị đang dùng khác giá trị gốc (ví dụ tên đơn vị đã gom
   biến thể, hoặc loại bài đã tách từ văn bản tự do) để minh hoạ sự khác biệt.
4. Cuộn xuống bảng "Tác giả": chỉ cột "Giảng viên liên kết" và "Trạng thái" — nếu công
   trình có tác giả `Chờ xác nhận`, nói rõ đây chính là hàng đợi ở phân đoạn 3.

**Câu nói then chốt**:
> "Ba cột này là câu trả lời cho câu hỏi mà Phòng Khoa học – Công nghệ bị hỏi nhiều nhất:
> 'số này ở đâu ra?'. Giá trị gốc không bao giờ bị ghi đè; giá trị đang dùng luôn nói được
> nó từ nguồn nào, ai đổi, lúc nào."

**Con số thật**: kho nguồn 8.034 bản ghi thô → 7.618 công trình sau chuẩn hoá; đồng bộ đủ
100% kể cả 11 bản ghi bị bỏ sót do phân trang không ổn định (S-04).

**Ảnh**: `docs/images/tra-cuu.png`, `docs/images/cong-trinh.png`

---

## 3. Hàng đợi tác giả có gợi ý AI + gợi ý người hướng dẫn (135 giây)

> **Nhắc trước khi demo**: chạy trên bản sao DB dành riêng cho demo, hoặc nếu dùng DB
> thật thì chỉ thao tác trên các hàng đã kiểm tra trước là an toàn để đổi trạng thái
> (tránh xác nhận/bác bỏ nhầm một liên kết còn cần giữ nguyên cho lần demo sau).

**Phần A — hàng đợi tác giả** (90 giây):

**URL**: `/doi-soat/tac-gia/`

**Thao tác**:
1. Trang mở ở tab "Chờ xác nhận" — chỉ vào số đếm trên tab (903).
2. Chỉ vào một dòng có cột "Gợi ý AI" hiển thị huy hiệu "gợi ý · hạng 1" kèm lý do (ví dụ
   "3 công trình đã xác nhận của người này cùng chủ đề").
3. Tick chọn 1–2 dòng **đã kiểm tra trước là an toàn**; thanh hành động nổi lên ở đáy màn
   hình với ba nút: **Xác nhận**, **Bác bỏ**, **Chuyển cho người khác**.
4. Bấm **Bác bỏ** trên một dòng khác để mở hộp thoại — chỉ vào ô "Lý do" bắt buộc (dấu `*`)
   trước khi bấm Bác bỏ trong hộp thoại, không submit thật nếu không cần.
5. Bấm **Xác nhận** cho các dòng đã chọn ở bước 3 — toast báo "Đã xử lý N liên kết tác
   giả."; số đếm trên tab giảm ngay.

**Câu nói then chốt**:
> "AI chỉ xếp hạng ứng viên và giải thích vì sao — không có nút nào trong hệ thống tự nối
> tác giả. Người bấm Xác nhận, và hệ thống ghi lại ai bấm, lúc nào, vào nhật ký thao tác."

**Con số thật**: 903 liên kết đang chờ xác nhận; nối tự động 3.135 lượt; bài báo 86,6% có
liên kết (78,8% tự động + 15,9% chờ xác nhận) so với 8% ở nguồn.

**Ảnh**: `docs/images/hang-doi-tac-gia.png`

**Phần B — Gợi ý người hướng dẫn (AI)** (`/doi-soat/huong-dan/`, 45 giây):

1. Mở `/doi-soat/huong-dan/` — chỉ vào dòng đầu trang: **4.621/5.375 đồ án (86%)** đang
   ghi người hướng dẫn là `ICTU_TEACHER`, AI gợi ý được cho **1.381** (29,9%).
2. Tìm dòng đồ án về đề tài "kiểm thử tự động bằng Selenium" — chỉ vào ứng viên hàng đầu
   **Nguyễn Lan Oanh** (3 phiếu, điểm 2,606) và đồ án dẫn chứng đã có liên kết thật.
3. Bấm **"Đưa vào hàng đợi"** — toast báo đã tạo liên kết `ChoXacNhan`; nhấn mạnh: đây
   **không** tự xác nhận, dòng này giờ hiện ra đúng ở hàng đợi tác giả vừa demo ở Phần A.

**Câu nói then chốt**:
> "AI không tự gán người hướng dẫn — nó chỉ tìm đồ án cùng đề tài đã có người hướng dẫn
> thật, xếp hạng ứng viên kèm bằng chứng, rồi đưa vào đúng hàng đợi xác nhận mà chuyên
> viên vừa dùng ở phần trên. Quyết định cuối cùng luôn ở đó, không có đường tắt nào khác."

**Con số thật**: 4.621/5.375 đồ án ghi `ICTU_TEACHER`; AI gợi ý được cho 1.381 đồ án
(29,9%) có ít nhất một ứng viên qua ngưỡng (`k=5, min_votes=2, min_score=0,70`); ứng viên
Nguyễn Lan Oanh xuất hiện lặp lại ở nhiều đồ án đích vì đề tài Selenium phổ biến ở cùng
một khoá — đúng cảnh báo "một đề tài phổ biến có thể do nhiều giảng viên khác nhau hướng
dẫn" ghi trong docstring `suggest_mentors` (`docs/ai.md` mục 6).

---

## 4. Nghi trùng so cạnh nhau + Giữ riêng khi đồ án nhóm (90 giây)

**URL**: `/doi-soat/trung-lap/` → `/doi-soat/trung-lap/chi-tiet/?id=`

**Thao tác**:
1. Ở `/doi-soat/trung-lap/`, tab "Nghi trùng" — chỉ cột "Lưu ý" có huy hiệu cảnh báo màu
   vàng ở các nhóm bị gắn `hint` (dấu hiệu đồ án nhóm).
2. Bấm vào một nhóm có cảnh báo để mở trang chi tiết.
3. Chỉ vào **hộp cảnh báo đỏ/vàng đầu trang**: "Dấu hiệu này cho thấy các bản ghi có thể
   thuộc cùng một đồ án nhóm. Hãy ưu tiên kiểm tra trước khi gộp."
4. Chỉ vào bảng so sánh cạnh nhau: mỗi cột là một công trình thành viên, ô có giá trị khác
   nhau được tô nền vàng.
5. Nếu nhóm có tương đồng AI, chỉ vào khối "Tương đồng AI" (phần trăm cosine giữa tóm tắt).
6. Chỉ vào ba nút cuối trang: **Bỏ qua**, **Giữ riêng** (nổi bật — biến `default` — khi có
   cảnh báo đồ án nhóm), **Gộp** (biến phụ khi có cảnh báo). Bấm **Giữ riêng**, nhập lý do
   ví dụ "Đây là đồ án nhóm của các nhóm sinh viên khác nhau…", xác nhận.

**Câu nói then chốt**:
> "Gộp trùng theo tiêu đề ngây thơ sẽ xoá dữ liệu thật — 34 trên 43 nhóm trùng tiêu đề ở
> khảo sát ban đầu là đồ án nhóm hợp lệ. Vì vậy nút mặc định được đề xuất luôn là Giữ
> riêng khi có cảnh báo, và Gộp không bao giờ tự chạy."

**Con số thật**: 39 nhóm nghi trùng đang mở trên dữ liệu thật, 15 nhóm có cảnh báo đồ án
nhóm.

**Ảnh**: `docs/images/nghi-trung.png`

---

## 5. Đối chiếu đề tài 4 khía cạnh + rà soát theo khoá (120 giây)

**URL**: `/doi-chieu/` rồi `/doi-chieu/ra-soat/`

**Phần A — đối chiếu đề tài dự kiến** (`/doi-chieu/`):
1. Nhập một tiêu đề đề tài mẫu (ví dụ "Xây dựng ứng dụng học tiếng Anh có tích hợp AI trên
   Android"), điền ngắn gọn một hoặc hai trong bốn khía cạnh (bài toán, đối tượng, phạm vi,
   phương pháp), bấm **Đối chiếu đề tài**.
2. Chỉ vào hộp "Phạm vi kết quả" — luôn có câu *"so trên tiêu đề, tóm tắt và từ khoá —
   không phải toàn văn"*.
3. Chỉ vào từng kết quả: ma trận bốn khía cạnh (giống / khác / chưa đủ thông tin), **không
   có điểm phần trăm tổng hợp nào** — nhấn mạnh đây là chủ ý thiết kế (BR-17).

**Phần B — rà soát theo khoá** (`/doi-chieu/ra-soat/`):
1. Chọn khoá **21** ở ô "Khoá" (nhãn hiển thị "Khoá 21 — 529 đồ án, 47 gắn cờ"), mức tối
   thiểu "Cao".
2. Chỉ vào từng kết quả: nhãn mức (Cao/Vừa/Thấp), điểm tương đồng tóm tắt, danh sách láng
   giềng ở khoá khác kèm điểm số.
3. Bấm **Đối chiếu chi tiết** trên một kết quả để cho thấy nó điền sẵn tiêu đề sang màn
   Phần A.

**Câu nói then chốt**:
> "Ngưỡng 0,90/0,80 không phải số mặc định thư viện — chúng tôi đo trên toàn bộ 529 đồ án
> khoá 21 đã có vector, thấy ngưỡng khía cạnh 0,55/0,35 kế thừa từ đối chiếu đề tài gắn cờ
> 100% đồ án, vô dụng. Đọc bằng mắt hàng chục cặp quanh 0,80–0,95 rồi mới chọn 0,90 làm
> ngưỡng 'Cao' — gắn cờ 47 trên 529 đồ án, khoảng 8,9%, nằm trong khoảng mục tiêu 5–15%.
> Và dù mức là 'Cao', hệ thống không tự làm gì cả — **AI gợi ý, người quyết**; đây không
> phải kiểm tra đạo văn, chỉ là gợi ý để giảng viên xem lại."

**Con số thật**: cohort 21, 529 đồ án đã rà; phân vị điểm p50=0,835 · p90=0,897 · p99=0,928;
47/529 (8,9%) gắn cờ mức Cao ở ngưỡng 0,90; ngưỡng cũ kế thừa 0,55/0,35 gắn cờ 529/529
(100%).

**Ảnh**: `docs/images/doi-chieu.png`, `docs/images/ra-soat.png`

---

## 6. Kỳ báo cáo, kê khai hai cấp, minh chứng tệp & chỉnh tay có xuất xứ (110–140 giây)

**Chuẩn bị riêng cho phân đoạn này**: quy trình duyệt hai cấp đổi vai giữa chuyên viên
khoa, lãnh đạo khoa và phòng KH-CN. **Trước** buổi demo: đặt mật khẩu cho ba tài khoản mẫu
(xem "Chuẩn bị trước buổi demo" cuối tài liệu), rồi mở sẵn **ba tab trình duyệt ẩn danh** —
mỗi tab giữ một phiên đăng nhập riêng, tránh việc đăng nhập ở tab sau ghi đè cookie phiên
của tab trước:

| Tab | Tài khoản | Vai trò | Đơn vị |
|---|---|---|---|
| 1 | `rd@ictu.edu.vn` | `rd_officer` — phòng KH-CN | toàn trường |
| 2 | `khoa.cntt@ictu.edu.vn` | `faculty_officer` — chuyên viên khoa | `HIEUTRUONG` |
| 3 | `truong.khoa@ictu.edu.vn` | `faculty_head` — lãnh đạo khoa | `HIEUTRUONG` |

**Phần A — duyệt hai cấp** (`/ky-bao-cao/chi-tiet/?id=1`, mỗi tab):
1. Tab 2 — mở kỳ mẫu **`2026-H2`**, tab "Hồ sơ kê khai", chỉ vào **hồ sơ #2**: đã đi hết
   vòng duyệt tới **Đạt yêu cầu** — mở nhật ký `declaration_event`, đọc to bốn bước Trình
   khoa duyệt → Khoa đã duyệt → Gửi phòng → Đạt yêu cầu.
2. Tab 3 — mở **hồ sơ #3**: đang ở **Nháp** kèm huy hiệu "đã bị trả về"; chỉ vào lý do bắt
   buộc trong nhật ký: *"Thiếu minh chứng trang bìa tạp chí"* — nhấn mạnh hồ sơ **mất dấu
   đã duyệt**, phải sửa và trình lại từ đầu, không giữ nguyên trạng thái cũ.
3. Tab 1 — chỉ vào bảng tiến độ theo đơn vị (đủ cột cho 8 trạng thái, Nháp + Chờ bổ sung
   gộp thành "Đang soạn"); nếu kỳ đã Đã đóng nộp, bấm **Chốt kỳ** để minh hoạ chuyển hàng
   loạt hồ sơ Đạt yêu cầu → Đã chốt.

**Phần B — chỉnh tay có xuất xứ** (30 giây, tab 1 — `rd_officer`, tại `/cong-trinh/?id=`):
1. Ở bảng "Xuất xứ dữ liệu", bấm bút chì cạnh dòng **DOI**.
2. Nhập DOI mới và lý do bắt buộc (ví dụ "DOI cũ trỏ sai bản in lại"), lưu.
3. Chỉ vào dòng "Nguồn" vừa đổi thành **"Chỉnh tay bởi … lúc …"** kèm badge "Đã chỉnh
   tay" — cột "Giá trị gốc" vẫn giữ nguyên giá trị từ kho, không bị ghi đè.

**Phần C — tải minh chứng dạng tệp** (20 giây, tab 2 — `faculty_officer`, tại
`/ke-khai/?id=`):
1. Ở hồ sơ kê khai, bấm "Thêm minh chứng" → kéo-thả hoặc chọn một tệp PDF từ máy.
2. Sau khi tải xong, chỉ vào dòng minh chứng mới: tên tệp, kích thước, mã băm SHA-256
   rút gọn, nút tải về.
3. Bấm nút tải về để minh hoạ: trình duyệt nhận đúng tệp vừa tải lên.

**Câu nói riêng cho Phần C**:
> "Minh chứng giờ là một tệp thật lưu trên máy chủ, không còn chỉ là một đường link có
> thể chết bất cứ lúc nào — băm SHA-256 đảm bảo tệp tải về đúng là tệp đã nộp, và chỉ
> người trong đơn vị mới tải được về."

**Câu nói then chốt**:
> "Khoa duyệt trước, phòng kiểm tra sau, mỗi lần trả về đều bắt buộc nêu lý do và hồ sơ
> mất dấu đã duyệt. Và khi phòng KH-CN cần sửa tay một trường dữ liệu — DOI sai, tên tạp
> chí gõ nhầm — hệ thống không xoá xuất xứ cũ, chỉ thêm một lớp xuất xứ mới kèm lý do; theo
> BR-23, phòng KH-CN chỉ sửa được chín trường mô tả, không đụng được tác giả, đơn vị hay
> minh chứng."

**Con số thật**: kỳ mẫu `2026-H2`; hồ sơ #2 Đạt yêu cầu (đủ bốn bước duyệt); hồ sơ #3 bị
trả về Nháp, lý do "Thiếu minh chứng trang bìa tạp chí".

**Ảnh**: `docs/images/cong-trinh.png`.

---

## 7. Về hệ thống: AI cục bộ, giấy phép, giới hạn (60–75 giây)

**URL**: `/ve/`

**Thao tác**:
1. Chỉ khối "AI trong hệ thống": nhà cung cấp, mô hình
   `paraphrase-multilingual-MiniLM-L12-v2`, giấy phép Apache-2.0, kích thước 118 MB/384
   chiều, số vector đã tạo, số chủ đề/gợi ý, số khoá đã rà soát.
2. Chỉ khối "Giới hạn cần lưu ý" — đọc to 1–2 dòng đầu (chỉ so trên tóm tắt; không có điểm
   phần trăm tổng hợp).
3. Chuyển màn hình sang terminal hoặc mở tab mới tới `http://localhost:8000/docs` — cuộn
   nhanh qua OpenAPI, chỉ vào một endpoint bất kỳ có `response_model`.
4. Nếu có thời gian, mở GitHub repo: chỉ vào badge CI xanh, trang Releases (`v0.1.0`),
   Dockerfile đa tầng.

**Câu nói then chốt (khép lại)**:
> "Mọi phần AI trong sản phẩm này chạy hoàn toàn cục bộ, không cần khoá API, không cần
> GPU, tải mô hình một lần rồi chạy offline — đúng điều kiện để giám khảo tự cài và tự
> chạy từ mã nguồn. Và đây là phần hồ sơ nguồn mở đứng sau nó: giấy phép Apache-2.0, CI
> xanh trên mỗi commit, release theo semver, một ảnh Docker duy nhất chạy đủ cả API lẫn
> giao diện."

**Ảnh**: `docs/images/giang-vien.png` (dự phòng nếu còn thời gian cho hồ sơ giảng viên).

---

## 8. Bản đồ tri thức & xu hướng (60 giây)

**URL**: `/ban-do/`

**Thao tác**:
1. Mở `/ban-do/` — canvas hiện 7.618 điểm, tô màu mặc định theo chủ đề; đổi tiêu chí tô
   màu sang "Đơn vị" hoặc "Năm" bằng ô chọn phía trên.
2. Zoom/pan bằng chuột hoặc chạm, hover một điểm để hiện tiêu đề công trình, click một
   điểm để mở chi tiết công trình đó.
3. Chuyển tab "Xu hướng" — chọn một cụm chủ đề lớn, chỉ vào biểu đồ vùng xếp chồng theo
   khoá/năm.
4. Chuyển tab "Đồng tác giả" — chỉ vào một nút lớn (nhiều công trình chung), bấm ra hồ sơ
   giảng viên.

**Câu nói then chốt**:
> "Đây không phải một phép đo chính xác — chỉ 2 trên 384 chiều của vector ngữ nghĩa gốc,
> dùng để định hướng vùng nào gần vùng nào, không phải để kết luận hai công trình giống
> nhau bao nhiêu phần trăm."

**Con số thật**: 7.618 điểm, 39 cụm chủ đề, dựng trong 9,7 giây (`python -m cris ai map`);
`GET /api/ai/map` trả JSON khoảng 1,5 MB.

---

## 9. Tìm chuyên gia (45 giây)

**URL**: `/doi-chieu/chuyen-gia/` (tab thứ ba của "Đối chiếu đề tài")

**Thao tác**:
1. Nhập một đề tài mẫu, lọc học vị (ví dụ "TS" trở lên) nếu cần, bấm tìm.
2. Chỉ vào một thẻ giảng viên: thanh điểm, số công trình liên quan, 3 dẫn chứng kèm điểm.
3. Đọc dòng nhắc cuối kết quả: "gợi ý trên tóm tắt, người quyết".

**Câu nói then chốt**:
> "Đo trên 30 đồ án có GVHD thật — che tên người hướng dẫn rồi hỏi lại: đúng ngay vị trí
> đầu 23,3% số ca, nằm trong 5 gợi ý đầu 46,7%. Nghĩa là hơn một nửa số ca, người hướng dẫn
> thật **không** nằm trong top-5 — đây không phải AI đoán đúng người hướng dẫn, chỉ là suy
> luận từ tương đồng đề tài với công trình đã liên kết, dùng để thu hẹp danh sách liên hệ,
> không thay cho tìm hiểu thực tế."

**Con số thật**: top-1 7/30 (23,3%), top-5 14/30 (46,7%) (`scripts/eval_experts.py`,
`docs/ai.md` mục 8); thời gian trung bình mỗi lượt tìm 3,94 giây.

---

## 10. Cổng kiểm tra đề tài (30 giây)

**URL**: `/kiem-tra-de-tai/` — mở ở một tab ẩn danh mới để cho thấy không cần tài khoản.

**Thao tác**:
1. Vào thẳng `/kiem-tra-de-tai/` — không sidebar, không nút đăng nhập, một ô nhập lớn.
2. Nhập một đề tài dự kiến, bấm kiểm tra.
3. Chỉ vào hai khối kết quả: "Đề tài tương tự các khoá trước" (mức cao/vừa/thấp) và "Giảng
   viên gần chuyên môn" — chỉ rõ không có email hay số điện thoại nào hiện trong kết quả.

**Câu nói then chốt**:
> "Sinh viên tự vào trước khi đăng ký chính thức, không cần tài khoản, không lưu lại lượt
> tra cứu nào — chỉ giới hạn 20 lượt mỗi 5 phút theo địa chỉ IP để tránh dùng quá tải."

---

## 11. Trích dẫn & lý lịch khoa học (20 giây)

**URL**: `/cong-trinh/?id=` rồi `/giang-vien/ly-lich/?id=`

**Thao tác**:
1. Ở chi tiết công trình, bấm nút "Trích dẫn" — hộp thoại ba tab APA/IEEE/BibTeX, bấm sao
   chép một kiểu.
2. Từ hồ sơ giảng viên, bấm "Lý lịch khoa học" — trang in được (A4), bấm nút In/PDF để
   minh hoạ `window.print()`.

**Câu nói then chốt**:
> "Trích dẫn dựng thẳng từ metadata đã chuẩn hoá, không phải nhập tay; lý lịch khoa học tự
> tổng hợp số liệu công bố theo loại/năm và danh sách công trình dạng APA, sẵn sàng nộp hồ
> sơ xét duyệt."

---

## 12. Cảnh báo bất thường dữ liệu (20 giây)

**URL**: `/chat-luong-du-lieu/` → tab "Cảnh báo"

**Thao tác**:
1. Chỉ vào bảng cảnh báo theo loại — dòng "Ghi Scopus/ISI nhưng không có DOI" đang mở
   **64** cờ.
2. Bấm "Bỏ qua" trên một dòng, nhập lý do, xác nhận — cờ chuyển trạng thái ngay, có ghi
   nhật ký thao tác.

**Câu nói then chốt**:
> "Quét chỉ đọc dữ liệu, không tự sửa gì — 64 bài Scopus/WoS thiếu DOI, 2 luận văn trùng
> tiêu đề với một bài báo, 1.697 bài báo chưa có tóm tắt là ba con số nổi nhất; chuyên viên
> tự xem và bỏ qua kèm lý do nếu đã kiểm tra là không sao."

---

## 13. Chốt kỳ → báo cáo đóng băng (45 giây)

**URL**: `/ky-bao-cao/chi-tiet/?id=` (tab "Báo cáo", `rd_officer`) → `/bao-cao/?id=`

**Thao tác**:
1. Ở tab "Báo cáo" của kỳ mẫu **`2026-H2`** đã **Đã đóng nộp**, bấm **Chốt kỳ** — hệ thống
   chuyển thẳng tới bản báo cáo vừa tự sinh, không cần bấm thêm lần nào để "tạo báo cáo".
2. Chỉ vào badge **"Đóng băng · SHA-256 …"** đầu trang — hover vào tooltip giải thích: bản
   ghi này chụp lại toàn bộ hồ sơ kê khai tại đúng thời điểm chốt, không đổi về sau dù dữ
   liệu gốc có sửa tiếp.
3. Chỉ vào bảng tổng hợp đơn vị × trạng thái và bảng theo loại tài liệu, rồi cuộn xuống bảng
   chi tiết từng hồ sơ (có ô tìm nhanh).
4. Bấm nút tải **XLSX** — chỉ vào tệp vừa tải: hai sheet "Tổng hợp" và "Chi tiết", tiêu đề
   in đậm, hàng đầu cố định.

**Câu nói then chốt**:
> "Số liệu đã ký không sửa ngầm được. Mỗi lần chốt kỳ tạo một phiên bản báo cáo mới, kèm mã
> băm SHA-256 của toàn bộ dữ liệu — ai cũng tính lại được mã băm đó để chứng minh báo cáo
> chưa bị đổi một dòng nào, kể cả khi hồ sơ gốc bị sửa tiếp sau ngày chốt."

**Con số thật**: kỳ mẫu `2026-H2`, phiên bản v1, 3 hồ sơ kê khai tại thời điểm chốt.

---

## 14. Thông báo (15 giây)

**URL**: bất kỳ trang nào đã đăng nhập (chuông ở topbar) → `/thong-bao/`

**Thao tác**:
1. Chỉ vào chuông ở topbar — số chưa đọc hiện ngay trên huy hiệu.
2. Bấm chuông mở popover: danh sách thông báo gần nhất kèm thời gian tương đối; bấm một
   dòng — điều hướng thẳng tới hồ sơ/báo cáo liên quan và tự đánh dấu đã đọc.
3. Bấm "Đánh dấu tất cả đã đọc", huy hiệu về 0.

**Câu nói then chốt**:
> "Không phải chờ ai nhắc bằng lời hay bằng Excel gửi qua email nữa — hồ sơ đổi trạng thái,
> kỳ mở/đóng/chốt, hay công trình vừa được nối vào hồ sơ của mình, người liên quan biết ngay
> trong ứng dụng."

---

## 15. Góc nhìn khoa (30 giây)

**URL**: `/khoa/?id=`

**Thao tác**:
1. Mở `/khoa/?id=` của một khoa mẫu — chỉ vào hàng thẻ số: tổng công trình theo loại, 5 năm
   gần nhất.
2. Cuộn xuống bảng "10 giảng viên nhiều công trình nhất" và khối "hồ sơ kê khai theo trạng
   thái" của kỳ đang mở — bấm vào một trạng thái để đi thẳng tới hàng đợi/kỳ tương ứng.
3. Chỉ vào khối "Giảng viên chưa có công trình liên kết" — mỗi dòng có link ra hồ sơ liên
   kết tác giả.

**Câu nói then chốt**:
> "Trước đây lãnh đạo khoa chỉ có được bức tranh này khi chuyên viên tổng hợp tay từ Excel;
> giờ mở một trang là thấy ngay, và bấm vào bất kỳ con số nào cũng đi tiếp được về đúng hàng
> đợi hay hồ sơ đứng sau nó."

---

## Câu hỏi giám khảo có thể hỏi & trả lời ngắn

1. **Vì sao không dùng LLM (ChatGPT/Claude/Gemini) mà chỉ dùng mô hình embedding nhỏ?**
   Thể lệ chấm "cài đặt, dịch từ mã nguồn" và "thư viện, gói đính kèm" — sản phẩm cần chạy
   được khi giám khảo không có khoá API và không có GPU. Mô hình
   `paraphrase-multilingual-MiniLM-L12-v2` (Apache-2.0, 118 MB, chạy CPU) đáp ứng cả hai
   tiêu chí đó; kiến trúc vẫn chừa chỗ cho dịch vụ ngoài (`Provider.explain()`) để sinh
   lời giải thích ngôn ngữ tự nhiên sau này, nhưng **chưa hiện thực** trong bản này
   (`docs/ai.md` §2).

2. **Dữ liệu cá nhân giảng viên xử lý thế nào?**
   Kho mã nguồn chỉ chứa fixture kiểm thử đã ẩn danh (tên, email, điện thoại, ngày sinh).
   Dữ liệu thật không đưa vào Git — đây là cột bị hạn chế truy cập (README §"Dữ liệu &
   Quyền riêng tư"). Tầng AI (`cris/ai/`) chỉ nhận tiêu đề, tóm tắt, từ khoá, mô tả đề
   tài — không có trường cá nhân nào đi qua nó (NFR-42, `docs/SRS.md` §6).

3. **Không có toàn văn thì AI so sánh cái gì?**
   So trên tiêu đề + tóm tắt + từ khoá — mọi trang đối chiếu đều in rõ dòng "so trên tiêu
   đề, tóm tắt và từ khoá — không phải toàn văn" (BR-16/BR-17). Đây là giới hạn của chính
   dữ liệu nguồn: 39/40 PDF lấy mẫu là tóm tắt một trang do máy sinh, không phải toàn văn
   luận văn (BRD §2, vấn đề P5).

4. **Tại sao Next.js lại xuất tĩnh (`output: "export"`) thay vì chạy server Node?**
   Để giữ đúng nguyên tắc "một container, một cổng": FastAPI phục vụ cả `/api/*` và bản
   HTML/CSS/JS tĩnh của giao diện tại `/`, không cần tiến trình Node lúc chạy, không cần
   CORS trong sản xuất, triển khai bằng một ảnh Docker duy nhất
   (`docs/superpowers/plans/2026-09-11-giao-dien-nextjs.md`).

5. **Khi kho nguồn `repository.ictu.edu.vn` đổi cấu trúc HTML thì sao?**
   Bộ đọc nguồn (`cris/source/repository.py`) tách hoàn toàn khỏi phần còn lại của hệ
   thống; test dùng fixture HTML lưu sẵn trong repo nên không phụ thuộc kho sống khi chạy
   CI. Dữ liệu đã đồng bộ trước đó vẫn dùng được bình thường nếu lần đồng bộ sau thất bại —
   rủi ro này được ghi rõ ở `docs/BRD.md` §10 kèm biện pháp giảm thiểu.

6. **Độ chính xác liên kết tác giả 86,6% đo thế nào — có đáng tin không?**
   Đo trên toàn bộ 1.907 bài báo thật sau khi chạy `normalize → link`: 78,8% nối tự động
   (khớp duy nhất theo ORCID hoặc tên chuẩn hoá) + 15,9% vào hàng đợi chờ người xác nhận =
   86,6% có ít nhất một liên kết, so với 8% ở kho gốc (`BUILDING.md` §9, CHANGELOG
   `[0.1.0]`). Đây là tỷ lệ **có liên kết** (tự động hoặc đã vào hàng đợi), không phải tỷ
   lệ liên kết đã được người xác nhận đúng — phần xác nhận đúng/sai vẫn cần người quyết ở
   hàng đợi.

7. **Ngưỡng rà soát trùng đề tài 0,90/0,80 có phải số tuỳ tiện không?**
   Không lấy mặc định thư viện: hiệu chuẩn trên phân bố điểm thật của 529 đồ án khoá 21 đã
   có vector (p50=0,835, p90=0,897, p99=0,928), đọc thủ công hàng chục cặp quanh từng mức
   trước khi chọn — xem chi tiết và ví dụ cặp cụ thể ở `docs/ai.md` §5. Ngưỡng này hiệu
   chỉnh cho **một cohort, một mô hình**; đổi mô hình hoặc rà một cohort khác có thể cần
   đo lại, tài liệu ghi rõ giới hạn này chứ không giấu.

8. **Vì sao trang tổng quan không có biểu đồ đồ án theo năm?**
   Đồ án/luận văn/luận án không có trường năm xuất bản đáng tin ở nguồn — biểu đồ theo năm
   ở `/tong-quan/` vì vậy chỉ vẽ được cho bài báo; 5.734 công trình (phần lớn là đồ án)
   rơi vào nhóm "không rõ năm" và được đếm riêng dưới biểu đồ thay vì đoán năm
   (`docs/release-notes/v0.2.0.md` mục "Đã biết").

9. **Vì sao chưa có đăng nhập thật?**
   Nằm ngoài phạm vi bản dự thi (NFR-01, NFR-02) — thời gian ưu tiên cho đường ống dữ liệu
   và AI, hai phần quyết định điểm PoF + điểm AI. Bản hiện tại chạy với một người dùng mặc
   định hoặc header `X-CRIS-User`, và **không triển khai lên mạng công khai** vì lý do đó
   (README §"Cài đặt nhanh", `docs/SRS.md` §2.2).

10. **AI có tự gộp, tự nối, tự xoá gì không?**
    Không. Mã trong `cris/ai/` chỉ ghi vào bốn bảng riêng của nó
    (`ai_embedding`, `ai_topic`, `ai_topic_keyword`, `ai_suggestion`, `ai_query`) — có test
    rào chắn đếm số dòng `work`, `author_link`, `duplicate_group`, `field_provenance`
    trước và sau mỗi thao tác AI để đảm bảo bằng 0 thay đổi (NFR-43, `docs/ai.md` §1, §7).

11. **Mật khẩu lưu thế nào?**
    Băm bằng `hashlib.pbkdf2_hmac` (PBKDF2-HMAC-SHA256, 260.000 vòng, salt 16 byte riêng
    mỗi người) — không lưu mật khẩu gốc, không thêm dependency (`cris/auth.py`). Phiên đăng
    nhập là cookie `cris_session` (HttpOnly, SameSite=Lax, hết hạn 12 giờ); đăng nhập sai bị
    giới hạn 5 lần/5 phút theo email. Hệ thống chạy **chế độ mở** (không bắt buộc đăng
    nhập) cho tới khi một người dùng được đặt mật khẩu — xem `BUILDING.md` §6.5.

12. **Sao không SSO?**
    Trường chưa có hệ SSO sẵn dùng để tích hợp trong thời gian làm bản dự thi (NFR-01,
    `docs/ba/14-nfr.md`) — chọn mật khẩu cục bộ băm chuẩn PBKDF2 để có đăng nhập thật ngay,
    không thêm dependency, và không chặn tích hợp SSO trường thật ở lát cắt sau.

13. **Báo cáo đóng băng khác gì Excel gửi email?**
    Excel gửi qua email không có gì ngăn ai đó mở lại và sửa số sau khi đã gửi, cũng không
    ai chứng minh được bản đang cầm là bản đã chốt hay bản bị sửa tiếp. Báo cáo kỳ đóng băng
    ghi payload đầy đủ (mọi hồ sơ + công trình + tác giả + minh chứng tại thời điểm chốt)
    thành một dòng bất biến trong CSDL kèm mã băm SHA-256 — ai cũng tính lại được mã băm đó
    để kiểm báo cáo có bị đổi hay không, kể cả khi dữ liệu gốc (`declaration`/`work`) sửa
    tiếp sau ngày chốt; mỗi lần chốt kỳ tạo thêm một phiên bản mới (v1, v2, …) thay vì ghi
    đè, nên vẫn xem lại được số liệu của các kỳ trước đúng như lúc chốt.

14. **Ai được sửa dữ liệu, sửa xong có truy ngược được không?**
    Chỉ vai `rd_officer` (phòng KH-CN) sửa trực tiếp được — và chỉ chín trường mô tả
    (`cris/edit.py` — `EDITABLE`: tiêu đề, DOI, năm/số, tạp chí, tập, loại bài, khoá, tóm
    tắt, từ khoá), không sửa được tác giả, đơn vị, minh chứng (BR-23). Mọi lần sửa bắt buộc
    ghi lý do, lưu `field_provenance(set_kind='manual', set_by=...)` và
    `audit_log('work.edit')` — trang chi tiết công trình đổi dòng "Nguồn" thành "Chỉnh tay
    bởi … lúc …", giá trị gốc từ kho không bao giờ bị ghi đè.

15. **Gợi ý người hướng dẫn dựa trên gì, sai thì sao?**
    Dựa trên giả định thống kê (ghi rõ trong docstring `suggest_mentors`, `cris/ai/mentor.py`):
    đồ án cùng đề tài thường do cùng một giảng viên hướng dẫn. Với mỗi đồ án đang ghi
    `ICTU_TEACHER`, hệ thống tìm `k=5` đồ án gần nhất về nghĩa (cosine trên vector tiêu đề
    + tóm tắt + từ khoá) trong số đồ án đã có người hướng dẫn thật liên kết, gộp phiếu theo
    người, chỉ giữ ứng viên đạt `votes≥2` và tổng điểm `≥0,70`. Giả định này **có thể sai**
    — một đề tài phổ biến (ví dụ Selenium) có thể do nhiều giảng viên khác nhau hướng dẫn,
    không chỉ một người — nên sai không gây hậu quả: gợi ý chỉ đưa ứng viên vào hàng đợi
    tác giả ở trạng thái `ChoXacNhan`, giống mọi liên kết khác, chuyên viên xem bằng chứng
    (đồ án dẫn chứng) rồi tự quyết định xác nhận hay bác bỏ (BR-18) — không có gì tự nối.

16. **Khoa và phòng tranh nhau thì sao?**
    Không tranh chấp được vì mỗi bước chuyển trạng thái gắn cứng với một tập vai trò
    (`cris/declare.py` — `_TRANSITIONS`): khoa chỉ đưa hồ sơ từ Chờ khoa duyệt sang Khoa đã
    duyệt hoặc trả về Nháp; phòng chỉ quyết định từ Chờ phòng kiểm tra sang Đạt yêu cầu hoặc
    trả về Nháp — sai vai trò bị chặn ngay ở tầng nghiệp vụ (403), không dựa vào quy ước
    giao diện (NFR-03). Từ Khoa đã duyệt trở đi, mọi thay đổi đưa hồ sơ về lại Nháp và mất
    dấu đã duyệt, nên không có tình huống khoa và phòng cùng giữ hai bản "đã duyệt" khác
    nhau của cùng một hồ sơ.

17. **Tìm kiếm ngữ nghĩa khác gì Google?**
    Google (và tìm từ khoá cũ của hệ thống) khớp chuỗi ký tự — gõ "ứng dụng học tiếng Anh"
    sẽ bỏ lỡ một đồ án ghi "app luyện phát âm Anh ngữ" dù cùng đề tài. Tìm kiếm ngữ nghĩa
    embed câu đã gõ thành vector 384 chiều rồi so cosine với vector tiêu đề+tóm tắt+từ khoá
    của toàn kho — không cần trùng từ nào, xuyên được cả tiếng Việt–tiếng Anh. Đây không
    phải một công cụ tìm kiếm web tổng quát: chỉ tìm trong 7.618 công trình đã có trong kho,
    top-200 gần nghĩa nhất trước khi lọc tiếp (`docs/ai.md` mục 7) — không nhằm thay Google
    cho tra cứu ngoài phạm vi kho.

18. **Bản đồ PCA có tin được không?**
    Tin được để *định hướng*, không tin được để *đo khoảng cách chính xác*. PCA chỉ giữ lại
    2 trong 384 chiều của vector gốc (phần lớn "phương sai" — biến thiên dữ liệu — vẫn mất),
    nên hai điểm gần nhau trên bản đồ **thường** cùng chủ đề nhưng không phải lúc nào cũng
    đúng, và khoảng cách hình học trên canvas không phải một con số tương đồng có thể tin
    tuyệt đối. Muốn so hai công trình cụ thể chính xác hơn, dùng đối chiếu đề tài hoặc tìm
    kiếm ngữ nghĩa (so trên đủ 384 chiều) — bản đồ chỉ để nhìn toàn cảnh hướng nghiên cứu và
    mạng lưới hợp tác, không phải công cụ đo lường (`docs/ai.md` mục 10).

---

## Chuẩn bị trước buổi demo

Checklist chạy theo thứ tự, trên máy sẽ dùng để trình diễn — thử toàn bộ ít nhất một lần
trước ngày 10/10, tốt nhất là ngắt mạng ở bước cuối để chắc chắn hệ thống chạy offline:

- [ ] `docker compose up -d db` rồi `docker compose build app` — dựng xong không lỗi.
- [ ] `docker compose run --rm app migrate` — áp đủ `0001`–`0019`.
- [ ] Có dữ liệu thật đã đồng bộ (đồng bộ trước, không đồng bộ trực tiếp lúc demo — mất
      khoảng 2 giờ); nếu dùng bản sao dữ liệu demo, đối chiếu số liệu trong kịch bản với
      số liệu bản sao trước khi trình diễn.
- [ ] Tạo ba tài khoản demo cho phân đoạn 6 (kê khai hai cấp) — đơn vị `HIEUTRUONG` phải
      tồn tại trước khi gán:
      `python -m cris user create --email rd@ictu.edu.vn --name "Phòng KH-CN" --roles rd_officer`
      `python -m cris user create --email khoa.cntt@ictu.edu.vn --name "Chuyên viên khoa CNTT" --roles faculty_officer --unit HIEUTRUONG`
      `python -m cris user create --email truong.khoa@ictu.edu.vn --name "Trưởng khoa CNTT" --roles faculty_head --unit HIEUTRUONG`
- [ ] Đặt mật khẩu cho **cả ba** tài khoản demo **trước** buổi demo nếu định bật đăng nhập:
      `CRIS_PASSWORD='...' python -m cris user set-password <email>` cho từng tài khoản. Ngay
      khi đã đặt, **toàn hệ thống** chuyển sang bắt buộc đăng nhập — mở sẵn ba tab ẩn danh,
      mỗi tab đăng nhập một tài khoản ở `/dang-nhap/` **trước khi** demo các hàng đợi (phân
      đoạn 3, 4) và kê khai hai cấp (phân đoạn 6), nếu không mọi nút quyết định sẽ bị ẩn.
- [ ] Bật AI: `pip install -e ".[ai]"` (hoặc dùng ảnh có `--build-arg EXTRAS="[ai]"`),
      `python -m cris ai download` (tải một lần, kiểm SHA-256).
- [ ] `export CRIS_AI_PROVIDER=local` rồi lần lượt: `python -m cris ai embed`,
      `python -m cris ai topics`, `python -m cris ai suggest`,
      `python -m cris ai screen --cohort 21`.
- [ ] `python -m cris ai status` — xác nhận provider `local` và số vector đã có khớp số
      công trình.
- [ ] `python -m cris normalize --redo --doc-type do_an` (vá lượt tên vai `mentor` giữ chỗ
      hồi tố cho đồ án đã đồng bộ trước lát cắt I4) rồi `python -m cris ai mentors` — xác
      nhận `suggested > 0` trước khi mở `/doi-soat/huong-dan/` cho phân đoạn 3 Phần B.
- [ ] `python -m cris ai map` (cần `ai embed` + `ai topics` trước) — xác nhận in ra
      `points=7618 topics=39`, rồi `GET /api/ai/map` trả `200` trước khi mở `/ban-do/` cho
      phân đoạn 8.
- [ ] `python -m cris quality scan` — xác nhận báo cáo có cờ mở (`scopus_no_doi` 64,
      `thesis_title_equals_article` 2, `missing_abstract_article` 1.697) trước khi mở
      `/chat-luong-du-lieu/` tab "Cảnh báo" cho phân đoạn 12.
- [ ] Mở `/huong-dan/` — kiểm đủ ảnh cho bốn vai trò, để lại tab này cho giám khảo tự xem
      trong lúc chờ, không cần chờ người thuyết trình dẫn qua từng bước.
- [ ] `python -m cris serve` (hoặc container `serve --host 0.0.0.0`) — mở
      `http://localhost:8000` và `http://localhost:8000/docs`, kiểm cả hai trả `200`.
- [ ] Mở sẵn các tab trình duyệt theo đúng thứ tự mười lăm phân đoạn ở trên, để không mất
      thời gian gõ URL giữa buổi trình diễn: `/tong-quan/`, `/tra-cuu/`, `/doi-soat/tac-gia/`,
      `/doi-soat/huong-dan/`, `/doi-soat/trung-lap/`, `/doi-chieu/`, `/doi-chieu/ra-soat/`,
      `/ky-bao-cao/chi-tiet/?id=1`, `/ke-khai/?id=`, `/huong-dan/`, `/ve/`, `/docs`, `/ban-do/`,
      `/doi-chieu/chuyen-gia/`, `/kiem-tra-de-tai/`, `/giang-vien/ly-lich/?id=`,
      `/chat-luong-du-lieu/`, `/bao-cao/?id=`, `/thong-bao/`, `/khoa/?id=`.
  - [ ] Trước khi thao tác thật trên hàng đợi tác giả/nghi trùng (phân đoạn 3, 4), xác
      nhận đây là **bản sao DB dành cho demo**, hoặc đã đánh dấu trước các hàng "an toàn để
      đổi trạng thái" nếu bắt buộc dùng DB thật.
- [ ] **Kiểm tra chạy offline**: tắt Wi-Fi/mạng, tải lại từng tab đã mở ở trên — mọi trang
      và mọi thao tác AI (đối chiếu, rà soát) vẫn chạy vì mô hình đã tải cục bộ và không
      gọi ra ngoài (`CRIS_AI_PROVIDER=local`, `docs/ai.md` §2, NFR-38).
- [ ] Chuẩn bị một laptop dự phòng hoặc bản ghi màn hình (video) của toàn bộ mười hai phân
      đoạn, phòng khi mạng hội trường hoặc máy chiếu có sự cố — hệ thống không cần mạng để
      chạy, nhưng vẫn nên có phương án dự phòng cho phần cứng.
