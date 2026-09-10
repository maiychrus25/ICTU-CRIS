# TÀI LIỆU YÊU CẦU NGHIỆP VỤ (BRD) — ICTU-CRIS

| Mục | Nội dung |
|---|---|
| Tên sản phẩm | ICTU-CRIS — hệ thống thông tin nghiên cứu (*Current Research Information System*) cho Trường Công nghệ Thông tin và Truyền thông, Đại học Thái Nguyên |
| Phiên bản tài liệu | 1.0, ngày 10/09/2026 |
| Bối cảnh | Sản phẩm dự thi **"Phát triển phần mềm mã nguồn mở tích hợp AI 2026"** (Khoa CNTT, ICTU). Nộp kho mã nguồn trước 30/09/2026; chung kết 10/10/2026 |
| Giấy phép | Apache-2.0; mọi tệp mã có header SPDX |
| Kho mã nguồn | https://github.com/maiychrus25/CRIS |
| Tài liệu liên quan | [SRS.md](SRS.md) · [ba/](ba/00-README.md) (18 tệp phân tích nghiệp vụ) · [khảo sát nguồn](../khao-sat-nguon/README.md) · [kiểm chứng giả định bằng số đo](../khao-sat-nguon/kiem-chung-gia-dinh-de-tai.md) |

## 1. Bối cảnh

Trường có kho tư liệu số công khai `repository.ictu.edu.vn` với 8.034 bản ghi: 1.907 bài báo, 5.375 đồ án, 323 luận văn, 11 luận án, 410 hồ sơ giảng viên. Kho chạy WordPress với các kiểu bài viết tự viết, không phải DSpace dù tên site ghi vậy; không có API cho tài liệu học thuật, không có OAI-PMH, không có định danh bền.

Dữ liệu công bố khoa học của trường hiện nằm ở ba nơi không nói chuyện với nhau: bảng Excel các khoa gửi qua email mỗi kỳ báo cáo, kho công khai nói trên, và các chỉ mục ngoài (DOI, Scopus, Google Scholar). Mỗi lần Phòng Khoa học – Công nghệ tổng hợp số liệu là một lần gom tay; mỗi lần điều chỉnh không để lại phiên bản; và không có cách nào đi từ một con số trong báo cáo về bản ghi đã tạo ra nó.

Khảo sát ngày 09–10/09/2026 đo toàn bộ kho và cho ra những con số cụ thể ở mục 2. Toàn bộ vấn đề trong tài liệu này đều **đo được trên dữ liệu thật**, không phải giả định.

## 2. Vấn đề nghiệp vụ

| # | Vấn đề | Số đo | Hệ quả |
|---|---|---|---|
| P1 | **Tác giả không nối được với người thật.** Tên ghi hai hệ chính tả song song (68% không dấu kiểu `The-Vinh Nguyen`, 32% có dấu), hồ sơ giảng viên lưu có dấu | Chỉ **155/1.907 bài báo (8%)** liên kết được với hồ sơ giảng viên. TS. Nguyễn Văn Tảo: hồ sơ báo 5 bài, tên xuất hiện ở 29 bài, tìm kiếm ra 23 | Mọi thống kê "giảng viên X có bao nhiêu công bố" sai lệch một bậc, không phải vài phần trăm |
| P2 | **Số liệu không truy ngược được.** Không có xuất xứ cho từng trường dữ liệu; không có phiên bản báo cáo | 0 con số nào trong bất kỳ báo cáo hiện tại có đường dẫn về bản ghi gốc | Phòng KH-CN không giải trình được khi bị hỏi "số này gồm những bài nào"; sửa số liệu sau khi đã báo cáo không ai biết |
| P3 | **Dữ liệu nguồn nhiều lỗi có hệ thống.** Trường "loại bài" là văn bản tự do; bản ghi nhập hai lần; placeholder lọt ra giao diện; phân trang bỏ sót | 48 giá trị cho 1 trường loại bài · 11 nhóm bài báo trùng với metadata mâu thuẫn · **4.621/5.375 đồ án (86%)** ghi giảng viên hướng dẫn là `ICTU_TEACHER` · 11 đồ án không bao giờ lật trang tới được · 37% bài báo không có đơn vị | Đếm sai, đếm trùng, đếm thiếu — và không biết mình đang sai bao nhiêu |
| P4 | **Gộp trùng bằng tiêu đề sẽ xoá dữ liệu thật.** Đồ án nhóm nhiều sinh viên cùng đề tài trông y hệt bản ghi trùng | 43 nhóm đồ án trùng tiêu đề, trong đó **34 nhóm là đồ án nhóm** hợp lệ (52 bản ghi) | Bất kỳ công cụ khử trùng ngây thơ nào cũng phá dữ liệu; cần quy tắc gộp có sinh viên và khoá |
| P5 | **Đề tài trùng lặp không phát hiện được.** Tiêu đề đồ án dùng khuôn mẫu, từ khoá không kiểm soát | **703 đồ án** cùng mở đầu "Xây dựng website"; 10.951 từ khoá phân biệt, **76% chỉ xuất hiện đúng một lần** | Sinh viên chọn trùng đề tài khoá trước mà không biết; giảng viên không có căn cứ để so sánh ngoài trí nhớ |
| P6 | **Tổng hợp thủ công theo mùa vụ.** Văn phòng khoa gửi mẫu → chờ → gom → dán; lãnh đạo duyệt lại từ đầu mỗi lần | Chưa đo được thời gian (Q-06 trong bộ BA) — nhưng quy trình không có trạng thái, không biết hồ sơ đang chờ ai | Trễ hạn, nộp thiếu, và người duyệt ký vào thứ mình không kiểm được |

## 3. Giải pháp nghiệp vụ

ICTU-CRIS là **một nguồn sự thật cho dữ liệu công bố khoa học**, xây theo đường ống:

> **đồng bộ → chuẩn hoá → định danh người → nối tác giả → gộp trùng → hàng đợi xác nhận → tra cứu và báo cáo**

Ba nguyên tắc chi phối mọi thứ:

1. **Giữ nguyên bản gốc, ghi xuất xứ từng trường.** Mỗi bản ghi kéo về được lưu theo phiên bản; mỗi giá trị sau chuẩn hoá nói được nó từ đâu tới và ai đổi. Đây là cách duy nhất để một con số truy ngược được (P2).
2. **AI gợi ý, người quyết.** Nối tác giả mơ hồ, gộp bản ghi trùng, đối chiếu đề tài — máy xếp hạng và giải thích, người bấm quyết định, hệ thống ghi ai bấm. Không có luồng nào để máy tự đổi dữ liệu (P1, P4, P5).
3. **Không có AI vẫn chạy.** Mô hình cục bộ là mặc định; dịch vụ ngoài là tuỳ chọn qua cấu hình; `provider=none` chỉ mất phần gợi ý, không mất chức năng. Đây vừa là yêu cầu của phần mềm nguồn mở, vừa là điều kiện để giám khảo cài và chạy được từ mã nguồn.

Sản phẩm **không** thay thế kho `repository.ictu.edu.vn` — nó đọc từ kho, làm sạch, và trả lại giá trị mà kho không có: liên kết, xuất xứ, phiên bản, và gợi ý.

## 4. Mục tiêu và tiêu chí thành công

| Mục tiêu | Chỉ số | Mức đạt | Trạng thái 10/09 |
|---|---|---|---|
| G1. Mọi con số truy ngược được | Tỷ lệ trường dữ liệu có dòng xuất xứ; tỷ lệ chỉ tiêu mở ra được danh sách bản ghi | 100 % | ✅ tầng dữ liệu; giao diện tra cứu hiện đủ giá trị dùng / gốc / nguồn |
| G2. Nối được tác giả với người thật | Tỷ lệ bài báo có ít nhất một liên kết tác giả sau chuẩn hoá | ≥ 85 % (mốc nguồn: 8 %) | ✅ đo thử đạt 86 % bằng chuẩn hoá tên; ORCID phủ 91 % hồ sơ làm khoá nối ưu tiên |
| G3. Không mất bản ghi âm thầm | Số bản ghi lấy được so với số kho tự công bố | Khớp, lệch thì cảnh báo | ✅ đối soát số lượng + quét bù phân trang |
| G4. Không gộp nhầm đồ án nhóm | Số nhóm khác sinh viên bị gộp | 0 | ✅ khoá gộp gồm sinh viên + khoá; giao diện mặc định "giữ riêng" |
| G5. Đối chiếu đề tài có giải thích | Sinh viên nhập đề tài, nhận bảng so sánh theo khía cạnh với công trình liên quan | Có trên toàn bộ 5.709 đồ án/luận văn/luận án; nói rõ so trên tóm tắt | ⏳ **chưa** — mục tiêu của lát cắt AI |
| G6. Chạy được ở máy giám khảo | Cài từ mã nguồn, không khoá API, không GPU | `docker compose up` hoặc venv; mô hình cục bộ tải một lần | ✅ hiện tại; phải giữ khi thêm AI |
| G7. Hồ sơ nguồn mở đạt tiêu chí PoF | 6 tiêu chí phần I của thể lệ | Đủ, có release theo phiên bản | ⏳ thiếu **release** |

## 5. Phạm vi

### 5.1 Trong phạm vi (bản dự thi v0.1)

- **S — Đồng bộ:** kéo 6 loại nội dung từ kho ICTU, đọc trang chi tiết, lưu nguyên bản theo phiên bản, đánh dấu biến mất, đối soát số lượng, quét bù phân trang.
- **N — Chuẩn hoá và đối soát:** chuẩn hoá tên người, đơn vị, loại bài; xuất xứ từng trường; nhập hồ sơ giảng viên thành người; nối tác giả theo ORCID rồi theo tên; nghi trùng theo DOI, tiêu đề, tiêu đề+sinh viên+khoá; gộp giữ bản gốc; báo cáo chất lượng dữ liệu.
- **Giao diện hàng đợi và tra cứu:** hàng đợi liên kết tác giả, hàng đợi nghi trùng với so sánh cạnh nhau, tìm công trình, hồ sơ công bố giảng viên, chất lượng dữ liệu. Server-render, không thêm thư viện.
- **AI:** đối chiếu đề tài dự kiến trên tóm tắt (tương đồng ngữ nghĩa, bảng so sánh theo khía cạnh); gợi ý xếp hạng ứng viên trong hai hàng đợi; gom cụm từ khoá thành trục chủ đề. Mô hình cục bộ mặc định, dịch vụ ngoài tuỳ chọn.
- **K — Kỳ báo cáo (một phần):** lược đồ kỳ/hồ sơ/minh chứng và vòng đời kỳ. Chưa có giao diện.
- **Hồ sơ nguồn mở:** giấy phép, SPDX, NOTICE, chính sách thư viện, CHANGELOG, CONTRIBUTING, mẫu issue/PR, CI, hướng dẫn dịch từ mã nguồn, release theo phiên bản.

### 5.2 Ngoài phạm vi bản dự thi

- Kê khai, duyệt, chốt và xuất báo cáo theo kỳ (phần còn lại của K, toàn bộ D và R) — cần khảo sát người dùng thật, chưa làm được trong thời hạn cuộc thi.
- Đăng nhập và phân quyền theo đơn vị (NFR-01, NFR-02). Bản dự thi chạy với một người dùng mặc định và **không triển khai lên mạng công khai**.
- Nhập Excel khoa (S-06) — chờ biết biểu mẫu thật.
- Dẫn chứng theo trang trong toàn văn: **kho không có toàn văn** (39/40 PDF là tóm tắt một trang do máy sinh), nên không có gì để dẫn.
- Thống kê hợp tác quốc tế: kho không có trường cơ quan công tác hay quốc gia của tác giả.
- Kết luận đạo văn hay khẳng định tính mới của đề tài: hệ thống chỉ trình bày căn cứ, không kết luận.

## 6. Các bên liên quan

| Bên | Vai trò với sản phẩm | Điều họ cần |
|---|---|---|
| Chuyên viên Phòng KH-CN & HTQT | Người dùng chính của hàng đợi, đối soát, chất lượng dữ liệu | Số liệu tin được, giải trình được từng con số trong họp |
| Chuyên viên Văn phòng khoa | Người lập hồ sơ kê khai (giai đoạn sau) | Không nhập lại thứ đã có trong kho; biết hồ sơ đang chờ ai |
| Lãnh đạo khoa | Người duyệt (giai đoạn sau) | Thấy đúng cái mình đang ký, thấy khác gì so với lần trước |
| Giảng viên | Xác nhận công trình là của mình | Không bị hỏi đi hỏi lại; hồ sơ công bố đúng |
| Sinh viên, học viên | Tra cứu, đối chiếu đề tài dự kiến | Biết đề tài mình định làm đã có ai làm gần giống chưa, khác ở đâu |
| Ban tổ chức và giám khảo cuộc thi | Chấm theo thể lệ: 50 điểm PoF, 50 điểm sản phẩm | Cài chạy được từ mã nguồn; hồ sơ giấy phép sạch; AI có thật và có tài liệu; trình diễn thuyết phục |
| Người quản lý kho ICTU | Nhận danh sách lỗi dữ liệu nguồn | 10 lỗi đã ghi trong khảo sát, kèm cách sửa |

## 7. Yêu cầu nghiệp vụ cấp cao

Mã `YN` (yêu cầu nghiệp vụ). Các **quy tắc** nghiệp vụ chi tiết `BR-01..25` trong [ba/15-project-rules.md](ba/15-project-rules.md) được suy ra từ những yêu cầu này; SRS truy vết `YN → FR → UC → US` và ghi rõ FR nào thực thi BR nào.

| Mã | Yêu cầu | Giải quyết | Quy tắc liên quan |
|---|---|---|---|
| YN-01 | Đồng bộ dữ liệu từ kho ICTU mà **không mất bản ghi âm thầm**, giữ nguyên bản gốc theo phiên bản | P3 | BR-06 |
| YN-02 | Chuẩn hoá tên, đơn vị, loại bài; mỗi giá trị sau chuẩn hoá có **xuất xứ** | P2, P3 | BR-06, BR-10 |
| YN-03 | Nối tác giả với người thật: tự động ở mức tin cậy cao (ORCID, tên duy nhất), **hỏi người** ở mức mơ hồ, không bao giờ đề xuất lại cặp đã bác bỏ | P1 | BR-07 |
| YN-04 | Phát hiện và gộp bản ghi trùng **giữ bản gốc**; đồ án nhóm không bao giờ bị gộp theo tiêu đề | P3, P4 | BR-08, BR-09, BR-10 |
| YN-05 | Người ra quyết định trên hàng đợi; mọi quyết định ghi **ai, lúc nào, vì sao** | P1, P4 | BR-11, BR-14, BR-18 |
| YN-06 | Tra cứu công trình và hồ sơ công bố giảng viên với số liệu **nói rõ dựa trên gì** và thời điểm đồng bộ | P1, P2 | BR-03 |
| YN-07 | Đối chiếu đề tài dự kiến với kho: tìm công trình liên quan bằng **tương đồng ngữ nghĩa**, trình bày giống/khác theo khía cạnh, **không kết luận** | P5 | BR-16, BR-17 |
| YN-08 | AI **gợi ý**, người **quyết**; thiếu AI thì hệ thống vẫn đầy đủ chức năng | P1, P4, P5 | BR-18 |
| YN-09 | Báo cáo chất lượng dữ liệu cho biết số liệu **tin được đến đâu** trước khi dùng | P2, P3 | — |
| YN-10 | Đáp ứng đủ tiêu chí phần mềm nguồn mở của cuộc thi: giấy phép, dịch từ mã nguồn, thư viện, tài liệu, **release** | mục 6 | — |

## 8. Ràng buộc

| Ràng buộc | Nguồn | Ảnh hưởng |
|---|---|---|
| Nộp kho mã nguồn trước **30/09/2026**; chung kết **10/10/2026** | Thể lệ cuộc thi | Phạm vi mục 5.1 là tất cả những gì làm được; lát cắt D, R để sau |
| Sản phẩm phải là phần mềm nguồn mở theo giấy phép OSI, dịch được từ mã nguồn, có release | Thể lệ phần I | Không dùng dịch vụ đóng làm điều kiện chạy; mô hình AI phải tải được công khai |
| Giữ tối thiểu thư viện chạy; mỗi thư viện phải rà giấy phép | `DEPENDENCIES.md`, thể lệ tiêu chí 5 | Web viết bằng stdlib; thêm mô hình AI phải cập nhật chính sách thư viện |
| Kho nguồn không có API, cấu trúc HTML có thể đổi bất kỳ lúc nào | Khảo sát | Bộ đọc nguồn tách riêng, thay được không ảnh hưởng phần còn lại |
| Kho nguồn **không có toàn văn** | Khảo sát: 39/40 PDF là tóm tắt 1 trang | Đối chiếu đề tài chỉ ở mức tóm tắt và phải nói rõ điều đó |
| 4.621 đồ án mất tên GVHD ở nguồn | Khảo sát | Không khôi phục được bằng thuật toán; thống kê hướng dẫn chỉ đúng trên 14 % kho |
| Dữ liệu cá nhân giảng viên (email, điện thoại, ngày sinh) | Khảo sát | Không đưa dữ liệu thô vào repo; giao diện ẩn điện thoại và ngày sinh với vai trò sinh viên |
| Quy tắc tính điểm, năm, đồng tác giả thuộc thẩm quyền ICTU | BA §15.3 Q-07..Q-10 | Là cấu hình, không nhúng trong mã; bản dự thi dùng giá trị mặc định có ghi chú |

## 9. Giả định và phụ thuộc

- Kho `repository.ictu.edu.vn` tiếp tục công khai và `robots.txt` tiếp tục cho phép đọc toàn bộ (hiện: `Disallow:` trống).
- Mô hình embedding đa ngữ cỡ nhỏ chạy được trên CPU máy giám khảo trong thời gian chấp nhận được (mục tiêu: đối chiếu một đề tài ≤ 5 giây trên 5.709 tóm tắt).
- Hồ sơ giảng viên có ORCID (91 %) là đáng tin — chưa xác nhận với đơn vị (Q-14).
- Toàn bộ luồng quy trình K/D/R trong bộ BA là mô hình đề xuất, chưa khảo sát người dùng thật; bản dự thi không phụ thuộc vào chúng.

## 10. Rủi ro nghiệp vụ

| Rủi ro | Xác suất | Tác động | Giảm thiểu |
|---|---|---|---|
| Kho nguồn đổi cấu trúc HTML trước ngày chấm | thấp | đồng bộ hỏng | Bộ đọc tách riêng; fixture HTML trong test; dữ liệu đã đồng bộ vẫn dùng được |
| Mô hình AI cục bộ quá chậm hoặc quá nặng trên máy giám khảo | trung bình | mất điểm hoàn thiện và AI | Chọn mô hình ≤ 500 MB; tính vector trước và lưu trong DB; `provider=none` vẫn có đối chiếu bằng từ khoá |
| Thêm dependency AI làm hỏng hồ sơ giấy phép | trung bình | mất điểm PoF tiêu chí 5 | Chỉ chọn mô hình và thư viện giấy phép Apache/MIT; ghi vào `DEPENDENCIES.md` trước khi commit |
| Giám khảo hỏi "AI thật hay gắn cho có" | cao | mất điểm nguyên gốc | AI đặt đúng chỗ vấn đề đo được (P1, P4, P5); tài liệu kỹ thuật nêu rõ giới hạn; trình diễn trên dữ liệu thật |
| Không kịp release trước 30/09 | thấp | −5 điểm | Tag `v0.1.0` ngay sau khi lát cắt AI xanh; release sau đó là `v0.1.x` |
| Trình diễn trên dữ liệu có tên người thật | trung bình | vấn đề riêng tư | Fixture đã ẩn danh; demo dùng bản đồng bộ đã lọc cột cá nhân |

## 11. Lộ trình cấp cao

| Mốc | Nội dung | Hạn |
|---|---|---|
| ✅ Khảo sát nguồn, bộ BA 18 tệp, mô hình dữ liệu 0.1 | | 10/09 |
| ✅ Lát cắt S + N, giao diện hàng đợi và tra cứu, 152 test | | 10/09 |
| ⏳ BRD, SRS | tài liệu này | 11/09 |
| ⏳ Lát cắt AI: đối chiếu đề tài, gợi ý hàng đợi, gom cụm từ khoá | | 20/09 |
| ⏳ Release `v0.1.0`, cập nhật `DEPENDENCIES.md`, tài liệu kỹ thuật AI | | 22/09 |
| ⏳ Nộp kho mã nguồn | | trước 30/09 |
| ⏳ Kịch bản trình diễn 15 phút, dữ liệu demo ẩn danh | | 08/10 |
| Chung kết | hackathon + trình bày + hỏi đáp | 10/10 |

## 12. Phê duyệt

| Vai trò | Người | Ngày |
|---|---|---|
| Chủ nhiệm sản phẩm | maiychrus25 | |
| Rà soát nghiệp vụ | | |
