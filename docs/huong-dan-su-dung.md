# Hướng dẫn sử dụng ICTU-CRIS

> Tài liệu này viết cho người dùng cuối — phòng Khoa học – Công nghệ (KH-CN), chuyên viên
> và trưởng khoa, giảng viên, lãnh đạo trường. Nó mô tả **đúng** những gì bản hiện tại
> (v0.6.0) làm được: tên nút, tên tab và số liệu lấy trực tiếp từ mã nguồn và từ dữ liệu
> thật đã đồng bộ ngày 11–12/09/2026. Chỗ nào hệ thống chưa làm được, tài liệu ghi rõ
> "chưa có" thay vì bỏ qua.
>
> Câu ngắn, ngôi "bạn". Tên nút/ô/tab in **đậm** đúng chữ hiển thị trên giao diện. Đường
> dẫn trang viết dạng `/tra-cuu/`.

## Mục lục

- [1. Giới thiệu](#1-giới-thiệu)
  - [1.1 Hệ thống là gì](#11-hệ-thống-là-gì)
  - [1.2 Nguồn dữ liệu và ba số liệu chi phối thiết kế](#12-nguồn-dữ-liệu-và-ba-số-liệu-chi-phối-thiết-kế)
  - [1.3 Ai dùng hệ thống — 5 vai trò](#13-ai-dùng-hệ-thống--5-vai-trò)
  - [1.4 Đăng nhập](#14-đăng-nhập)
  - [1.5 Bố cục màn hình](#15-bố-cục-màn-hình)
  - [1.6 Quy ước chung](#16-quy-ước-chung)
- [2. Mục lục tính năng theo menu](#2-mục-lục-tính-năng-theo-menu)
  - [2.1 Tổng quan](#21-tổng-quan)
  - [2.2 Tra cứu](#22-tra-cứu)
  - [2.3 Chi tiết công trình](#23-chi-tiết-công-trình)
  - [2.4 Chủ đề](#24-chủ-đề)
  - [2.5 Bản đồ tri thức](#25-bản-đồ-tri-thức)
  - [2.6 Đối chiếu đề tài](#26-đối-chiếu-đề-tài)
  - [2.7 Cổng kiểm tra đề tài công khai](#27-cổng-kiểm-tra-đề-tài-công-khai)
  - [2.8 Hàng đợi tác giả](#28-hàng-đợi-tác-giả)
  - [2.9 Hàng đợi nghi trùng](#29-hàng-đợi-nghi-trùng)
  - [2.10 Kỳ báo cáo](#210-kỳ-báo-cáo)
  - [2.11 Kê khai của tôi](#211-kê-khai-của-tôi)
  - [2.12 Khoa của tôi / Theo khoa](#212-khoa-của-tôi--theo-khoa)
  - [2.13 Hồ sơ giảng viên](#213-hồ-sơ-giảng-viên)
  - [2.14 Chất lượng dữ liệu](#214-chất-lượng-dữ-liệu)
  - [2.15 Đồng bộ](#215-đồng-bộ)
  - [2.16 Nhật ký](#216-nhật-ký)
  - [2.17 Thông báo](#217-thông-báo)
  - [2.18 Về hệ thống](#218-về-hệ-thống)
  - [2.19 Hướng dẫn trong ứng dụng](#219-hướng-dẫn-trong-ứng-dụng)
- [3. Quy trình nghiệp vụ xuyên suốt](#3-quy-trình-nghiệp-vụ-xuyên-suốt)
  - [3.1 Một kỳ báo cáo: mở → kê khai → khoa duyệt → phòng kiểm tra → chốt](#31-một-kỳ-báo-cáo-mở--kê-khai--khoa-duyệt--phòng-kiểm-tra--chốt)
  - [3.2 Đối soát dữ liệu hàng tuần](#32-đối-soát-dữ-liệu-hàng-tuần)
  - [3.3 Sinh viên/giảng viên chọn đề tài](#33-sinh-viêngiảng-viên-chọn-đề-tài)
- [4. AI trong hệ thống](#4-ai-trong-hệ-thống)
- [5. Câu hỏi thường gặp](#5-câu-hỏi-thường-gặp)
- [6. Thuật ngữ](#6-thuật-ngữ)
- [7. Phụ lục quản trị](#7-phụ-lục-quản-trị)

---

## 1. Giới thiệu

### 1.1 Hệ thống là gì

ICTU-CRIS là hệ thống thông tin nghiên cứu (CRIS — *Current Research Information System*)
cho Trường Công nghệ Thông tin và Truyền thông, Đại học Thái Nguyên. Mục tiêu của nó là
làm **một nguồn sự thật** cho dữ liệu công bố khoa học: mỗi bản ghi kéo về từ kho được giữ
nguyên bản và có phiên bản, mỗi trường dữ liệu sau khi chuẩn hoá vẫn nói được nó xuất xứ từ
đâu, và quyết định cuối cùng — nối một cái tên vào đúng giảng viên, gộp hai bản ghi trùng,
duyệt một hồ sơ kê khai — luôn thuộc về người dùng, không phải máy.

Hệ thống có một tầng AI (đối chiếu đề tài, gợi ý hàng đợi, trục chủ đề, bản đồ tri thức…)
chạy mô hình cục bộ, không gửi dữ liệu ra ngoài. Nguyên tắc xuyên suốt là **BR-18: AI gợi
ý, người quyết** — không có nút nào trong hệ thống để AI tự nối tác giả, tự gộp bản ghi,
hay tự duyệt một hồ sơ.

Dữ liệu công trình lấy từ kho công khai của trường
(`repository.ictu.edu.vn`, nền tảng DSpace), **chỉ nhằm mục đích học tập** — đây không phải
kho lưu trữ chính thức của Bộ Giáo dục và Đào tạo.

### 1.2 Nguồn dữ liệu và ba số liệu chi phối thiết kế

Ba số liệu sau đo trên dữ liệu thật (8.034 bản ghi + 410 hồ sơ giảng viên, 09–10/09/2026)
và giải thích vì sao nhiều màn hình trong hệ thống trông như vậy:

| Số đo | Vì sao nó quan trọng khi bạn dùng hệ thống |
|---|---|
| Liên kết tác giả ở kho gốc chỉ phủ **8%** bài báo (155/1.907); sau khi hệ thống chuẩn hoá tên, con số lên **86,6%** (78,8% nối tự động + 15,9% vào hàng đợi chờ xác nhận) | Đây là lý do **Hàng đợi tác giả** tồn tại — phần lớn công việc hằng ngày của Phòng KH-CN là xác nhận các liên kết này, không phải nhập liệu từ đầu |
| Kho **không có toàn văn** — 39/40 PDF lấy mẫu chỉ là bản tóm tắt một trang do máy sinh | Mọi tính năng AI (đối chiếu đề tài, rà soát trùng, tìm chuyên gia, tìm kiếm ngữ nghĩa) chỉ so được trên **tiêu đề, tóm tắt và từ khoá** — không có "dẫn chứng theo trang" như đọc toàn văn |
| **4.621/5.375 đồ án (86%)** ghi tên giảng viên hướng dẫn là chữ giữ chỗ `ICTU_TEACHER`, không phải tên thật | Đây là lý do có tính năng **Gợi ý người hướng dẫn (AI)** — một cách để dần thay thế chữ giữ chỗ này bằng liên kết thật, có người xác nhận |

### 1.3 Ai dùng hệ thống — 5 vai trò

Hệ thống hiện có 5 vai trò người dùng. Một tài khoản có thể mang nhiều vai trò cùng lúc
(ví dụ vừa `rd_officer` vừa `lecturer`); khi đó tài khoản có quyền rộng nhất trong các vai
trò mình có.

| Vai trò | Mã trong hệ thống | Tóm tắt quyền |
|---|---|---|
| **Phòng KH-CN** | `rd_officer` | Toàn quyền trên toàn trường: mở/đóng/huỷ/chốt kỳ báo cáo, kiểm tra hồ sơ kê khai của mọi khoa, xử lý hàng đợi tác giả và nghi trùng, chỉnh tay dữ liệu công trình (có xuất xứ), bỏ qua cảnh báo bất thường, xem báo cáo và đơn vị bất kỳ. Giao diện gọi vai trò này là **"Chuyên viên KHCN"** ở các nút và tooltip (ví dụ tooltip **"Cần vai trò Chuyên viên KHCN"** khi bạn chưa đủ quyền) |
| **Chuyên viên khoa** | `faculty_officer` | Kê khai công trình và trình khoa duyệt, chỉ trong phạm vi đơn vị mình được gán — phạm vi này lọc ở tầng cơ sở dữ liệu, không chỉ ẩn trên giao diện |
| **Trưởng khoa** | `faculty_head` | Duyệt hoặc trả lại hồ sơ **của khoa mình**; không tự lập hồ sơ, không sửa nội dung công trình |
| **Giảng viên** | `lecturer` | Tự kê khai công trình đã liên kết với chính mình (`/ke-khai-cua-toi/`), tự xác nhận liên kết tác giả của mình, dùng đối chiếu đề tài và rà soát theo khoá |
| **Lãnh đạo** | `school_leader` | Xem tổng quan, khoa theo mọi đơn vị, chất lượng dữ liệu — không xử lý hàng đợi, không chỉnh dữ liệu, không chốt kỳ |

Bộ tài liệu phân tích nghiệp vụ (`docs/ba/05-permissions.md`) còn phác thảo thêm các vai
trò `student`, `admin`, `department_head` cho một mô hình rộng hơn trong tương lai; bản hệ
thống hiện tại (v0.6.0) chỉ triển khai 5 vai trò ở trên. Sinh viên dùng hệ thống qua **cổng
công khai** (mục 2.7) mà không cần tài khoản.

### 1.4 Đăng nhập

Hệ thống có hai chế độ:

- **Chế độ mở** (mặc định lúc mới cài): chưa ai được đặt mật khẩu. Không cần đăng nhập, hệ
  thống tự coi bạn là người dùng `rd_officer` đầu tiên trong danh sách — phù hợp lúc cài
  đặt hoặc trình diễn, **không phù hợp** để chạy công khai.
- **Chế độ bắt buộc đăng nhập**: ngay khi có một tài khoản được đặt mật khẩu (bằng
  `python -m cris user set-password`), toàn hệ thống chuyển sang bắt buộc đăng nhập cho mọi
  người. Trang **/dang-nhap/** có ô **Email** và **Mật khẩu**, nút **Đăng nhập**. Phiên đăng
  nhập là cookie `cris_session` (`HttpOnly`), hết hạn sau 12 giờ; đăng nhập sai quá 5 lần
  trong 5 phút cho cùng một email sẽ bị khoá tạm thời (429).

**Quên mật khẩu?** Bạn không tự đặt lại được trên giao diện — liên hệ **Phòng KH-CN**, họ
chạy lệnh dòng lệnh `python -m cris user set-password <email của bạn>` trên máy chủ để đặt
mật khẩu mới cho bạn (xem mục 7).

Trang đăng nhập cũng có hai liên kết phụ: **"Sinh viên: kiểm tra đề tài không cần tài
khoản"** (đưa tới cổng công khai) và **"Xem hướng dẫn sử dụng"** (đưa tới trang hướng dẫn
trong ứng dụng).

### 1.5 Bố cục màn hình

- **Thanh bên (sidebar)**, cố định bên trái trên máy tính (menu rút gọn qua nút **☰** trên
  điện thoại): logo ICTU-CRIS ở trên cùng, rồi tới danh sách điều hướng theo thứ tự
  **Tổng quan**, (**Kê khai của tôi** — chỉ hiện với giảng viên), **Tra cứu**, **Chủ đề**,
  **Bản đồ tri thức**, **Đối chiếu đề tài**, **Hàng đợi tác giả**, **Hàng đợi nghi trùng**,
  **Kỳ báo cáo**, **Chất lượng dữ liệu**, **Đồng bộ**, **Nhật ký**, **Về hệ thống**,
  **Hướng dẫn**. Nếu tài khoản gắn với một đơn vị hoặc có quyền xem mọi đơn vị, mục
  **Khoa của tôi** (hoặc **Theo khoa**) chèn thêm ngay sau **Kê khai của tôi**. Cuối thanh
  bên là liên kết **"Kiểm tra đề tài công khai"** rồi tới khối tài khoản (tên, vai trò, nút
  đăng xuất) hoặc nút **Đăng nhập** nếu chưa vào phiên.
- **Thanh trên (topbar)**: nút mở menu (điện thoại), tiêu đề trang hiện tại, ô **"Tìm nhanh
  công trình…"** (gõ rồi Enter để nhảy thẳng sang `/tra-cuu/` với từ khoá đó), chuông
  **Thông báo**, nút đổi **sáng/tối** (biểu tượng mặt trời/mặt trăng).
- **Chuông thông báo**: hiện số thông báo chưa đọc (tối đa hiển thị "99+"); bấm mở danh
  sách 8 thông báo gần nhất, bấm một dòng để mở đúng hồ sơ/báo cáo liên quan và tự đánh dấu
  đã đọc; nút **"Xem tất cả"** đưa sang trang `/thong-bao/` đầy đủ.
- **Banner tình trạng hệ thống**: chỉ Phòng KH-CN thấy, hiện khi mô hình AI cục bộ chưa
  nạp — dòng cảnh báo màu vàng nhắc chạy `python -m cris ai download`.
- **Chân trang (footer)**: cố định ở đáy màn hình, một dòng ghi rõ dữ liệu lấy từ DSpace
  của Trường CNTT&TT – ĐH Thái Nguyên (`repository.ictu.edu.vn`), **chỉ nhằm mục đích học
  tập**, cùng liên kết tới mã nguồn Apache-2.0 trên GitHub.

Hai trang không dùng bố cục có thanh bên: **/kiem-tra-de-tai/** (cổng công khai) và
**/giang-vien/ly-lich/** (lý lịch khoa học in được) — cả hai hiển thị toàn màn hình để phù
hợp với việc chia sẻ hoặc in.

### 1.6 Quy ước chung

- **Badge trạng thái**: mỗi trạng thái (liên kết tác giả, nhóm nghi trùng, kỳ báo cáo, hồ sơ
  kê khai, lượt đồng bộ…) luôn hiện dưới dạng một huy hiệu màu kèm đúng nhãn tiếng Việt của
  nó (ví dụ **Chờ xác nhận**, **Đã gộp**, **Đang mở**, **Đã chốt**) — không hiện mã kỹ thuật
  (`ChoXacNhan`, `DaGop`…) cho người dùng.
- **Ô bắt buộc**: mọi ô cần điền trước khi bấm nút đều có dấu **`*`** màu đỏ cạnh nhãn, ví
  dụ **Lý do \***. Thiếu ô này, nút submit vẫn bấm được nhưng hệ thống báo lỗi và không lưu.
- **Thông báo lỗi**: hiện dưới dạng hộp cảnh báo màu đỏ phía trên biểu mẫu hoặc toast (thông
  báo nổi góc màn hình) với câu tiếng Việt cụ thể; hầu hết có thêm nút **"Thử lại"**.
- **Trạng thái rỗng**: khi một danh sách chưa có dữ liệu, trang hiện một khối văn bản giải
  thích lý do (ví dụ *"Chưa có cụm chủ đề — hãy chạy quy trình phân tích chủ đề rồi tải lại
  trang"*) thay vì một bảng trống không giải thích gì.
- **Chế độ tối**: bấm biểu tượng mặt trời/mặt trăng ở thanh trên để đổi giữa giao diện sáng
  và tối; lựa chọn được nhớ cho lần sau.
- **In**: hai trang thiết kế để in trực tiếp bằng `Ctrl/Cmd+P` (hoặc nút **In / Lưu PDF**) —
  **Lý lịch khoa học** (khổ A4) và trang **Báo cáo đóng băng** (nút **In**, ẩn thanh hành
  động khi in).

---

## 2. Mục lục tính năng theo menu

### 2.1 Tổng quan

**Tính năng này là gì.** Trang mở đầu (`/tong-quan/`) trả lời "hệ thống đang ở đâu" bằng số
liệu 5 năm gần nhất, không cần mở từng màn con — đúng như cách một lãnh đạo muốn thấy bức
tranh chung trước khi đi vào chi tiết.

**Cung cấp gì.**
- Bốn thẻ số đầu trang: **Tổng công trình 5 năm**, **Công trình có liên kết tác giả** (%),
  **Liên kết tác giả chờ xác nhận** (bấm vào để mở thẳng Hàng đợi tác giả), **Nhóm nghi
  trùng đang mở** (bấm vào để mở Hàng đợi nghi trùng).
- Khối **"Mới cập nhật từ kho"**: hai cột **Thêm** và **Đổi** liệt kê công trình vừa thêm
  mới hoặc thay đổi ở lượt đồng bộ gần nhất, cùng nút **"Xem lịch sử đồng bộ"** và nút
  **RSS** (mở `/api/feed.xml` — nguồn cấp dữ liệu công khai cho công cụ theo dõi bên ngoài).
- Biểu đồ cột chồng **"Công trình theo năm và loại tài liệu"**, kèm dòng chú thích số công
  trình "không rõ năm" nằm ngoài biểu đồ.
- Bảng **"Công trình theo đơn vị"** (mã, tên, số công trình).
- Bảng **"10 giảng viên có nhiều công trình nhất"** — bấm tên để mở hồ sơ giảng viên.
- Dòng chân trang ghi thời điểm đồng bộ lần cuối.

**Cách sử dụng.**
1. Mở `/tong-quan/` (trang mặc định sau khi vào hệ thống).
2. Đọc bốn thẻ số ở đầu trang; bấm vào **Liên kết tác giả chờ xác nhận** hoặc **Nhóm nghi
   trùng đang mở** để nhảy thẳng sang hàng đợi tương ứng.
3. Cuộn xuống biểu đồ theo năm và loại tài liệu, đọc dòng chú thích dưới biểu đồ.
4. Xem bảng theo đơn vị và top giảng viên; bấm tên một giảng viên để mở hồ sơ của họ.

**Ai được dùng.** Mọi vai trò đã đăng nhập (hoặc mọi người nếu hệ thống đang ở chế độ mở) —
trang chỉ đọc, không có thao tác quyết định nào.

**Lưu ý / giới hạn.**
- Biểu đồ theo năm **chỉ vẽ được cho bài báo** — đồ án/luận văn/luận án không có năm xuất
  bản đáng tin ở nguồn, nên bị đếm riêng vào nhóm "không rõ năm" thay vì đoán năm.
- Số liệu luôn tính trên **5 năm gần nhất có dữ liệu**, không phải toàn bộ lịch sử kho.

**Ảnh.** `docs/huong-dan/tong-quan.png` (máy tính), `docs/huong-dan/tong-quan-dien-thoai.png`
(điện thoại).

---

### 2.2 Tra cứu

**Tính năng này là gì.** Trang `/tra-cuu/` là nơi tìm công trình theo hai cách: **Theo từ
khoá** (khớp chuỗi, kể cả gõ không dấu) hoặc **Theo nghĩa (AI)** (tìm câu gần nghĩa dù không
trùng từ), kèm bộ lọc và xuất CSV.

**Cung cấp gì.**
- Công tắc **"Theo từ khoá"** / **"Theo nghĩa (AI)"** ngay cạnh ô tìm.
- Ô **Từ khoá** (placeholder đổi theo chế độ: *"Tiêu đề (không dấu cũng được) hoặc tên tác
  giả…"* ở chế độ từ khoá, *"Mô tả điều bạn tìm, ví dụ: app dạy trẻ phát âm"* ở chế độ AI).
- Bộ lọc chính: **Loại tài liệu**, **Năm**, **Đơn vị**, **Chủ đề** (mỗi lựa chọn kèm số
  lượng công trình khớp, ví dụ *"Bài báo (1.907)"*).
- Khung **"Bộ lọc nâng cao"** (đóng mặc định, bấm mở): **Loại bài/chỉ mục**, **Quartile**,
  **Khoá**.
- Chip từ khoá: mỗi công trình trong bảng kết quả hiện tối đa 3 từ khoá dạng huy hiệu, bấm
  vào một từ khoá để lọc tiếp theo đúng từ khoá đó.
- Nút **Tải CSV** (tải đúng tập kết quả đang lọc, UTF-8 có BOM, mở được ngay bằng Excel).
- Nút **Tra cứu** (chạy tìm kiếm) và **Xoá bộ lọc**.
- Bảng kết quả: cột **Công trình** (tiêu đề + DOI nếu có + chip từ khoá), cột **Độ gần**
  (chỉ hiện ở chế độ AI — thanh phần trăm), **Loại**, **Năm**, **Trạng thái**.

**Cách sử dụng.**
1. Gõ từ khoá vào ô tìm; giữ mặc định **Theo từ khoá** hoặc bấm **Theo nghĩa (AI)** nếu
   muốn tìm theo mô tả gần nghĩa.
2. Chọn thêm **Loại tài liệu**, **Năm**, **Đơn vị**, **Chủ đề** nếu cần; mở **Bộ lọc nâng
   cao** để lọc theo chỉ mục/quartile/khoá.
3. Bấm **Tra cứu**. Bảng kết quả cập nhật theo trang (phân trang 50 dòng).
4. Bấm tiêu đề một công trình để mở chi tiết; bấm một chip từ khoá để lọc theo đúng từ khoá
   đó; bấm **Tải CSV** để xuất danh sách đang lọc.

**Ai được dùng.** Công khai — không cần đăng nhập để tra cứu.

**Lưu ý / giới hạn.**
- Ở chế độ **Theo nghĩa (AI)**, kết quả chỉ tìm trong **top-200 công trình gần nghĩa nhất**
  trước khi lọc tiếp bằng các bộ lọc khác — một đề tài rất hiếm gặp có thể nằm ngoài top-200
  dù đúng nghĩa và không hiện ra.
- Khi AI chưa bật (`CRIS_AI_PROVIDER=none`), chế độ **Theo nghĩa (AI)** tự rơi về tìm theo
  từ khoá và hiện dòng giải thích *"AI chưa bật — tìm theo từ khoá."* — không bao giờ báo
  lỗi.
- Bộ lọc **Loại tài liệu** chỉ liệt kê 5 loại công bố (Bài báo, Đồ án, Luận văn, Luận án,
  Học liệu) — hai loại nội bộ "Giảng viên" và "Đăng ký đồ án" không xuất hiện ở đây.

**Ảnh.** `docs/huong-dan/tra-cuu.png`.

---

### 2.3 Chi tiết công trình

**Tính năng này là gì.** Trang `/cong-trinh/?id=` cho một công trình, trả lời câu hỏi "số
này ở đâu ra": giữ song song giá trị đang dùng, giá trị gốc từ kho, và ai đã đổi nó nếu có.

**Cung cấp gì.**
- Bảng **"Xuất xứ dữ liệu"** — 4 cột: **Trường**, **Giá trị đang dùng**, **Giá trị gốc**,
  **Nguồn**. Dòng "Nguồn" ghi rõ *"Chỉnh tay bởi … lúc …"* nếu trường đó từng bị sửa tay,
  ngược lại ghi nguồn gốc (kho dữ liệu ICTU, bảng tính khoa, phiếu đăng ký…).
- Bảng **"Tác giả"** — vị trí, tên trong nguồn, vai trò (tác giả/người hướng dẫn/sinh viên
  thực hiện…), giảng viên liên kết (hoặc **"Chưa liên kết"**), trạng thái liên kết.
- Badge **"Đã chỉnh tay"** nếu công trình có ít nhất một trường bị sửa tay; cảnh báo màu
  vàng **"Cần đối soát"** nếu công trình còn cần người dùng kiểm tra.
- Nút **Trích dẫn** — mở hộp thoại 3 tab **APA** / **IEEE** / **BibTeX**, nút **Sao chép**
  và **Tải .bib**.
- Nút **"Mở PDF ở kho"** nếu công trình có PDF; liên kết **"Lịch sử chỉnh sửa"** đưa sang
  trang Nhật ký nếu công trình từng bị sửa tay.
- Với **Phòng KH-CN**: một icon bút chì cạnh mỗi dòng trong bảng xuất xứ thuộc 9 trường
  được phép sửa, mở hộp thoại chỉnh sửa.

**Cách sử dụng.**
1. Mở một công trình từ Tra cứu, Tổng quan, hàng đợi, hoặc hồ sơ giảng viên.
2. Đọc bảng **Xuất xứ dữ liệu** để biết giá trị đang dùng khác giá trị gốc chỗ nào và vì
   sao.
3. Bấm **Trích dẫn**, chọn tab định dạng, bấm **Sao chép** hoặc **Tải .bib**.
4. (Chỉ Phòng KH-CN) Bấm icon bút chì cạnh một trường được phép sửa, nhập **Giá trị mới \***
   và **Lý do \***, bấm **Lưu chỉnh sửa**. Dòng "Nguồn" đổi ngay thành *"Chỉnh tay bởi … lúc
   …"*; cột **Giá trị gốc** không đổi.

**Ai được dùng.** Xem: mọi người. Chỉnh tay: chỉ **Phòng KH-CN** (`rd_officer`) — người
khác thấy nút bị ẩn hoặc vô hiệu hoá.

**Lưu ý / giới hạn.**
- Chỉ **9 trường** được phép chỉnh tay: **tiêu đề, DOI, năm/số, tạp chí, tập, loại bài,
  khoá, tóm tắt, từ khoá**. Tác giả, đơn vị và minh chứng **không** sửa được ở đây — sai thì
  trả hồ sơ về khoa (BR-23).
- Mọi lần sửa bắt buộc **Lý do**; hệ thống ghi lại người sửa, thời điểm, giá trị cũ — không
  bao giờ ghi đè lên giá trị gốc lấy từ kho.
- Công trình đã bị gộp vào bản ghi khác thì không chỉnh tay được nữa.

**Ảnh.** `docs/huong-dan/chi-tiet-cong-trinh.png`.

---

### 2.4 Chủ đề

**Tính năng này là gì.** Trang `/chu-de/` liệt kê các cụm chủ đề do AI gom từ toàn bộ từ
khoá trong kho (thuật toán k-means), giúp bạn duyệt công trình theo hướng nghiên cứu thay
vì phải nhớ đúng từ khoá.

**Cung cấp gì.**
- Danh sách thẻ, mỗi thẻ là một cụm chủ đề: nhãn cụm (từ khoá phổ biến nhất trong cụm), một
  số từ khoá đại diện, và số công trình thuộc cụm — sắp xếp giảm dần theo số công trình.
- Trang chi tiết `/chu-de/chi-tiet/?id=`: khối **"Từ khoá và trọng số"** (thanh dài hơn = từ
  khoá nặng hơn trong cụm) và bảng **"Công trình thuộc chủ đề"**.
- Nút **"Tra cứu theo chủ đề này"** đưa thẳng sang `/tra-cuu/?topic=` đã lọc sẵn.

**Cách sử dụng.**
1. Mở `/chu-de/`, đọc các thẻ cụm chủ đề.
2. Bấm một thẻ để xem chi tiết: từ khoá đại diện và danh sách công trình.
3. Bấm **"Tra cứu theo chủ đề này"** để lọc toàn bộ công trình thuộc cụm ở trang Tra cứu.

**Ai được dùng.** Công khai.

**Lưu ý / giới hạn.**
- Cố định **40 cụm** (k-means) trên toàn bộ từ khoá của kho — cụm chỉ để định hướng, nhãn
  cụm là từ khoá tần suất cao nhất, **không thay** từ khoá gốc của công trình.
- Cần đã chạy `python -m cris ai topics` thì trang mới có dữ liệu; chưa chạy thì trang hiện
  trạng thái rỗng.

**Ảnh.** Chưa có ảnh minh hoạ riêng.

---

### 2.5 Bản đồ tri thức

**Tính năng này là gì.** Trang `/ban-do/` chiếu 2 chiều (PCA) toàn bộ vector ngữ nghĩa của
công trình lên một canvas, để nhìn toàn cảnh hướng nghiên cứu và mạng lưới hợp tác — có 3
tab: **Bản đồ**, **Xu hướng**, **Đồng tác giả**.

**Cung cấp gì.**
- Tab **Bản đồ**: canvas các điểm (mỗi điểm là một công trình), ô **"Tìm nhanh trên bản
  đồ"**, chọn **"Tô màu theo"** — **Chủ đề** (mặc định) / **Đơn vị** / **Năm** / **Loại tài
  liệu**; cuộn/chụm để phóng to, kéo để di chuyển, bấm một điểm để mở chi tiết công trình.
- Tab **Xu hướng**: chọn trục **"Theo khoá"** / **"Theo năm"**, cách tính **"Số lượng"** /
  **"Tỉ lệ %"**, chọn tối đa 6 cụm chủ đề để so sánh trên biểu đồ vùng xếp chồng và bảng số
  liệu bên dưới.
- Tab **Đồng tác giả**: đồ thị mạng — nút là giảng viên, cạnh nối hai giảng viên từng cùng
  đứng tên ít nhất một công trình; lọc **"Theo đơn vị"**; bấm một nút để mở hồ sơ giảng
  viên.

**Cách sử dụng.**
1. Mở `/ban-do/`, tab **Bản đồ** mặc định hiện toàn bộ công trình tô theo chủ đề.
2. Đổi **"Tô màu theo"** sang tiêu chí khác nếu muốn nhìn theo góc khác; gõ vào ô tìm nhanh
   để định vị một công trình cụ thể; bấm một điểm để mở chi tiết.
3. Chuyển tab **Xu hướng**, chọn trục thời gian và tối đa 6 cụm chủ đề để so sánh xu hướng.
4. Chuyển tab **Đồng tác giả**, lọc theo đơn vị nếu cần, bấm một nút để mở hồ sơ giảng viên
   tương ứng.

**Ai được dùng.** Công khai.

**Lưu ý / giới hạn.**
- Đây **không phải một phép đo chính xác** — chỉ 2 trong 384 chiều gốc của vector ngữ
  nghĩa, dùng để định hướng "vùng nào gần vùng nào", **không** dùng để so khoảng cách tuyệt
  đối hay kết luận hai công trình giống nhau bao nhiêu phần trăm.
- Đo trên dữ liệu thật: 7.618 điểm, 39 cụm chủ đề, dựng trong 9,7 giây; kết quả trả về nén
  gzip còn khoảng 316 KB (từ ~1,5 MB chưa nén).
- Tab Xu hướng chỉ hiện tối đa **6 cụm** cùng lúc trên biểu đồ, mặc định hiện sẵn 4 cụm lớn
  nhất.
- Tab Đồng tác giả chỉ tính giảng viên có từ 2 công trình liên kết trở lên, và cắt tối đa
  300 nút để đồ thị còn đọc được.
- Cần đã chạy `python -m cris ai map` (sau `ai embed` và `ai topics`) thì bản đồ mới có dữ
  liệu.

**Ảnh.** Chưa có ảnh minh hoạ riêng.

---

### 2.6 Đối chiếu đề tài

Nhóm ba tính năng dùng chung một bộ tab điều hướng ở đầu trang: **Đối chiếu một đề tài** /
**Rà soát theo khoá** / **Tìm chuyên gia**.

#### 2.6.1 Đối chiếu một đề tài

**Tính năng này là gì.** Trang `/doi-chieu/` gợi ý các công trình đã có trong kho gần với
một đề tài dự kiến, so sánh theo bốn khía cạnh riêng biệt thay vì một con số tổng hợp.

**Cung cấp gì.**
- Ô **Tiêu đề đề tài \*** (ít nhất 3 ký tự) và **Mô tả**.
- Bốn ô khía cạnh (không bắt buộc): **Bài toán**, **Đối tượng**, **Phạm vi**, **Phương
  pháp**.
- Bộ lọc **Loại tài liệu** (chọn nhiều).
- Nút **Đối chiếu đề tài**.
- Kết quả: hộp **"Phạm vi kết quả"** luôn ghi *"So trên tiêu đề, tóm tắt và từ khoá — không
  phải toàn văn"*; mỗi công trình gợi ý kèm ma trận 4 khía cạnh, mỗi ô là **Cao** / **Vừa** /
  **Thấp** / **Chưa đủ dữ liệu** — **không có điểm phần trăm tổng hợp**.

**Cách sử dụng.**
1. Nhập **Tiêu đề đề tài \***, **Mô tả**, và điền các khía cạnh nếu biết.
2. Chọn **Loại tài liệu** cần so nếu muốn thu hẹp phạm vi.
3. Bấm **Đối chiếu đề tài**. Đọc hộp "Phạm vi kết quả" trước khi xem danh sách.
4. Với mỗi kết quả, xem ma trận 4 khía cạnh — tự đánh giá, hệ thống không kết luận "trùng"
   hay "mới".

**Ai được dùng.** Công khai (không cần đăng nhập để chạy đối chiếu; kết quả lưu lại có thể
chia sẻ qua đường link `?id=`).

**Lưu ý / giới hạn.**
- Ngưỡng khía cạnh (`≥0,55` giống, `≤0,35` khác) là **mặc định của thư viện, chưa hiệu
  chỉnh** trên tập gán tay — khác với ngưỡng của mục 2.6.2 đã được hiệu chỉnh cẩn thận.
- Không có điểm phần trăm tổng hợp là **chủ ý thiết kế** (BR-17): một con số duy nhất dễ
  tạo cảm giác kết luận sai.

**Ảnh.** `docs/huong-dan/doi-chieu-de-tai.png`.

#### 2.6.2 Rà soát trùng đề tài theo khoá

**Tính năng này là gì.** Trang `/doi-chieu/ra-soat/` so đề tài đồ án của **một khoá** với
toàn bộ các khoá trước, gắn cờ theo mức cao/vừa/thấp — vì kho không có bảng đăng ký đề tài
nên không rà được ngay lúc sinh viên đăng ký.

**Cung cấp gì.**
- Ô chọn **Khoá** (nhãn kèm số liệu, ví dụ *"Khoá 2021 — 529 đồ án, 47 gắn cờ"*).
- Ô chọn **Mức tối thiểu** — **Cao** hoặc **Vừa**.
- Ô **Điểm tối thiểu (tuỳ chọn)** (0–1, ví dụ 0,90).
- Mỗi kết quả: nhãn mức (**Cao** / **Vừa** / **Thấp**), điểm **"Tương đồng tóm tắt"**, danh
  sách láng giềng ở khoá khác kèm điểm số, nút **"Đối chiếu chi tiết"** (điền sẵn tiêu đề
  sang màn 2.6.1).

**Cách sử dụng.**
1. Mở `/doi-chieu/ra-soat/`, chọn **Khoá** cần xem.
2. Chọn **Mức tối thiểu** (mặc định **Cao**); nhập thêm **Điểm tối thiểu** nếu muốn lọc chặt
   hơn.
3. Đọc từng kết quả: mức, điểm, danh sách láng giềng ở khoá khác.
4. Bấm **"Đối chiếu chi tiết"** trên một kết quả để xem đủ 4 khía cạnh ở màn 2.6.1.

**Ai được dùng.** Công khai — kết quả chỉ đọc, đã được tính sẵn bằng lệnh
`python -m cris ai screen --cohort <mã khoá>`, trang này không tự chạy AI khi bạn mở nó.

**Lưu ý / giới hạn.**
- Ngưỡng **0,90 (Cao) / 0,80 (Vừa)** được hiệu chỉnh trên phân bố điểm thật của 529 đồ án
  khoá 21 (phân vị p50=0,835 · p90=0,897 · p99=0,928), không phải số mặc định — ngưỡng cũ kế
  thừa từ đối chiếu đề tài (0,55/0,35) từng gắn cờ 100% đồ án, vô dụng.
- Ở cohort 21: 47/529 đồ án (8,9%) được gắn cờ mức Cao.
- Chỉ khía cạnh **Bài toán** của mỗi láng giềng có mức tính được; ba khía cạnh còn lại luôn
  hiện **"Chưa đủ dữ liệu"** vì không có mô tả khía cạnh riêng để so.
- Đây **không phải kiểm tra đạo văn** — chỉ là gợi ý để giảng viên xem lại; không có hành
  động gộp/xoá nào chạy tự động dù mức là Cao.
- Ngưỡng hiệu chỉnh cho **một cohort, một mô hình** — đổi mô hình hoặc rà một cohort khác có
  thể cần đo lại.

**Ảnh.** `docs/huong-dan/ra-soat-theo-khoa.png`.

#### 2.6.3 Tìm chuyên gia

**Tính năng này là gì.** Trang `/doi-chieu/chuyen-gia/` gợi ý giảng viên gần chuyên môn nhất
với một đề tài, dựa trên các công trình đã liên kết của họ — dùng để thu hẹp danh sách liên
hệ khi tìm người phản biện, hướng dẫn, hoặc hợp tác.

**Cung cấp gì.**
- Ô **Tiêu đề đề tài \*** và **Mô tả**.
- Khung **"Bộ lọc nâng cao"**: **Học vị tối thiểu** (Không giới hạn / Thạc sĩ / Tiến sĩ),
  **Đơn vị**, **Loại trừ giảng viên** (gõ tên để loại một người khỏi kết quả).
- Nút **Tìm chuyên gia**; nút **"Sao chép danh sách"** và **"Chia sẻ"** trên kết quả.
- Mỗi thẻ kết quả: tên, học vị, đơn vị, số bài liên quan, thanh **"Mức phù hợp tương đối"**,
  và **"Ba dẫn chứng gần nhất"** (công trình + điểm).

**Cách sử dụng.**
1. Nhập **Tiêu đề đề tài \*** và **Mô tả**.
2. Mở **Bộ lọc nâng cao** nếu cần giới hạn học vị, đơn vị, hoặc loại trừ một vài người.
3. Bấm **Tìm chuyên gia**. Đọc dẫn chứng của từng người trước khi liên hệ.
4. Dùng **"Sao chép danh sách"** hoặc **"Chia sẻ"** để gửi kết quả cho người khác.

**Ai được dùng.** Cần đăng nhập khi hệ thống đang bắt buộc đăng nhập (mọi vai trò dùng
được); kết quả đã lưu có thể xem lại qua đường link `?id=` mà không cần đăng nhập.

**Lưu ý / giới hạn.**
- Đo trên 30 đồ án có người hướng dẫn thật (che tên rồi hỏi lại): đúng vị trí đầu **23,3%**
  (7/30), nằm trong 5 gợi ý đầu **46,7%** (14/30) — nghĩa là **hơn một nửa số ca**, người
  hướng dẫn thật không nằm trong top-5. Đây là suy luận từ tương đồng đề tài, **không phải**
  đánh giá năng lực hay "AI đoán đúng người hướng dẫn".
- Thanh **"Mức phù hợp"** chỉ có ý nghĩa **tương đối trong danh sách đang xem**, không phải
  một con số tuyệt đối so được giữa các lượt tìm khác nhau.
- Chỉ tính trên công trình **đã liên kết** trong kho — giảng viên có công trình gần đề tài
  nhưng còn ở hàng đợi tác giả chưa được tính.
- Kết quả ưu tiên nhẹ công trình trong 3 năm gần đây.

**Ảnh.** Chưa có ảnh minh hoạ riêng.

---

### 2.7 Cổng kiểm tra đề tài công khai

**Tính năng này là gì.** Trang `/kiem-tra-de-tai/` — **công khai, không cần tài khoản** —
cho sinh viên tự nhập đề tài dự kiến trước khi đăng ký chính thức, xem đề tài tương tự các
khoá trước và giảng viên gần chuyên môn.

**Cung cấp gì.**
- Trang riêng, không có thanh bên — chỉ có nút **"Vào hệ thống"** ở góc trên.
- Ô **"Tên đề tài dự định \*"** (ít nhất 5 ký tự) và **"Mô tả (tuỳ chọn)"**.
- Nút **Kiểm tra**.
- Hai cột kết quả: **"Đề tài tương tự các khoá trước"** (nhãn mức Cao/Vừa/Thấp, khoá, năm)
  và **"Giảng viên gần chuyên môn"** (tên, học vị, đơn vị — **không có** email/điện thoại).

**Cách sử dụng.**
1. Vào thẳng `/kiem-tra-de-tai/` (không cần đăng nhập).
2. Nhập **"Tên đề tài dự định"**, có thể thêm mô tả.
3. Bấm **Kiểm tra**.
4. Xem đề tài tương tự các khoá trước (mức Cao là rất giống, nên đổi hướng hoặc trao đổi
   với giảng viên hướng dẫn) và danh sách giảng viên gần chuyên môn.

**Ai được dùng.** Bất kỳ ai, kể cả không có tài khoản — chủ yếu dành cho sinh viên.

**Lưu ý / giới hạn.**
- Giới hạn **20 lượt/5 phút cho mỗi địa chỉ IP**; vượt quá sẽ bị từ chối tạm thời cho tới
  khi hết 5 phút.
- **Không lưu lại lượt tra cứu nào** — kết quả không có đường link chia sẻ như các trang đối
  chiếu khác dành cho người đã đăng nhập.
- Kết quả giảng viên chỉ gồm tên, học vị, đơn vị, điểm gần chuyên môn — **không bao giờ**
  hiện email hay số điện thoại.
- Kết quả không thay thế việc trao đổi trực tiếp với giảng viên hướng dẫn.

**Ảnh.** Chưa có ảnh minh hoạ riêng.

---

### 2.8 Hàng đợi tác giả

**Tính năng này là gì.** Trang `/doi-soat/tac-gia/` là nơi xử lý mọi lượt tên tác giả trong
kho chưa được nối chắc chắn với một giảng viên — đây là hàng đợi trung tâm vì liên kết tác
giả ở kho gốc chỉ phủ 8%, còn nhiều việc cần người xác nhận.

**Cung cấp gì.**
- Bốn tab trạng thái kèm số đếm: **Chờ xác nhận** (mặc định), **Đã nối tự động**, **Đã xác
  nhận**, **Đã bác bỏ**.
- Ô tìm **"Tìm theo tên thô…"**.
- Bảng: **Tên thô**, **Công trình**, **Ứng viên**, **Tin cậy** (huy hiệu, ví dụ *"Khớp
  ORCID"*, *"Tên đầy đủ, một ứng viên"*, hoặc *"AI đề xuất (hướng dẫn)"* nếu ứng viên tới từ
  mục 2.8.1), **Học vị** (kèm cảnh báo nếu có xung đột trong nguồn), **Cùng tên** (số lượt
  tên trùng), **Gợi ý AI** (huy hiệu *"gợi ý · hạng {n}"* kèm lý do bằng lời, ví dụ *"3 công
  trình đã xác nhận của người này cùng chủ đề"*).
- Chọn nhiều dòng bằng ô tick, thanh hành động nổi lên ở đáy màn hình với 3 nút: **Xác
  nhận**, **Bác bỏ**, **Chuyển cho người khác**.

**Cách sử dụng.**
1. Mở tab **Chờ xác nhận** (mặc định).
2. Đọc cột **Tin cậy** và **Gợi ý AI** — đây chỉ là gợi ý, bạn tự quyết định.
3. Tick chọn một hoặc nhiều dòng đã kiểm tra là đúng, bấm **Xác nhận** ở thanh hành động.
4. Với dòng sai, bấm **Bác bỏ**, nhập **Lý do \*** bắt buộc rồi xác nhận trong hộp thoại.
5. Với dòng cần chuyển cho người khác xử lý, bấm **Chuyển cho người khác**, chọn **Người
   nhận \*** (tìm theo tên), có thể ghi lý do (tuỳ chọn).

**Ai được dùng.** Xem: mọi người đã đăng nhập. Quyết định (Xác nhận/Bác bỏ/Chuyển): chỉ
**Phòng KH-CN** (`rd_officer`) — nút bị vô hiệu hoá với người khác, kèm tooltip **"Cần vai
trò Chuyên viên KHCN"**.

**Lưu ý / giới hạn.**
- Đo trên dữ liệu thật: **903 liên kết** đang chờ xác nhận; nối tự động 3.135 lượt; bài báo
  đạt 86,6% có liên kết (78,8% tự động + 15,9% chờ xác nhận), so với 8% ở nguồn.
- Chỉ hai mức tin cậy cao nhất (khớp ORCID, khớp tên đầy đủ duy nhất) được **nối tự động**;
  mọi trường hợp còn lại luôn vào hàng đợi chờ người xác nhận.
- AI chỉ **xếp hạng** ứng viên và giải thích vì sao — không có nút nào tự nối tác giả.

**Ảnh.** `docs/huong-dan/hang-doi-tac-gia.png`, `docs/huong-dan/hang-doi-dien-thoai.png`
(điện thoại).

#### 2.8.1 Gợi ý người hướng dẫn (AI)

**Tính năng này là gì.** Tab thứ hai của Hàng đợi tác giả, tại `/doi-soat/huong-dan/` —
dành riêng cho các đồ án đang ghi người hướng dẫn là chữ giữ chỗ `ICTU_TEACHER` (4.621/5.375
đồ án, 86%). AI tìm đồ án cùng đề tài đã có người hướng dẫn thật, xếp hạng ứng viên.

**Cung cấp gì.**
- Bộ lọc **Đơn vị** và **Số phiếu tối thiểu** (mặc định 2, phải là số nguyên ≥ 1).
- Bảng: **Đồ án** (kèm khoá), **Ứng viên** (kèm học vị), **Phiếu**, **Điểm**, **Đồ án dẫn
  chứng** (tối đa 2), cột **Hành động** — nút **"Đưa vào hàng đợi"**, hoặc nếu đã đưa rồi thì
  hiện **"Đang chờ xác nhận"** (đưa bạn sang tab Hàng đợi tác giả).

**Cách sử dụng.**
1. Mở `/doi-soat/huong-dan/`. Đọc dòng đầu trang: bao nhiêu đồ án đang ghi `ICTU_TEACHER` và
   AI gợi ý được cho bao nhiêu đồ án.
2. Lọc theo **Đơn vị** nếu cần; đổi **Số phiếu tối thiểu** nếu muốn siết hoặc nới điều kiện.
3. Với một đồ án, xem ứng viên hàng đầu (điểm cao nhất) và đồ án dẫn chứng của họ.
4. Bấm **"Đưa vào hàng đợi"** — hệ thống tạo một liên kết **đang chờ xác nhận** (không tự
   xác nhận); liên kết này hiện đúng ở Hàng đợi tác giả (mục 2.8) để xử lý tiếp.

**Ai được dùng.** Xem: mọi người đã đăng nhập. Đưa vào hàng đợi: chỉ **Phòng KH-CN**.

**Lưu ý / giới hạn.**
- Đo trên dữ liệu thật: AI gợi ý được cho **1.381/4.621 đồ án (29,9%)** có ít nhất một ứng
  viên qua ngưỡng (`k=5, số phiếu tối thiểu=2, điểm tối thiểu=0,70`).
- Giả định của tính năng — *"đồ án cùng đề tài thường do cùng một giảng viên hướng dẫn"* —
  **có thể sai**: một đề tài phổ biến (ví dụ kiểm thử tự động bằng Selenium) có thể do nhiều
  giảng viên khác nhau hướng dẫn ở các khoá khác nhau, nên ứng viên gợi ý có thể lặp lại
  cùng một người cho nhiều đồ án đích.
- Vì sai không gây hậu quả trực tiếp — gợi ý chỉ vào hàng đợi chờ xác nhận, chuyên viên vẫn
  phải tự xem bằng chứng rồi quyết định.

**Ảnh.** Dùng chung `docs/huong-dan/hang-doi-tac-gia.png`.

---

### 2.9 Hàng đợi nghi trùng

**Tính năng này là gì.** Trang `/doi-soat/trung-lap/` liệt kê các nhóm bản ghi bị nghi là
cùng mô tả một công trình (thường là đồ án trùng tiêu đề) — bạn so sánh rồi quyết định gộp,
giữ riêng, hay bỏ qua.

**Cung cấp gì.**
- 4 tab trạng thái: **Nghi trùng** (mặc định), **Đã gộp**, **Giữ riêng**, **Tất cả**.
- Bảng danh sách: **Mã nhóm**, **Loại tài liệu**, **Cơ sở** (căn cứ phát hiện trùng), **Thành
  viên**, **Lưu ý** (huy hiệu cảnh báo vàng nếu có dấu hiệu đồ án nhóm), **Ngày tạo**.
- Trang chi tiết `/doi-soat/trung-lap/chi-tiet/?id=`: bảng **"So sánh bản ghi"** — mỗi cột
  một công trình thành viên, ô có giá trị khác nhau được tô nền vàng; khối **"Tương đồng
  AI"** (phần trăm cosine giữa tóm tắt các thành viên, nếu có); ba nút cuối trang **Bỏ qua**,
  **Giữ riêng**, **Gộp**.

**Cách sử dụng.**
1. Mở tab **Nghi trùng**, chú ý cột **Lưu ý** — huy hiệu cảnh báo vàng là dấu hiệu đồ án
   nhóm (nhiều sinh viên làm chung một đề tài, **không phải** trùng thật).
2. Bấm vào một nhóm để mở trang chi tiết.
3. Nếu có cảnh báo đồ án nhóm, đọc hộp cảnh báo đỏ/vàng đầu trang trước khi quyết định.
4. So bảng "So sánh bản ghi" — chú ý các ô tô vàng (giá trị khác nhau giữa các thành viên).
5. Chọn một trong ba hành động:
   - **Bỏ qua** — không quyết định ngay, để xem lại sau.
   - **Giữ riêng** — chọn khi đây thực sự là các công trình khác nhau (ví dụ đồ án nhóm);
     nhập **Lý do \*** bắt buộc (ví dụ *"Đây là đồ án nhóm của các nhóm sinh viên khác
     nhau…"*).
   - **Gộp** — chọn bản ghi sống sót và giá trị cho từng trường khác biệt trước khi xác
     nhận; thao tác **không thể hoàn tác**.

**Ai được dùng.** Xem: mọi người đã đăng nhập. Quyết định: chỉ **Phòng KH-CN**.

**Lưu ý / giới hạn.**
- Đo trên dữ liệu thật: **39 nhóm nghi trùng** đang mở, **15 nhóm** có cảnh báo đồ án nhóm.
- Khi có cảnh báo đồ án nhóm, nút **Giữ riêng** được làm nổi bật (nút chính) còn **Gộp** hạ
  xuống nút phụ — vì gộp theo tiêu đề ngây thơ có thể xoá dữ liệu thật: phần lớn nhóm trùng
  tiêu đề ở khảo sát ban đầu là đồ án nhóm hợp lệ, không phải trùng thật.
- **Gộp không bao giờ chạy tự động** — kể cả khi có gợi ý tương đồng AI cao.

**Ảnh.** `docs/huong-dan/nghi-trung.png`.

---

### 2.10 Kỳ báo cáo

**Tính năng này là gì.** Nhóm màn hình quản lý một kỳ kê khai công trình toàn trường: mở
kỳ, theo dõi tiến độ từng đơn vị, duyệt hồ sơ kê khai qua hai cấp (khoa rồi phòng), và chốt
kỳ thành một bản báo cáo không đổi được nữa.

**Cung cấp gì.**

*Danh sách kỳ* (`/ky-bao-cao/`): bảng các kỳ (mã, tên, trạng thái, hạn nộp, ngày mở); nút
**"Mở kỳ mới"** (chỉ Phòng KH-CN) mở hộp thoại nhập **Mã kỳ \***, **Tên kỳ \***, **Phạm vi
(JSON) \***, **Tiêu chí (tuỳ chọn)**, **Hạn nộp \***.

*Chi tiết một kỳ* (`/ky-bao-cao/chi-tiet/?id=`) có 3 tab:
- **Tiến độ theo đơn vị**: bảng mỗi đơn vị một dòng, thanh tiến độ theo 7 nhóm trạng thái —
  **Đang soạn** (gộp Nháp + Chờ bổ sung), **Chờ khoa**, **Khoa đã duyệt**, **Chờ phòng**,
  **Đạt**, **Đã chốt**, **Rút**.
- **Hồ sơ kê khai**: bảng từng hồ sơ (công trình, đơn vị, trạng thái, số minh chứng); nút
  **"Kê khai công trình"** (chọn công trình + đơn vị, chỉ khi kỳ đang **Đang mở**); mỗi hồ sơ
  có menu **Hành động** hiện đúng bước chuyển được phép theo vai trò của bạn.
- **Báo cáo**: danh sách các phiên bản báo cáo đã tạo, nút **"Tạo bản báo cáo"**, mỗi phiên
  bản có nút **Xem**, **CSV**, **XLSX**.

*Nút vòng đời kỳ* (Phòng KH-CN): **Đóng nộp** (khi kỳ đang mở), **Chốt kỳ** (khi đã đóng
nộp), **Huỷ kỳ** (khi kỳ đang chuẩn bị hoặc đang mở).

*Chi tiết một hồ sơ kê khai* (`/ke-khai/?id=`): thông tin hồ sơ, dòng thời gian sự kiện (mỗi
lần chuyển trạng thái kèm người thực hiện và lý do nếu có), danh sách minh chứng (đường dẫn/
ghi chú/tệp), nút **"Thêm minh chứng"**.

*Báo cáo đã chốt* (`/bao-cao/?id=`): badge **"Đóng băng · SHA-256 …"**, bảng tổng hợp theo
đơn vị × trạng thái, bảng theo loại tài liệu, bảng chi tiết từng hồ sơ (có ô tìm nhanh), nút
**CSV**, **XLSX**, **In**.

**Cách sử dụng.**

*Mở kỳ mới (Phòng KH-CN):*
1. Ở `/ky-bao-cao/`, bấm **"Mở kỳ mới"**.
2. Điền **Mã kỳ**, **Tên kỳ**, **Phạm vi** (JSON, ví dụ `{"doc_types":["bai_bao"]}`), **Hạn
   nộp**. Bấm **Mở kỳ** — kỳ chuyển ngay sang trạng thái **Đang mở**.

*Kê khai một công trình vào kỳ:*
1. Mở chi tiết kỳ, tab **Hồ sơ kê khai**, bấm **"Kê khai công trình"**.
2. Chọn **Công trình \*** (gõ tiêu đề để tìm), chọn **Đơn vị \*** chịu trách nhiệm, ghi chú
   nếu cần. Bấm **Kê khai** — hồ sơ mới ở trạng thái **Nháp**.

*Trình duyệt và duyệt hai cấp:* xem bảng chuyển trạng thái × vai trò dưới đây — mở hồ sơ ở
`/ke-khai/?id=`, bấm đúng nút hành động hiện ra theo vai trò của bạn (một số bước bắt buộc
nhập **Lý do \***).

*Thêm minh chứng:*
1. Ở chi tiết hồ sơ, bấm **"Thêm minh chứng"**.
2. Chọn tab **"Đường dẫn / ghi chú"** (nhập URL hoặc ghi chú) hoặc **"Tải tệp lên"** (kéo-thả
   hoặc bấm **"Chọn tệp"**, tối đa 10 MB, chỉ nhận PDF/PNG/JPG/DOCX).
3. Bấm **"Thêm minh chứng"**. Với tệp đã tải lên, dòng minh chứng hiện tên tệp, kích thước,
   mã băm SHA-256 rút gọn và nút **"Tải về"**.

*Chốt kỳ và xem báo cáo (Phòng KH-CN):*
1. Khi kỳ đã **Đã đóng nộp**, mở tab **Báo cáo**, bấm **Chốt kỳ** ở trên (hoặc **"Tạo bản báo
   cáo"** để chỉ tạo thêm một phiên bản mà không đổi trạng thái kỳ).
2. Hệ thống chuyển thẳng tới `/bao-cao/?id=` vừa sinh — không cần thao tác thêm.
3. Đọc badge **"Đóng băng · SHA-256 …"**; xem bảng tổng hợp và bảng chi tiết; bấm **CSV**,
   **XLSX**, hoặc **In** để xuất.

**Bảng chuyển trạng thái hồ sơ kê khai × vai trò** (8 trạng thái: **Nháp**, **Chờ bổ sung**,
**Chờ khoa duyệt**, **Khoa đã duyệt**, **Chờ phòng kiểm tra**, **Đạt yêu cầu**, **Đã chốt**,
**Đã rút**):

| Từ trạng thái | Nút bấm | Sang trạng thái | Ai bấm được | Cần lý do? |
|---|---|---|---|---|
| Nháp | **Trình khoa duyệt** | Chờ khoa duyệt | Chuyên viên khoa, Phòng KH-CN, Giảng viên (hồ sơ của chính mình) | Không |
| Nháp | **Yêu cầu bổ sung** | Chờ bổ sung | Chuyên viên khoa, Phòng KH-CN | **Có** |
| Nháp | **Rút** | Đã rút | Chuyên viên khoa, Phòng KH-CN, Giảng viên (của chính mình) | **Có** |
| Chờ bổ sung | **Trả về nháp** | Nháp | Chuyên viên khoa, Phòng KH-CN | Không |
| Chờ bổ sung | **Rút** | Đã rút | Chuyên viên khoa, Phòng KH-CN, Giảng viên (của chính mình) | **Có** |
| Chờ khoa duyệt | **Khoa duyệt** | Khoa đã duyệt | Trưởng khoa | Không |
| Chờ khoa duyệt | **Trả về** | Nháp | Trưởng khoa | **Có** |
| Khoa đã duyệt | **Gửi phòng kiểm tra** | Chờ phòng kiểm tra | Trưởng khoa, Phòng KH-CN | Không |
| Chờ phòng kiểm tra | **Đạt yêu cầu** | Đạt yêu cầu | Phòng KH-CN | Không |
| Chờ phòng kiểm tra | **Trả về** | Nháp | Phòng KH-CN | **Có** |
| Đạt yêu cầu | (chỉ qua **Chốt kỳ**, hàng loạt) | Đã chốt | Phòng KH-CN | Không |

Quy tắc quan trọng: **từ "Khoa đã duyệt" trở đi, mọi thay đổi đưa hồ sơ về lại Nháp và mất
dấu đã duyệt** — không có tình huống khoa và phòng cùng giữ hai bản "đã duyệt" khác nhau của
cùng một hồ sơ.

**Ai được dùng.** Mở/đóng/huỷ/chốt kỳ, kiểm tra và tạo báo cáo: **Phòng KH-CN**. Kê khai và
trình duyệt: **Chuyên viên khoa** (trong phạm vi đơn vị mình), **Giảng viên** (chỉ hồ sơ của
chính mình, xem mục 2.11). Duyệt/trả về: **Trưởng khoa** (chỉ khoa mình). Xem tiến độ và báo
cáo: **Lãnh đạo** xem mọi đơn vị; cấp khoa chỉ xem đơn vị mình.

**Lưu ý / giới hạn.**
- Minh chứng dạng tệp: tối đa **10 MB**, chỉ nhận PDF/PNG/JPG/DOCX — loại tệp được kiểm bằng
  **chữ ký byte đầu tệp**, không tin phần mở rộng tên tệp gửi lên; tệp được băm SHA-256 lúc
  lưu để kiểm lại không bị đổi.
- Báo cáo đã chốt (**đóng băng**) chụp lại toàn bộ hồ sơ kê khai của kỳ (mọi trạng thái) cùng
  công trình/tác giả/minh chứng **tại đúng thời điểm chốt**, không đổi về sau dù dữ liệu gốc
  có sửa tiếp; mỗi lần chốt hoặc tạo thêm bản báo cáo sinh một **phiên bản mới** (v1, v2…),
  không ghi đè phiên bản cũ.
- Cấp khoa chỉ xem/xuất được hồ sơ **của đơn vị mình** trong một báo cáo — không thấy dữ liệu
  của khoa khác.
- Phạm vi đơn vị (NFR-02) được lọc **ở tầng cơ sở dữ liệu**, không chỉ ẩn trên giao diện —
  chuyên viên/trưởng khoa không lấy được dữ liệu của khoa khác kể cả khi gõ thẳng đường link.

**Ảnh.** `docs/huong-dan/chi-tiet-cong-trinh.png` (minh hoạ thao tác chỉnh tay có xuất xứ đi
kèm quy trình kê khai). Chưa có ảnh riêng cho màn hình kỳ báo cáo/báo cáo đóng băng.

---

### 2.11 Kê khai của tôi

**Tính năng này là gì.** Trang `/ke-khai-cua-toi/` cho **giảng viên** tự kê khai công trình
đã được liên kết với chính mình vào kỳ báo cáo đang mở, không cần nhờ chuyên viên khoa nhập
hộ.

**Cung cấp gì.**
- Khối **"Công trình của tôi"**: bảng công trình đã liên kết với hồ sơ giảng viên của bạn
  (tiêu đề, loại, năm, trạng thái liên kết, đã kê khai vào kỳ nào chưa); ô chọn **Kỳ đang
  mở**; nút **"Kê khai vào kỳ này"** trên mỗi dòng.
- Khối **"Hồ sơ của tôi"**: chỉ gồm hồ sơ do chính bạn kê khai — nút **"Trình khoa duyệt"**
  và **"Rút"** trên mỗi dòng khi còn ở bước cho phép.

**Cách sử dụng.**
1. Mở `/ke-khai-cua-toi/`. Nếu chưa có kỳ nào đang mở, trang vẫn cho xem công trình và hồ sơ
   cũ, chỉ chưa kê khai mới được.
2. Chọn **Kỳ đang mở** ở ô chọn.
3. Ở bảng "Công trình của tôi", bấm **"Kê khai vào kỳ này"** trên công trình muốn kê khai.
4. Xuống khối "Hồ sơ của tôi", bấm **"Trình khoa duyệt"** khi hồ sơ đã sẵn sàng, hoặc
   **"Rút"** (kèm lý do bắt buộc) nếu muốn rút lại.

**Ai được dùng.** **Giảng viên** — chỉ thấy và thao tác được công trình/hồ sơ của chính
mình.

**Lưu ý / giới hạn.**
- Chỉ kê khai được công trình có liên kết tác giả ở trạng thái **Đã nối tự động** hoặc **Đã
  xác nhận** — công trình còn ở hàng đợi chờ xác nhận chưa kê khai được.
- Nếu tài khoản của bạn chưa được gắn với đúng hồ sơ giảng viên, trang báo *"Chưa thể kê
  khai — Tài khoản chưa gắn với hồ sơ giảng viên"* — liên hệ Phòng KH-CN.

**Ảnh.** Chưa có ảnh minh hoạ riêng.

---

### 2.12 Khoa của tôi / Theo khoa

**Tính năng này là gì.** Trang `/khoa/?id=` gom số liệu công trình và hồ sơ kê khai của
**một đơn vị (khoa)** vào một màn hình — trước đây lãnh đạo khoa chỉ có bức tranh này khi
chuyên viên tổng hợp tay từ Excel.

**Cung cấp gì.**
- Bốn thẻ số: **Tổng công trình**, **Đã liên kết**, **Chờ xác nhận**, **Giảng viên chưa có
  công trình**.
- Biểu đồ **"Công trình 5 năm theo loại tài liệu"**.
- Bảng **"10 giảng viên có nhiều công trình nhất"**.
- Khối **"Hồ sơ kê khai theo trạng thái"** của kỳ đang mở — bấm một huy hiệu trạng thái để
  đi thẳng tới kỳ báo cáo tương ứng.
- Khối **"Giảng viên chưa có công trình liên kết"**, kèm liên kết sang **"kiểm tra hàng đợi
  tác giả"**.
- Với **Phòng KH-CN**/**Lãnh đạo**: ô chọn **đơn vị** ở đầu trang để xem khoa bất kỳ.

**Cách sử dụng.**
1. Chuyên viên khoa/Trưởng khoa/Giảng viên: mở mục **"Khoa của tôi"** ở thanh bên — trang tự
   mở đúng đơn vị của bạn.
2. Phòng KH-CN/Lãnh đạo: mở mục **"Theo khoa"**, chọn đơn vị cần xem ở ô chọn.
3. Đọc bốn thẻ số, biểu đồ 5 năm, bảng top giảng viên.
4. Bấm một huy hiệu trạng thái trong khối "Hồ sơ kê khai theo trạng thái" để mở kỳ báo cáo
   tương ứng; bấm vào khối "Giảng viên chưa có công trình liên kết" để đi tới hàng đợi tác
   giả kiểm tra.

**Ai được dùng.** **Chuyên viên khoa**, **Trưởng khoa**, **Giảng viên** — chỉ xem được đơn vị
mình. **Phòng KH-CN**, **Lãnh đạo** — xem được mọi đơn vị.

**Lưu ý / giới hạn.**
- Bảng top giảng viên và biểu đồ chỉ tính **10 giảng viên** và **5 năm gần nhất**.
- Cấp khoa cố tình bị chặn ở tầng máy chủ nếu gõ thẳng đường link sang đơn vị khác — trang
  trả về lỗi truy cập, không chỉ ẩn trên giao diện.

**Ảnh.** Chưa có ảnh minh hoạ riêng.

---

### 2.13 Hồ sơ giảng viên

**Tính năng này là gì.** Trang `/giang-vien/?id=` gom mọi công trình đã liên kết của một
giảng viên thành một hồ sơ công bố, cùng số liệu theo loại và theo năm.

**Cung cấp gì.**
- Thông tin liên hệ: ORCID, Google Scholar, email (nếu có).
- Cảnh báo nếu có công trình đang chờ xác nhận liên kết với hồ sơ này, kèm liên kết mở hàng
  đợi tác giả.
- Khối **"Công trình theo loại"** và **"Công trình theo năm"** (biểu đồ cột).
- Bảng **"Danh sách công trình"** — mỗi dòng có nút **Trích dẫn** mở hộp thoại 3 định dạng.
- Nút **"Lý lịch khoa học"** và **"Tải CSV"** ở đầu trang.

**Cách sử dụng.**
1. Mở hồ sơ một giảng viên từ Tổng quan, Tra cứu, hàng đợi, hoặc chi tiết công trình.
2. Xem thống kê theo loại và theo năm; nếu có cảnh báo liên kết đang chờ, bấm mở hàng đợi
   tác giả để xử lý.
3. Ở bảng danh sách công trình, bấm **Trích dẫn** trên một dòng để lấy APA/IEEE/BibTeX.
4. Bấm **"Tải CSV"** để xuất toàn bộ danh sách công bố của giảng viên này.
5. Bấm **"Lý lịch khoa học"** để mở bản in được (xem mục 2.13.1).

**Ai được dùng.** Công khai.

**Lưu ý / giới hạn.** Không có giới hạn số dòng — bảng hiển thị toàn bộ công trình đã liên
kết của giảng viên, sắp theo năm giảm dần.

**Ảnh.** `docs/huong-dan/ho-so-giang-vien.png`.

#### 2.13.1 Lý lịch khoa học

**Tính năng này là gì.** Trang `/giang-vien/ly-lich/?id=` sinh một bản lý lịch khoa học khổ
A4, sẵn sàng in hoặc lưu PDF — tổng hợp học hàm/học vị, số liệu công bố theo loại/năm, và
danh sách công trình dạng APA.

**Cung cấp gì.**
- Toàn bộ nội dung dạng in (không có thanh bên); nút **"Về hồ sơ"** quay lại `/giang-vien/`.
- Nút **"Sao chép trích dẫn tất cả"** (sao chép toàn bộ danh sách công trình dạng APA vào
  bộ nhớ tạm).
- Nút **"In / Lưu PDF"** — gọi hộp thoại in của trình duyệt, chọn "Lưu dưới dạng PDF" để có
  tệp PDF.

**Cách sử dụng.**
1. Từ hồ sơ giảng viên, bấm **"Lý lịch khoa học"**.
2. Bấm **"Sao chép trích dẫn tất cả"** nếu cần dán danh sách công trình vào nơi khác.
3. Bấm **"In / Lưu PDF"**, chọn máy in hoặc "Lưu dưới dạng PDF" trong hộp thoại của trình
   duyệt.

**Ai được dùng.** Công khai.

**Lưu ý / giới hạn.** Trang được canh khổ **A4**; phần thanh nút tự ẩn khi in (chỉ nội dung
lý lịch được in ra).

**Ảnh.** Chưa có ảnh minh hoạ riêng.

---

### 2.14 Chất lượng dữ liệu

**Tính năng này là gì.** Nhóm hai màn hình theo dõi độ phủ liên kết và các bất thường trong
dữ liệu, giúp Phòng KH-CN biết cần xử lý gì tiếp mà không phải dò từng bảng.

**Cung cấp gì (Tổng quan, `/chat-luong-du-lieu/`).**
- Khối **"Chỉ số cần theo dõi"**: danh sách chỉ số (tổng công trình, công trình cần rà soát,
  lượt tên giữ chỗ, số liên kết tự động/chờ/xác nhận, nhóm nghi trùng đang mở, cảnh báo đang
  mở…), mỗi chỉ số có nút **"Mở hàng đợi"** hoặc **"Mở cảnh báo"** đưa thẳng tới đúng nơi xử
  lý.
- Khối **"Mức phủ liên kết tác giả"** — thanh phần trăm công trình đã có liên kết.
- Biểu đồ **"Công trình theo loại tài liệu"**.
- Thanh tab con: **Tổng quan** / **Cảnh báo**.

**Cách sử dụng (Tổng quan).**
1. Mở `/chat-luong-du-lieu/`.
2. Đọc từng chỉ số ở khối "Chỉ số cần theo dõi"; bấm **"Mở hàng đợi"** hoặc **"Mở cảnh báo"**
   trên chỉ số cần xử lý để đi thẳng tới đó.
3. Xem thanh phần trăm liên kết tác giả và biểu đồ theo loại tài liệu.

**Ai được dùng.** Xem: mọi người đã đăng nhập (đặc biệt hữu ích cho **Lãnh đạo** và **Phòng
KH-CN**).

#### 2.14.1 Cảnh báo bất thường dữ liệu

**Tính năng này là gì.** Tab **Cảnh báo** (`/chat-luong-du-lieu/canh-bao/`) hiện kết quả quét
**6 loại bất thường** trong dữ liệu (chỉ đọc, không tự sửa), để chuyên viên xem và xử lý.

**Cung cấp gì.**
- Nút lọc nhanh theo từng loại kèm số lượng đang mở: **Scopus/ISI thiếu DOI**, **Năm ngoài
  khoảng**, **Trùng tiêu đề bài báo**, **Trùng ORCID**, **DOI sai định dạng**, **Bài báo
  thiếu tóm tắt**.
- Bộ lọc **Mức độ** (Cao/Vừa/Thấp) và **Trạng thái** (Đang mở/Đã bỏ qua/Đã khắc phục).
- Bảng: **Loại**, **Mức**, **Công trình hoặc giảng viên**, **Chi tiết**, **Ngày**, nút
  **Bỏ qua**.

**Cách sử dụng.**
1. Mở tab **Cảnh báo**. Bấm một nút loại cảnh báo để lọc nhanh, hoặc dùng bộ lọc **Mức độ**/
   **Trạng thái**.
2. Xem cột **Chi tiết** để biết đúng vấn đề (ví dụ liên kết sang công trình bị trùng, hoặc
   giá trị năm sai).
3. Với cảnh báo đã kiểm tra là không sao, bấm **Bỏ qua**, nhập **Lý do \*** bắt buộc (ít nhất
   3 ký tự), xác nhận — cờ chuyển sang **Đã bỏ qua** ngay, có ghi vào nhật ký thao tác.

**Ai được dùng.** Xem: mọi người đã đăng nhập. Bỏ qua: chỉ **Phòng KH-CN**.

**Lưu ý / giới hạn.**
- Sáu loại và mức độ mặc định: **Scopus/ISI thiếu DOI** (mức Cao, đo được 64 cờ),
  **Trùng ORCID** (mức Cao, 0 cờ), **Năm ngoài khoảng 1990–năm hiện tại+1** (mức Vừa,
  0 cờ), **Trùng tiêu đề với một bài báo** (mức Vừa, 2 cờ), **DOI sai định dạng** (mức Vừa,
  0 cờ), **Bài báo không có tóm tắt** (mức Thấp, 1.697 cờ) — số liệu đo trên 7.618 công
  trình, 400 giảng viên.
- Quét **chỉ đọc**, không tự sửa gì; cờ đã **Đã bỏ qua** không bao giờ tự mở lại dù điều
  kiện vẫn còn đúng ở lần quét sau.
- Cần chạy `python -m cris quality scan` để có/cập nhật dữ liệu cảnh báo — trang không tự
  quét khi bạn mở nó.

**Ảnh.** Chưa có ảnh minh hoạ riêng.

---

### 2.15 Đồng bộ

**Tính năng này là gì.** Trang `/dong-bo/` là lịch sử mọi lượt lấy dữ liệu từ kho nguồn:
thêm/đổi/mất bao nhiêu bản ghi, mất bao lâu, có lỗi hay cảnh báo gì không.

**Cung cấp gì.**
- Bảng: **Thời điểm**, **Nguồn / phạm vi**, **Trạng thái**, **Thêm / đổi / mất**, **Lỗi /
  cảnh báo**, **Thời lượng**.
- Trang chi tiết `/dong-bo/chi-tiet/?id=`: 6 ô số liệu (**Dự kiến**, **Đã lấy**, **Thêm**,
  **Đổi**, **Mất**, **Thời lượng**), cảnh báo/lỗi nếu có, và bảng **"Bản ghi thay đổi gần
  nhất"** (tối đa 20 dòng).

**Cách sử dụng.**
1. Mở `/dong-bo/` để xem toàn bộ lịch sử đồng bộ.
2. Bấm một dòng để mở chi tiết lượt đó.
3. Xem 6 ô số liệu và bảng bản ghi thay đổi gần nhất; đọc khối cảnh báo/lỗi nếu trạng thái
   không phải "Thành công".

**Ai được dùng.** Công khai — không có kiểm tra vai trò trên trang này.

**Lưu ý / giới hạn.** Mỗi yêu cầu tới kho nguồn giãn cách 0,35 giây; một lượt đồng bộ đầy đủ
toàn bộ kho (6 loại tài liệu) đo được khoảng 2 giờ.

**Ảnh.** Chưa có ảnh minh hoạ riêng.

---

### 2.16 Nhật ký

**Tính năng này là gì.** Trang `/nhat-ky/` là nhật ký thao tác của toàn hệ thống — mọi quyết
định (xác nhận/bác bỏ liên kết, gộp/giữ riêng, mở/đóng/chốt kỳ, chỉnh tay dữ liệu, bỏ qua
cảnh báo…) đều đọc lại được kèm người thực hiện và giá trị trước/sau.

**Cung cấp gì.**
- Bộ lọc **"Loại thực thể"**: Tất cả / Liên kết tác giả / Nhóm nghi trùng / Kỳ báo cáo / Hồ
  sơ kê khai / Bản ghi nguồn / Lượt tên.
- Bảng: **Thời điểm**, **Người thao tác** (hoặc **"Hệ thống"** nếu không có người), **Thao
  tác** (nhãn tiếng Việt, ví dụ *"Xác nhận liên kết"*, *"Gộp bản ghi trùng"*, *"Chỉnh tay
  trường dữ liệu"*, *"Bỏ qua cảnh báo chất lượng"*), **Thực thể**, nút **"Xem thay đổi"**.
- Hộp thoại "Xem thay đổi": hai khối **"Trước thay đổi"** và **"Sau thay đổi"** hiện dữ liệu
  chi tiết dạng JSON.

**Cách sử dụng.**
1. Mở `/nhat-ky/`. Lọc theo **Loại thực thể** nếu muốn xem riêng một nhóm thao tác.
2. Với một dòng cần biết chi tiết, bấm **"Xem thay đổi"** để xem giá trị trước và sau.

**Ai được dùng.** Cần đăng nhập khi hệ thống đang bắt buộc đăng nhập (mọi vai trò xem được —
không giới hạn riêng cho Phòng KH-CN).

**Lưu ý / giới hạn.** Phân trang 50 dòng mỗi trang.

**Ảnh.** Chưa có ảnh minh hoạ riêng.

---

### 2.17 Thông báo

**Tính năng này là gì.** Chuông ở thanh trên và trang `/thong-bao/` báo cho bạn biết ngay
khi hồ sơ của mình đổi trạng thái, kỳ báo cáo mở/đóng/huỷ/chốt, hoặc công trình vừa được nối
vào hồ sơ giảng viên của mình.

**Cung cấp gì.**
- Chuông ở thanh trên: huy hiệu số thông báo chưa đọc; bấm mở danh sách 8 thông báo gần
  nhất; nút **"Đánh dấu tất cả đã đọc"**; nút **"Xem tất cả"**.
- Trang `/thong-bao/`: ô tích **"Chỉ hiện chưa đọc"**, bảng đầy đủ (Thông báo, Nội dung, Thời
  gian, Trạng thái), nút **"Đánh dấu tất cả đã đọc"**.

**Cách sử dụng.**
1. Bấm biểu tượng chuông ở thanh trên để xem nhanh; bấm một dòng để mở đúng hồ sơ/báo cáo
   liên quan (tự đánh dấu đã đọc).
2. Bấm **"Xem tất cả"** để mở `/thong-bao/` đầy đủ, có phân trang.
3. Bấm **"Chỉ hiện chưa đọc"** để lọc; bấm **"Đánh dấu tất cả đã đọc"** khi muốn dọn hết huy
   hiệu chưa đọc.

**Ai được dùng.** Mọi người dùng đã đăng nhập — mỗi người chỉ thấy thông báo của chính mình.

**Lưu ý / giới hạn.**
- Không bao giờ tự báo cho chính người vừa thực hiện thao tác đó.
- Chỉ có kênh thông báo **trong ứng dụng** — chưa gửi email hay Zalo.
- Lỗi khi gửi thông báo không làm hỏng thao tác nghiệp vụ chính (ví dụ duyệt hồ sơ vẫn thành
  công dù thông báo gửi lỗi).

**Ảnh.** Chưa có ảnh minh hoạ riêng.

---

### 2.18 Về hệ thống

**Tính năng này là gì.** Trang `/ve/` cho biết tình trạng vận hành của hệ thống và của tầng
AI — nơi kiểm tra nhanh "hệ thống có đang khoẻ không, AI có đang bật không" mà không cần mở
terminal.

**Cung cấp gì.**
- Khối **"Tình trạng"**: **Cơ sở dữ liệu** (Hoạt động bình thường/Không kết nối được),
  **Mô hình AI** (Đã nạp/Chưa nạp/Đã tắt), **Tuổi dữ liệu đồng bộ** (cách đây bao nhiêu giờ),
  **Phiên bản** hệ thống.
- Khối **"Nguồn và đồng bộ"**: tổng số công trình, liên kết tới kho dữ liệu ICTU và mã nguồn
  trên GitHub, lần đồng bộ gần nhất.
- Khối **"Công trình theo loại"**.
- Khối **"AI trong hệ thống"** (badge **"Chỉ gợi ý"**): nhà cung cấp, mô hình, giấy phép,
  kích thước/số chiều, số vector đã tạo, số chủ đề/gợi ý, số gợi ý người hướng dẫn, số khoá
  đã rà soát.
- Khối **"Giới hạn cần lưu ý"** — danh sách đánh số các giới hạn thật của AI (xem mục 4).
- Cảnh báo màu vàng **"Chưa bật đăng nhập"** nếu hệ thống vẫn ở chế độ mở.

**Cách sử dụng.**
1. Mở `/ve/` khi cần kiểm tra nhanh tình trạng hệ thống hoặc muốn biết mô hình AI đang dùng
   là gì.
2. Đọc khối "Tình trạng" trước — nếu "Mô hình AI" báo **Chưa nạp**, liên hệ người vận hành
   chạy lại `python -m cris ai download`.
3. Đọc khối "Giới hạn cần lưu ý" trước khi trình bày số liệu AI cho người khác.

**Ai được dùng.** Công khai.

**Lưu ý / giới hạn.** Nội dung khối "Giới hạn cần lưu ý" chính là các câu ở mục 4 bên dưới —
trang này chỉ hiển thị lại, không có gì thêm ngoài đó.

**Ảnh.** Chưa có ảnh minh hoạ riêng.

---

### 2.19 Hướng dẫn trong ứng dụng

**Tính năng này là gì.** Trang `/huong-dan/` là hướng dẫn ngắn gọn **ngay trong ứng dụng**,
chia theo 4 nhóm vai trò, để người dùng mới tự bắt đầu mà không cần đọc tài liệu này.

**Cung cấp gì.**
- Mục lục theo 4 vai trò: **Phòng KH-CN**, **Khoa**, **Giảng viên**, **Lãnh đạo** — mục phù
  hợp với vai trò đang đăng nhập của bạn được đánh dấu **"Vai trò của bạn"**.
- Mỗi mục là các bước đánh số kèm liên kết đưa thẳng tới đúng trang, cộng ảnh minh hoạ cho
  Phòng KH-CN, Giảng viên, Lãnh đạo.
- Khối **"AI làm gì — và không làm gì"**.
- Khối **"Thuật ngữ"** (7 mục) và **"8 trạng thái"** của hồ sơ kê khai.
- Khối **"Câu hỏi thường gặp"** (6 câu, dạng xổ xuống).

**Cách sử dụng.**
1. Mở `/huong-dan/` từ mục **Hướng dẫn** ở thanh bên, hoặc từ trang đăng nhập.
2. Tìm mục có huy hiệu **"Vai trò của bạn"**, đọc các bước theo đúng thứ tự.
3. Bấm liên kết ở mỗi bước để mở ngay trang tương ứng.
4. Cuộn xuống đọc "Thuật ngữ" và "Câu hỏi thường gặp" nếu cần tra nhanh một khái niệm.

**Ai được dùng.** Mọi người — kể cả chưa đăng nhập (khi đó không mục nào được đánh dấu "Vai
trò của bạn").

**Lưu ý / giới hạn.** Đây là bản **rút gọn**; tài liệu bạn đang đọc (`docs/huong-dan-su-dung.md`)
đầy đủ và chi tiết hơn nhiều, gồm cả số liệu và giới hạn kỹ thuật của từng tính năng.

**Ảnh.** Dùng chung các ảnh trong `docs/huong-dan/`.

---

## 3. Quy trình nghiệp vụ xuyên suốt

### 3.1 Một kỳ báo cáo: mở → kê khai → khoa duyệt → phòng kiểm tra → chốt

1. **Phòng KH-CN** mở kỳ mới ở `/ky-bao-cao/` — bấm **"Mở kỳ mới"**, điền mã, tên, phạm vi,
   hạn nộp. Kỳ chuyển sang **Đang mở**.
2. **Chuyên viên khoa** kê khai công trình của đơn vị mình vào kỳ (`/ky-bao-cao/chi-tiet/`,
   tab **Hồ sơ kê khai**, nút **"Kê khai công trình"**) — hoặc **Giảng viên** tự kê khai công
   trình của chính mình ở `/ke-khai-cua-toi/`. Hồ sơ khởi tạo ở trạng thái **Nháp**.
3. Chuyên viên khoa (hoặc giảng viên) bấm **"Trình khoa duyệt"** — hồ sơ chuyển sang **Chờ
   khoa duyệt**.
4. **Trưởng khoa** mở hồ sơ, kiểm tra rồi bấm **"Khoa duyệt"** (chuyển **Khoa đã duyệt**)
   hoặc **"Trả về"** kèm lý do bắt buộc (hồ sơ về lại **Nháp**, mất dấu đã duyệt, phải sửa và
   trình lại từ đầu).
5. Từ **Khoa đã duyệt**, trưởng khoa (hoặc Phòng KH-CN) bấm **"Gửi phòng kiểm tra"** — hồ sơ
   chuyển **Chờ phòng kiểm tra**.
6. **Phòng KH-CN** kiểm tra rồi bấm **"Đạt yêu cầu"** (chuyển **Đạt yêu cầu**) hoặc **"Trả
   về"** kèm lý do bắt buộc (về lại **Nháp**).
7. Khi kỳ đã **Đã đóng nộp** và các hồ sơ cần thiết đã **Đạt yêu cầu**, Phòng KH-CN bấm
   **Chốt kỳ** ở chi tiết kỳ. Hệ thống chuyển hàng loạt hồ sơ **Đạt yêu cầu** sang **Đã
   chốt**, đồng thời tự sinh một **bản báo cáo đóng băng** (phiên bản mới, kèm mã băm
   SHA-256) và đưa bạn thẳng tới trang xem báo cáo đó.
8. Ai liên quan (người tạo hồ sơ, trưởng khoa, chuyên viên khoa cùng đơn vị) nhận **thông
   báo** ngay khi hồ sơ đổi trạng thái ở mỗi bước trên.

### 3.2 Đối soát dữ liệu hàng tuần

1. **Phòng KH-CN** chạy đồng bộ dữ liệu từ kho nguồn (theo lịch vận hành, xem mục 7) —
   `/dong-bo/` cho biết lượt đồng bộ gần nhất thêm/đổi/mất bao nhiêu bản ghi.
2. Mở **Hàng đợi tác giả** (`/doi-soat/tac-gia/`), xử lý các lượt tên tác giả mới ở tab **Chờ
   xác nhận** — dùng gợi ý AI làm căn cứ, tự quyết định **Xác nhận**/**Bác bỏ**/**Chuyển cho
   người khác**. Nếu có đồ án ghi `ICTU_TEACHER`, kiểm thêm tab **Gợi ý người hướng dẫn
   (AI)**.
3. Mở **Hàng đợi nghi trùng** (`/doi-soat/trung-lap/`), xử lý các nhóm nghi trùng mới phát
   sinh — chú ý cảnh báo đồ án nhóm trước khi quyết định **Gộp** hay **Giữ riêng**.
4. Chạy quét bất thường dữ liệu (`python -m cris quality scan`), mở **Chất lượng dữ liệu →
   Cảnh báo** (`/chat-luong-du-lieu/canh-bao/`) để xem cờ mới, **Bỏ qua** kèm lý do những cờ
   đã kiểm tra là không sao.
5. Xem lại **Nhật ký** (`/nhat-ky/`) nếu cần đối chiếu ai đã quyết định gì trong tuần.

### 3.3 Sinh viên/giảng viên chọn đề tài

1. **Sinh viên** vào cổng công khai `/kiem-tra-de-tai/` (không cần tài khoản), nhập đề tài dự
   kiến, xem đề tài tương tự các khoá trước và giảng viên gần chuyên môn.
2. Nếu cần xem chi tiết hơn theo 4 khía cạnh, **giảng viên hướng dẫn** (đã đăng nhập) mở
   **Đối chiếu đề tài** (`/doi-chieu/`) với cùng đề tài đó để xem ma trận bài toán/đối tượng/
   phạm vi/phương pháp.
3. Nếu cần rà theo lô cho cả một khoá, dùng **Rà soát theo khoá** (`/doi-chieu/ra-soat/`) để
   xem những đồ án bị gắn cờ mức Cao/Vừa so với các khoá trước.
4. Khi cần tìm người hướng dẫn hoặc phản biện phù hợp, dùng **Tìm chuyên gia**
   (`/doi-chieu/chuyen-gia/`) để có danh sách giảng viên gần chuyên môn kèm bằng chứng.
5. Với đồ án đang ghi người hướng dẫn giữ chỗ `ICTU_TEACHER`, Phòng KH-CN dùng **Gợi ý người
   hướng dẫn (AI)** (`/doi-soat/huong-dan/`) để tìm ứng viên thay thế và đưa vào hàng đợi xác
   nhận.

---

## 4. AI trong hệ thống

Nguyên tắc xuyên suốt — **BR-18: AI gợi ý, người quyết**. Không có nơi nào trong hệ thống để
AI tự nối tác giả, tự gộp bản ghi, tự duyệt hồ sơ, hay tự đổi một trường dữ liệu nghiệp vụ.
Mã của tầng AI (`cris/ai/`) chỉ ghi vào các bảng riêng của nó
(`ai_embedding`, `ai_topic`, `ai_topic_keyword`, `ai_suggestion`, `ai_query`, `ai_map`) — hệ
thống có test riêng đếm số dòng của các bảng nghiệp vụ trước và sau mỗi thao tác AI để đảm
bảo luôn bằng 0 thay đổi.

Mô hình chạy **hoàn toàn cục bộ** — `paraphrase-multilingual-MiniLM-L12-v2` (giấy phép
Apache-2.0, 118 MB mô hình + 17 MB tokenizer, 384 chiều, chạy CPU, không cần GPU). Sau khi
tải mô hình một lần, hệ thống **không gửi bất kỳ dữ liệu nào ra ngoài** — không có dữ liệu cá
nhân nào (email, điện thoại, ngày sinh) đi qua tầng AI, chỉ tiêu đề/tóm tắt/từ khoá/mô tả đề
tài. Khi tắt AI (`CRIS_AI_PROVIDER=none`), mọi chức năng khác vẫn chạy đủ — các chỗ gợi ý
hiện rõ "AI chưa bật".

| Tính năng | Dữ liệu dùng | Cách tính (một câu) | Số đo thật | Giới hạn |
|---|---|---|---|---|
| Đối chiếu đề tài | Tiêu đề, tóm tắt, từ khoá | So cosine trên vector câu; mỗi khía cạnh so riêng với từng câu trong tóm tắt | Không có % tổng hợp (chủ ý — BR-17) | Ngưỡng khía cạnh 0,55/0,35 là mặc định thư viện, chưa hiệu chỉnh |
| Gợi ý hàng đợi tác giả | Vector các công trình đã xác nhận của một người | Điểm ứng viên = trung bình cosine với công trình đã xác nhận của người đó | 903 liên kết chờ xác nhận trên dữ liệu thật | Chỉ có gợi ý khi người đó đã có ít nhất 1 công trình xác nhận |
| Gợi ý hàng đợi nghi trùng | Tóm tắt các thành viên trong nhóm | Cosine giữa tóm tắt từng cặp thành viên | Chỉ hiển thị thêm, không đổi gợi ý mặc định "Giữ riêng" khi có cảnh báo | Không dùng để tự quyết định gộp |
| Trục chủ đề | Vector từ khoá toàn kho | k-means (k-means++, ≤ 50 vòng) | 40 cụm cố định trên 11.716 từ khoá | Nhãn cụm chỉ là từ khoá tần suất cao nhất, không phải phân loại chính xác |
| Rà soát trùng đề tài theo khoá | Tiêu đề + tóm tắt + từ khoá của đồ án | Top-k cosine trong cùng loại tài liệu, cùng khoá so với khoá khác | Cohort 21: 47/529 (8,9%) gắn cờ mức Cao ở ngưỡng 0,90 | Chỉ khía cạnh Bài toán có mức tính được; ngưỡng hiệu chỉnh cho một cohort/một mô hình |
| Gợi ý người hướng dẫn | Vector đồ án đã có GVHD thật liên kết | Top-k láng giềng cosine, gộp phiếu theo người, `score` = tổng cosine | 1.381/4.621 đồ án (29,9%) có ít nhất một ứng viên qua ngưỡng | Giả định "cùng đề tài, cùng người hướng dẫn" có thể sai với đề tài phổ biến |
| Tìm kiếm ngữ nghĩa | Câu gõ vào so với tiêu đề+tóm tắt+từ khoá | Top-200 cosine trước khi lọc tiếp các bộ lọc khác | — | Đề tài hiếm gặp nằm ngoài top-200 sẽ không hiện dù đúng nghĩa |
| Tìm chuyên gia | Công trình đã liên kết của từng giảng viên | `Σ sᵢ·0,8^hạng·(1,1 nếu gần đây)` gộp theo người | Top-1 đúng 23,3% (7/30), top-5 chứa đúng người 46,7% (14/30) | Không phải đánh giá năng lực; chỉ tính trên công trình đã liên kết |
| Bản đồ tri thức | Toàn bộ vector ngữ nghĩa | PCA (SVD) giữ 2 trong 384 chiều | 7.618 điểm, 39 cụm, dựng trong 9,7 giây | Chỉ để định hướng, không so khoảng cách tuyệt đối |
| Cổng kiểm tra đề tài | Như Rà soát theo khoá + Tìm chuyên gia, rút gọn | Không lưu lịch sử tra cứu | Giới hạn 20 lượt/5 phút/IP | Không hiện email/điện thoại giảng viên |

---

## 5. Câu hỏi thường gặp

1. **Tôi quên mật khẩu, tự đặt lại được không?**
   Không tự đặt lại được trên giao diện. Liên hệ Phòng KH-CN để họ chạy
   `python -m cris user set-password <email của bạn>` trên máy chủ (xem mục 7).

2. **Vì sao có lúc hệ thống không bắt đăng nhập?**
   Đó là "chế độ mở" — chưa có tài khoản nào được đặt mật khẩu. Ngay khi Phòng KH-CN đặt mật
   khẩu cho một tài khoản đầu tiên, toàn hệ thống chuyển sang bắt buộc đăng nhập cho tất cả.

3. **AI có tự nối tác giả, tự gộp bản ghi trùng, hay tự duyệt hồ sơ không?**
   Không bao giờ. AI chỉ xếp hạng, gợi ý, hoặc gắn cờ kèm lý do — mọi quyết định (Xác nhận,
   Bác bỏ, Gộp, Giữ riêng, Duyệt, Trả về…) đều cần bạn tự bấm nút (BR-18).

4. **Không có toàn văn thì AI đối chiếu đề tài dựa vào đâu?**
   Chỉ dựa vào tiêu đề, tóm tắt và từ khoá — kho không có toàn văn (39/40 PDF lấy mẫu chỉ là
   tóm tắt một trang do máy sinh). Mọi trang đối chiếu đều ghi rõ dòng này.

5. **Tỷ lệ liên kết tác giả 86,6% có nghĩa là đã đúng hết chưa?**
   Chưa. Đây là tỷ lệ bài báo **có ít nhất một liên kết** (tự động hoặc đã vào hàng đợi),
   không phải tỷ lệ đã được người xác nhận đúng — phần xác nhận vẫn cần bạn quyết định ở
   Hàng đợi tác giả.

6. **Ngưỡng rà soát Cao/Vừa (0,90/0,80) có phải số tuỳ tiện không?**
   Không. Ngưỡng này được hiệu chỉnh trên phân bố điểm thật của 529 đồ án khoá 21, đọc thủ
   công hàng chục cặp quanh từng mức trước khi chọn — xem mục 4 và `docs/ai.md` §5.

7. **Ai được sửa dữ liệu công trình, sửa xong có truy ngược được không?**
   Chỉ **Phòng KH-CN** sửa trực tiếp được, và chỉ 9 trường mô tả (không sửa tác giả, đơn vị,
   minh chứng). Mọi lần sửa bắt buộc ghi lý do; giá trị gốc từ kho không bao giờ bị ghi đè,
   dòng "Nguồn" đổi thành "Chỉnh tay bởi … lúc …".

8. **Vì sao trang Tổng quan không có biểu đồ đồ án theo năm?**
   Đồ án/luận văn/luận án không có năm xuất bản đáng tin ở nguồn — biểu đồ theo năm chỉ vẽ
   được cho bài báo; phần còn lại được đếm riêng vào nhóm "không rõ năm".

9. **Tìm chuyên gia có đáng tin để tự quyết định chọn ai không?**
   Chỉ nên dùng để **thu hẹp danh sách liên hệ**. Đo trên 30 đồ án có GVHD thật: đúng vị trí
   đầu chỉ 23,3%, nằm trong top-5 46,7% — hơn một nửa số ca người thật không nằm trong top-5.
   Luôn đọc bằng chứng rồi tự liên hệ tìm hiểu thêm.

10. **Kê khai hồ sơ đang Khoa đã duyệt, tôi sửa lại một chi tiết thì sao?**
    Mọi thay đổi từ bước "Khoa đã duyệt" trở đi đưa hồ sơ **về lại Nháp** và mất dấu đã
    duyệt — phải trình khoa duyệt lại từ đầu. Đây là chủ ý thiết kế để không có hai bản "đã
    duyệt" khác nhau của cùng một hồ sơ.

11. **Báo cáo đã chốt (đóng băng) có sửa lại được không?**
    Không. Báo cáo đã chốt giữ nguyên payload tại đúng thời điểm chốt, kèm mã băm SHA-256 để
    ai cũng kiểm lại được. Muốn cập nhật số liệu, Phòng KH-CN tạo một **phiên bản báo cáo
    mới** — phiên bản cũ vẫn giữ nguyên để đối chiếu.

12. **Minh chứng dạng tệp giới hạn gì?**
    Tối đa 10 MB, chỉ nhận PDF/PNG/JPG/DOCX — loại tệp được kiểm bằng chữ ký byte đầu tệp
    (không tin đuôi tệp bạn đặt tên), và được băm SHA-256 khi lưu.

13. **Cổng kiểm tra đề tài công khai có lưu lại những gì tôi đã tra không?**
    Không. Cổng này (`/kiem-tra-de-tai/`) không lưu lịch sử tra cứu và không cần tài khoản;
    chỉ giới hạn 20 lượt/5 phút cho mỗi địa chỉ IP để tránh dùng quá tải.

14. **Sao không tích hợp SSO của trường?**
    Trường chưa có hệ SSO sẵn dùng trong thời gian phát triển bản này — hệ thống dùng đăng
    nhập cục bộ (mật khẩu băm PBKDF2-HMAC-SHA256) để có đăng nhập thật ngay, không chặn tích
    hợp SSO ở các bản sau.

## 6. Thuật ngữ

| Thuật ngữ | Giải thích |
|---|---|
| **Xuất xứ** (provenance) | Dấu vết cho biết một giá trị đến từ bản ghi nguồn nào hoặc do ai chỉnh tay, vào lúc nào. Giá trị gốc không bao giờ bị ghi đè khi giá trị đang dùng thay đổi. |
| **Lượt tên** (mention) | Một lần tên tác giả hoặc người hướng dẫn xuất hiện trên một công trình nguồn. Cùng một người có thể có nhiều lượt tên với cách viết khác nhau. |
| **Liên kết tác giả** (author link) | Mối nối giữa một lượt tên và đúng hồ sơ giảng viên; có trạng thái Đã nối tự động / Chờ xác nhận / Đã xác nhận / Đã bác bỏ. |
| **Nghi trùng** (duplicate) | Nhóm từ hai bản ghi trở lên có dấu hiệu mô tả cùng một công trình; người dùng phải so sánh rồi chọn Gộp, Giữ riêng, hoặc Bỏ qua. |
| **Khía cạnh** (aspect) | Một góc so sánh đề tài: bài toán, đối tượng, phạm vi, hoặc phương pháp — mỗi khía cạnh được giải thích riêng thay vì gộp thành một phần trăm tổng hợp. |
| **Kỳ báo cáo** (period) | Khoảng thời gian Phòng KH-CN mở để các đơn vị kê khai, duyệt và nộp công trình. Sau khi chốt, số liệu của kỳ không sửa ngầm được nữa. |
| **Chế độ mở** | Khi chưa có tài khoản nào được đặt mật khẩu, hệ thống không bắt buộc đăng nhập. Ngay khi bật đăng nhập, mọi thao tác được kiểm theo tài khoản và vai trò. |
| **Hồ sơ kê khai** (declaration) | Bản ghi gắn một công trình với một đơn vị trong một kỳ báo cáo, đi qua 8 trạng thái từ Nháp tới Đã chốt (hoặc Đã rút). |
| **Minh chứng** (evidence) | Tài liệu chứng minh cho một hồ sơ kê khai — có thể là đường dẫn, ghi chú, hoặc tệp tải lên (tối đa 10 MB). |
| **Báo cáo đóng băng** | Một phiên bản chụp lại toàn bộ dữ liệu của một kỳ báo cáo tại đúng thời điểm chốt, không đổi về sau, kèm mã băm SHA-256 để kiểm lại. |
| **BR-18 (AI gợi ý, người quyết)** | Nguyên tắc: AI trong hệ thống chỉ đưa ra gợi ý kèm lý do; quyết định cuối cùng luôn cần một người có thẩm quyền bấm nút. |
| **Cụm chủ đề** (topic) | Một nhóm công trình được AI gom lại theo từ khoá gần nhau bằng thuật toán k-means; nhãn cụm là từ khoá phổ biến nhất trong nhóm. |
| **Cohort (khoá)** | Nhóm sinh viên/đồ án cùng khoá học, dùng làm đơn vị so sánh trong tính năng Rà soát trùng đề tài theo khoá. |
| **`ICTU_TEACHER`** | Chữ giữ chỗ mà kho nguồn dùng khi chưa biết đúng giảng viên hướng dẫn của một đồ án — không phải tên một giảng viên thật. |
| **Cosine (độ tương đồng cosine)** | Cách đo mức độ gần nhau về nghĩa giữa hai đoạn văn bản đã chuyển thành vector số — giá trị càng gần 1 càng gần nghĩa. |
| **Vector ngữ nghĩa / embedding** | Dãy số (384 chiều trong hệ thống này) biểu diễn nghĩa của một đoạn văn bản, dùng để so sánh độ gần nghĩa giữa các công trình. |
| **PCA (chiếu 2 chiều)** | Kỹ thuật toán học rút gọn một vector nhiều chiều xuống còn 2 chiều để vẽ lên bản đồ — giữ lại phần lớn nhưng không phải toàn bộ thông tin gốc. |
| **NFR-02 (phạm vi đơn vị)** | Quy tắc: vai trò cấp khoa chỉ xem và thao tác được dữ liệu của đơn vị mình, lọc ngay ở tầng cơ sở dữ liệu. |
| **BR-23 (chỉnh tay có xuất xứ)** | Quy tắc: Phòng KH-CN chỉ sửa trực tiếp được 9 trường mô tả của công trình, luôn kèm lý do, không sửa tác giả/đơn vị/minh chứng. |

## 7. Phụ lục quản trị

Phần này dành cho người vận hành hệ thống (thường là Phòng KH-CN hoặc quản trị hạ tầng), chỉ
tóm tắt — chi tiết đầy đủ xem [BUILDING.md](../BUILDING.md) và
[docs/deploy-prod.md](deploy-prod.md).

- **Tạo tài khoản mới**:
  `python -m cris user create --email <email> --name "<tên>" --roles <vai_trò_1,vai_trò_2> [--unit <mã đơn vị>] [--password]`
  — ví dụ tạo một chuyên viên khoa: `--roles faculty_officer --unit HIEUTRUONG`.
- **Đặt hoặc đổi mật khẩu** (kể cả khi người dùng quên mật khẩu):
  `python -m cris user set-password <email>` (hỏi mật khẩu tại chỗ) hoặc
  `CRIS_PASSWORD='...' python -m cris user set-password <email>`. Xem danh sách tài khoản
  bằng `python -m cris user list`.
- **Gán hoặc đổi đơn vị** cho một tài khoản cấp khoa:
  `python -m cris user set-unit --email <email> --unit <mã đơn vị>`.
- **Tạo hàng loạt tài khoản giảng viên** (chưa có mật khẩu, khớp theo email để không tạo
  trùng khi chạy lại): `python -m cris user create-lecturers [--unit <mã đơn vị>] [--dry-run]`.
- **Chạy đường ống dữ liệu đầy đủ** (đồng bộ → chuẩn hoá → liên kết → gộp trùng → AI → quét
  bất thường) trên máy chủ: `bash deploy/pipeline.sh` (hoặc `--nightly` để bỏ hai bước AI
  nặng nhất trong lịch chạy đêm thường).
- **Sao lưu cơ sở dữ liệu**: tự động trước mỗi lần nâng cấp
  (`backups/pre-<phiên bản>-<ngày>.dump`) và hằng đêm lúc 03:30
  (`deploy/backups/cris-<ngày>.sql.gz`, giữ 7 ngày gần nhất). Khôi phục bằng `pg_restore`
  (bản `.dump`) hoặc `gunzip | psql` (bản `.sql.gz`).
- **Nâng cấp bản chạy thật bằng tay**: `ssh deploy@<máy chủ>` rồi
  `bash /opt/ictu-cris/deploy/upgrade.sh vX.Y.Z` — script tự sao lưu trước khi đổi, chạy
  migration, kiểm `/api/health`, và tự quay lui nếu có lỗi.
