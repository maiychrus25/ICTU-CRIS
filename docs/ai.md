# Tích hợp AI trong ICTU-CRIS

Tài liệu kỹ thuật cho FR-AI-01..09 ([SRS §3.4](SRS.md)). Viết cho hai người đọc: người
vận hành muốn bật/tắt và biết dữ liệu đi đâu; giám khảo muốn biết AI làm gì thật, dựa
trên gì, và dừng ở đâu.

## 1. AI làm gì, và không làm gì

AI trong ICTU-CRIS **gợi ý**; **người quyết** (BR-18). Ba chỗ có AI, cả ba đều là vấn đề
đo được trên dữ liệu thật của kho `repository.ictu.edu.vn` (xem
[khảo sát](../khao-sat-nguon/kiem-chung-gia-dinh-de-tai.md)):

| Chỗ | Vấn đề đo được | AI làm gì | Người làm gì |
|---|---|---|---|
| **Đối chiếu đề tài** `/doi-chieu` | 703 đồ án cùng mở đầu "Xây dựng website"; từ khoá 76 % chỉ xuất hiện một lần → so tên và từ khoá gần như vô dụng | Tìm công trình gần về nghĩa trên tiêu đề + tóm tắt + từ khoá; so từng khía cạnh (bài toán, đối tượng, phạm vi, phương pháp) → *giống* / *khác* / *chưa đủ thông tin* | Giảng viên đọc bảng đối chiếu và quyết định; hệ thống không kết luận "trùng" hay "mới" |
| **Gợi ý hàng đợi tác giả** `/doi-soat/tac-gia` | 8 % bài báo nối được tác giả ở nguồn; nhiều ca trùng tên khác người | Xếp hạng ứng viên theo tương đồng chủ đề với các công trình người đó đã được xác nhận | Chuyên viên bấm xác nhận / bác bỏ / gán lại — đúng luồng cũ, có ghi ai bấm |
| **Gợi ý hàng đợi nghi trùng** `/doi-soat/trung-lap` | 43 nhóm đồ án trùng tiêu đề, 34 là đồ án nhóm hợp lệ | Hiện tương đồng tóm tắt giữa các thành viên như một thông tin thêm | Gợi ý mặc định "Giữ riêng" cho nhóm khác sinh viên **không đổi**; người quyết gộp hay giữ |
| **Trục chủ đề** `/tra-cuu?topic=` | 10.951 từ khoá không kiểm soát | Gom từ khoá thành cụm, nhãn cụm là từ khoá phổ biến nhất | Dùng làm bộ lọc; không thay từ khoá gốc |
| **Rà soát trùng đề tài theo khoá** `/doi-chieu/ra-soat` | `dang_ky_do_an` không có ở nguồn nên không rà được lúc đăng ký; đề tài đồ án lặp lại qua các năm là nỗi đau của giảng viên hướng dẫn | Với đồ án của một khoá, tìm láng giềng ngữ nghĩa ở các khoá khác, chia mức `cao`/`vua`/`thap` theo cosine toàn văn bản | Chuyên viên/giảng viên xem bảng, tự quyết định có phải trùng hay không — không có hành động gộp/xoá nào tự động |

AI **không** làm: kết luận đạo văn, khẳng định tính mới, tự gộp bản ghi, tự nối tác giả,
tự đổi bất kỳ trường dữ liệu nghiệp vụ nào. Mã trong `cris/ai/` chỉ ghi vào bảng
`ai_embedding`, `ai_topic`, `ai_topic_keyword`, `ai_suggestion`, `ai_query` — có test rào
chắn đếm số dòng `work`, `author_link`, `duplicate_group`, `field_provenance` trước và sau
mỗi thao tác AI.

## 2. Bật, tắt, và ba nhà cung cấp

| `CRIS_AI_PROVIDER` | Là gì | Khi nào dùng |
|---|---|---|
| `none` (**mặc định**) | Không có AI. Mọi chức năng khác nguyên vẹn; chỗ gợi ý hiện "AI chưa bật"; đối chiếu đề tài **vẫn chạy** bằng đường lui khớp từ khoá, có hộp cảnh báo nói rõ | Cài lần đầu; máy không cài được thư viện AI; muốn chứng minh hệ thống không phụ thuộc AI |
| `local` | Mô hình embedding chạy trên CPU của chính máy, không gọi ra ngoài sau khi đã tải mô hình một lần | Vận hành thật; trình diễn |
| `fake` | Vector xác định từ túi từ, không cần thư viện, không cần mô hình | Chỉ để kiểm thử — không dùng cho người thật |

Bật `local`:

```bash
pip install -e ".[ai]"          # onnxruntime · tokenizers · numpy (xem DEPENDENCIES.md)
python -m cris ai download      # 118 MB + 17 MB, kiểm SHA-256, chỉ tải một lần
export CRIS_AI_PROVIDER=local
python -m cris migrate          # bảng ai_* (migration 0007) — bắt buộc nếu DB được tạo trước đó
python -m cris ai embed         # vector cho toàn bộ công trình
python -m cris ai topics        # trục chủ đề (mặc định 40 cụm, --k để đổi)
python -m cris ai suggest       # gợi ý cho hai hàng đợi
python -m cris ai screen --cohort K18   # rà soát trùng đề tài của khoá K18 với các khoá khác
python -m cris ai status        # provider, mô hình, số vector đã có
```

Tắt: đặt lại `CRIS_AI_PROVIDER=none` (hoặc bỏ biến). Bảng `ai_*` giữ nguyên, giao diện
tự chuyển sang trạng thái "AI chưa bật".

Dịch vụ AI ngoài (Claude, OpenAI…) **chưa** được hiện thực. Giao diện `Provider.explain()`
đã có chỗ cho nó — chỉ dùng để sinh lời giải thích ngôn ngữ tự nhiên ở đối chiếu đề tài,
luôn kèm nhãn "do AI sinh, cần kiểm", và chỉ nhận tiêu đề/tóm tắt/từ khoá/mô tả đề tài.
Không có dữ liệu cá nhân nào (email, điện thoại, ngày sinh) đi qua tầng AI.

## 3. Mô hình

| Mục | Giá trị |
|---|---|
| Tên | `paraphrase-multilingual-MiniLM-L12-v2` — sentence-transformers |
| Bản dùng | ONNX lượng tử hoá 8-bit (`Xenova/paraphrase-multilingual-MiniLM-L12-v2`) |
| Giấy phép | Apache-2.0 |
| Kích thước | 118 MB mô hình + 17 MB tokenizer; cài đặt thư viện thêm ~120 MB |
| Chiều vector | 384, chuẩn hoá L2, so bằng cosine |
| Ngôn ngữ | 50+, có tiếng Việt và tiếng Anh; xuyên ngôn ngữ (đề tài tiếng Việt tìm được công trình tiếng Anh cùng chủ đề) |
| Độ dài vào | cắt ở 256 token — đủ cho tiêu đề + tóm tắt một trang |
| Phần cứng | CPU, không GPU. Đo 10/09/2026 trên 4 nhân: 64 đoạn ~200 token trong 1,8 s → toàn kho 5.709 công trình ≈ 3 phút |
| Kiểm băm | SHA-256 hai tệp ghi trong `cris/ai/local.py`, kiểm trước mỗi lần nạp |
| Dữ liệu huấn luyện | Theo công bố của sentence-transformers (cặp câu song ngữ đa ngôn ngữ); dự án không huấn luyện thêm |

Vì sao chọn mô hình này thay vì mô hình lớn hơn hoặc dịch vụ ngoài: thể lệ cuộc thi chấm
"cài đặt, dịch từ mã nguồn" và "thư viện, gói đính kèm"; một sản phẩm chết khi thiếu khoá
API hoặc cần GPU sẽ yếu ở cả hai. Mô hình 118 MB chạy CPU trên máy giám khảo là điểm cân
bằng đo được.

## 4. Thuật toán (ngắn)

- **Vector công trình**: `embed(tiêu đề + "\n" + tóm tắt + "\n" + từ khoá)`; băm văn bản
  để chạy lại chỉ tính phần đổi. Công trình đã gộp không có vector.
- **Đối chiếu đề tài**: `q = embed(tên + mô tả)`; top-k cosine trên toàn ma trận (numpy,
  không pgvector). Khía cạnh: tách tóm tắt thành câu theo `.` `;` xuống dòng;
  `s = max cosine(embed(mô tả khía cạnh), câu)`; `s ≥ 0,55` → giống, `s ≤ 0,35` → khác,
  còn lại chưa đủ. Hai ngưỡng là **mặc định chưa tinh chỉnh** trên tập gán tay — ghi rõ
  để không ai tưởng đó là số đã kiểm định.
- **Gợi ý tác giả**: điểm ứng viên = trung bình cosine giữa vector công trình đang xét
  và vector các công trình đã xác nhận của ứng viên; không có công trình xác nhận → không
  điểm, kèm lý do.
- **Gợi ý nghi trùng**: cosine giữa tóm tắt các thành viên; chỉ hiển thị, không đổi gợi ý
  mặc định.
- **Trục chủ đề**: k-means (k-means++, ≤ 50 vòng) trên vector từ khoá; k tự giảm nếu ít
  từ khoá hơn k; nhãn cụm = từ khoá tần suất cao nhất.
- **Rà soát trùng đề tài theo khoá**: với mỗi đồ án của khoá đang rà, top-k cosine trong
  cùng `doc_type` (mặc định 3), loại láng giềng cùng khoá; mức khía cạnh `bai_toan` chia
  theo đúng hai ngưỡng 0,55/0,35 (đổi tên nhãn: `cao`/`vua`/`thap` thay vì `giống`/`khác`/
  `chưa đủ` của đối chiếu đề tài, để không lẫn hai thang đo); ba khía cạnh còn lại luôn là
  `khong_du_du_lieu` vì không có mô tả khía cạnh riêng để so — chỉ có tiêu đề/tóm tắt/từ
  khoá của chính công trình.

## 5. Rà soát trùng đề tài theo khoá

`/doi-chieu/ra-soat` (`cris/ai/screen.py`, `python -m cris ai screen --cohort K18`,
`GET /api/ai/screen`, `GET /api/ai/screen/cohorts`).

**Mục đích**: `dang_ky_do_an` không có ở nguồn, nên không rà được đề tài trùng lúc đăng
ký — thay vào đó rà theo lô sau khi đồ án của một khoá đã có trong kho, so với các khoá
trước. Đúng nỗi đau "đề tài lặp lại qua các năm" mà giảng viên hướng dẫn gặp phải.

**Cách chạy**:

```bash
python -m cris ai embed                 # cần vector trước — screen chỉ rà công trình đã embed
python -m cris ai screen --cohort K18   # --k đổi số láng giềng mỗi công trình (mặc định 3)
```

Ghi `ai_suggestion(kind='topic_overlap', target_id=<work_id>, payload={cohort, neighbours:
[{work_id, title, cohort, score, aspects}]})`, UPSERT theo `UNIQUE(kind, target_id,
model)` — chạy lại không nhân đôi dòng. `GET /api/ai/screen?cohort=&min=cao|vua|thap&page=`
đọc lại gợi ý đã ghi (không tự chạy AI), lọc theo khoá và theo mức cao nhất của `bai_toan`
trong các láng giềng; `GET /api/ai/screen/cohorts` liệt kê số công trình đã rà/đã gắn cờ
theo từng khoá.

**Giới hạn**: chỉ so trên tóm tắt (như mọi chức năng AI khác trong dự án — xem mục 5 bên
dưới); chỉ khía cạnh `bai_toan` có mức tính được (theo cosine toàn văn bản), ba khía cạnh
còn lại luôn `khong_du_du_lieu` vì không có mô tả khía cạnh riêng để tách; **AI gợi ý,
người quyết** — không có hành động gộp, xoá hay đổi trạng thái nào chạy tự động từ kết
quả rà soát, kể cả khi mức là `cao`.

## 6. Giới hạn — nói trước để không ai hiểu nhầm

1. **Chỉ so trên tóm tắt.** Kho không có toàn văn: 39/40 PDF là tóm tắt một trang do máy
   sinh. Mọi kết quả đối chiếu đều ghi dòng *"So trên tiêu đề, tóm tắt và từ khoá — không
   phải toàn văn."* Không có "dẫn chứng theo trang".
2. **Không có điểm phần trăm tương đồng.** Giao diện cố ý không hiện một con số tổng hợp
   (BR-17): một con số tạo cảm giác kết luận; bảng theo khía cạnh buộc người đọc tự xét.
3. **Bài báo thiếu tóm tắt** chỉ có vector từ tiêu đề + từ khoá — chất lượng thấp hơn.
4. **Ngưỡng khía cạnh là mặc định.** Chưa có tập gán tay để tinh chỉnh; việc này ghi ở
   kế hoạch "ngoài phạm vi".
5. **Trộn ngôn ngữ**: tóm tắt tiếng Anh do máy sinh cho đồ án tiếng Việt; mô hình đa ngữ
   xử lý được nhưng không hoàn hảo.
6. **Gợi ý tác giả chỉ có khi người đó đã có công trình xác nhận** — đúng là điểm yếu ở
   giai đoạn đầu, khi liên kết còn thưa; nó tốt dần theo số quyết định của người dùng.

## 7. Kiểm thử

- Test đơn vị dùng provider `fake` (xác định, không tải gì): đối chiếu, khía cạnh, đường
  lui, gom cụm, gợi ý, rà soát trùng đề tài theo khoá, rào chắn "AI không đổi dữ liệu
  nghiệp vụ" (`tests/test_ai_screen.py`).
- Test mô hình thật `tests/test_ai_local_slow.py`, đánh dấu `slow`: 384 chiều, cùng chủ
  đề gần hơn khác chủ đề, xuyên ngôn ngữ Việt–Anh, 64 đoạn dưới 30 giây. Tự bỏ qua khi
  chưa tải mô hình; CI chạy `-m "not slow"`.
- Chạy: `pytest -q` (nhanh) · `pytest -m slow` (cần mô hình).

## 8. Bảng dữ liệu AI

| Bảng | Nội dung |
|---|---|
| `ai_embedding` | `work_id`, `model`, `dim`, `vector`, `text_hash`, `built_at` — một dòng cho mỗi (công trình, mô hình) |
| `ai_topic`, `ai_topic_keyword` | cụm chủ đề và từ khoá thuộc cụm, kèm trọng số tần suất |
| `ai_suggestion` | gợi ý cho hàng đợi: `kind` (`author_link` / `duplicate` / `topic_overlap`), `target_id`, `payload` |
| `ai_query` | lịch sử đối chiếu đề tài: đầu vào, kết quả, provider, người chạy — để xem lại và gửi giảng viên |

Xoá toàn bộ dấu vết AI mà không ảnh hưởng nghiệp vụ: `TRUNCATE ai_query, ai_suggestion,
ai_topic_keyword, ai_topic, ai_embedding`. Không bảng nghiệp vụ nào tham chiếu tới chúng.
