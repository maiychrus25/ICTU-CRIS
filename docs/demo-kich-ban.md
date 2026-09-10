# Kịch bản trình diễn — chung kết 10/10/2026

Thời lượng mục tiêu: **8–10 phút** trình diễn sống + phần hỏi đáp riêng (mục cuối). Chạy
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

## 3. Hàng đợi tác giả có gợi ý AI (90 giây)

> **Nhắc trước khi demo**: chạy trên bản sao DB dành riêng cho demo, hoặc nếu dùng DB
> thật thì chỉ thao tác trên các hàng đã kiểm tra trước là an toàn để đổi trạng thái
> (tránh xác nhận/bác bỏ nhầm một liên kết còn cần giữ nguyên cho lần demo sau).

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

## 6. Về hệ thống: AI cục bộ, giấy phép, giới hạn (60–75 giây)

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

---

## Chuẩn bị trước buổi demo

Checklist chạy theo thứ tự, trên máy sẽ dùng để trình diễn — thử toàn bộ ít nhất một lần
trước ngày 10/10, tốt nhất là ngắt mạng ở bước cuối để chắc chắn hệ thống chạy offline:

- [ ] `docker compose up -d db` rồi `docker compose build app` — dựng xong không lỗi.
- [ ] `docker compose run --rm app migrate` — áp đủ `0001`–`0008`.
- [ ] Có dữ liệu thật đã đồng bộ (đồng bộ trước, không đồng bộ trực tiếp lúc demo — mất
      khoảng 2 giờ); nếu dùng bản sao dữ liệu demo, đối chiếu số liệu trong kịch bản với
      số liệu bản sao trước khi trình diễn.
- [ ] Tạo ít nhất một người dùng vai `rd_officer`:
      `INSERT INTO app_user(email, display_name, roles) VALUES ('demo@ictu.edu.vn', 'Người trình diễn', ARRAY['rd_officer']);`
- [ ] Bật AI: `pip install -e ".[ai]"` (hoặc dùng ảnh có `--build-arg EXTRAS="[ai]"`),
      `python -m cris ai download` (tải một lần, kiểm SHA-256).
- [ ] `export CRIS_AI_PROVIDER=local` rồi lần lượt: `python -m cris ai embed`,
      `python -m cris ai topics`, `python -m cris ai suggest`,
      `python -m cris ai screen --cohort 21`.
- [ ] `python -m cris ai status` — xác nhận provider `local` và số vector đã có khớp số
      công trình.
- [ ] `python -m cris serve` (hoặc container `serve --host 0.0.0.0`) — mở
      `http://localhost:8000` và `http://localhost:8000/docs`, kiểm cả hai trả `200`.
- [ ] Mở sẵn các tab trình duyệt theo đúng thứ tự sáu phân đoạn ở trên, để không mất thời
      gian gõ URL giữa buổi trình diễn: `/tong-quan/`, `/tra-cuu/`, `/doi-soat/tac-gia/`,
      `/doi-soat/trung-lap/`, `/doi-chieu/`, `/doi-chieu/ra-soat/`, `/ve/`, `/docs`.
  - [ ] Trước khi thao tác thật trên hàng đợi tác giả/nghi trùng (phân đoạn 3, 4), xác
      nhận đây là **bản sao DB dành cho demo**, hoặc đã đánh dấu trước các hàng "an toàn để
      đổi trạng thái" nếu bắt buộc dùng DB thật.
- [ ] **Kiểm tra chạy offline**: tắt Wi-Fi/mạng, tải lại từng tab đã mở ở trên — mọi trang
      và mọi thao tác AI (đối chiếu, rà soát) vẫn chạy vì mô hình đã tải cục bộ và không
      gọi ra ngoài (`CRIS_AI_PROVIDER=local`, `docs/ai.md` §2, NFR-38).
- [ ] Chuẩn bị một laptop dự phòng hoặc bản ghi màn hình (video) của toàn bộ sáu phân đoạn,
      phòng khi mạng hội trường hoặc máy chiếu có sự cố — hệ thống không cần mạng để chạy,
      nhưng vẫn nên có phương án dự phòng cho phần cứng.
