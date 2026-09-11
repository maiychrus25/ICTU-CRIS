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
| **Gợi ý người hướng dẫn** `/doi-soat/huong-dan` | 4.621/5.375 đồ án (86%, xem README mục "Ba số liệu") ghi người hướng dẫn là `ICTU_TEACHER` — tên giữ chỗ, không phải giảng viên thật | Với đồ án giữ chỗ, tìm đồ án cùng đề tài đã có người hướng dẫn thật liên kết, xếp hạng ứng viên theo số phiếu + tổng cosine | Chuyên viên đọc bằng chứng (đồ án dẫn chứng) rồi bấm "đưa vào hàng đợi xác nhận" — chỉ tạo `author_link` **đang chờ**, quyết định vẫn ở hàng đợi tác giả |

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
python -m cris ai mentors       # gợi ý người hướng dẫn cho đồ án đang ghi ICTU_TEACHER
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
  cùng `doc_type` (mặc định 3), loại láng giềng cùng khoá; mức `cao`/`vua`/`thap` (đổi tên
  nhãn khỏi `giống`/`khác`/`chưa đủ` của đối chiếu đề tài, để không lẫn hai thang đo) chia
  theo `SCREEN_THRESHOLDS = (0.90, 0.80)` — **hiệu chỉnh riêng trên phân bố điểm thật**
  (không dùng lại 0,55/0,35 của đối chiếu đề tài, xem số đo ở mục 5) — tính trên
  `max_score`, điểm cosine toàn văn bản của láng giềng cao nhất; ba khía cạnh còn lại của
  từng láng giềng luôn là `khong_du_du_lieu` vì không có mô tả khía cạnh riêng để so — chỉ
  có tiêu đề/tóm tắt/từ khoá của chính công trình.
- **Gợi ý người hướng dẫn**: với mỗi đồ án có lượt tên vai `mentor` giữ chỗ và chưa có liên
  kết nào, lấy `k` đồ án láng giềng gần nhất (cosine) trong tập đồ án đã có người hướng dẫn
  **thật** đã liên kết; gộp láng giềng theo `person_id`, `votes` = số láng giềng, `score` =
  **tổng** (không phải trung bình) cosine của các láng giềng đó — nhiều láng giềng gần hơn
  một láng giềng giống hệt. Ứng viên qua ngưỡng khi `votes ≥ min_votes` **và**
  `score ≥ min_score`; xem mục 6 cho số đo trên dữ liệu thật.

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
python -m cris ai screen --cohort K18 --high 0.92 --mid 0.82   # tự đổi ngưỡng nếu cần
```

Ghi `ai_suggestion(kind='topic_overlap', target_id=<work_id>, payload={cohort, max_score,
level, neighbours: [{work_id, title, cohort, score, aspects}]})`, UPSERT theo
`UNIQUE(kind, target_id, model)` — chạy lại không nhân đôi dòng. `max_score` là điểm láng
giềng cao nhất; `level` (`cao`/`vua`/`thap`) là mức của `max_score` theo `SCREEN_THRESHOLDS`
(hoặc `--high`/`--mid` nếu đổi lúc chạy). `GET /api/ai/screen?cohort=&min=cao|vua|thap&
min_score=&page=` đọc lại gợi ý đã ghi (không tự chạy AI), lọc theo khoá, theo mức và/hoặc
theo điểm số tối thiểu, **sắp theo `max_score` giảm dần**; `GET /api/ai/screen/cohorts`
liệt kê số công trình đã rà/đã gắn cờ (`level == "cao"`) theo từng khoá.

**Hiệu chỉnh ngưỡng (10/09/2026, DB thật, cohort 21, 529 đồ án đã `ai embed`, mô hình
`local`)**: đo `max_score` của mỗi đồ án — phân vị p50=0,835 · p75=0,870 · p90=0,897 ·
p95=0,908 · p99=0,928; số đồ án có `max_score` ≥ 0,80/0,85/0,90/0,95 lần lượt là
370 (69,9%) / 205 (38,8%) / 47 (8,9%) / 2 (0,4%). Ngưỡng khía cạnh 0,55/0,35 kế thừa nhầm
từ đối chiếu đề tài (hiệu chỉnh cho so một khía cạnh với một câu, không phải so toàn văn
bản hai công trình cùng loại) gắn cờ 529/529 = 100% — vô dụng. Đọc từng cặp: quanh 0,80–
0,85 phần lớn chỉ trùng lớp từ vựng chung của đồ án CNTT (VD: hai website "quản lý ... cho
công ty/cửa hàng ..." khác hẳn đề tài); từ 0,90 trở lên các cặp đọc lên là cùng đề tài thật,
ví dụ: "Xây dựng ứng dụng Android hỗ trợ du lịch thông minh" ~ "Xây dựng ứng dụng du lịch
trên nền tảng Android" (0,9503); "Xây dựng ứng dụng học tiếng Anh có tích hợp AI trên
Android" ~ "Xây dựng ứng dụng học lập trình thông minh tích hợp AI trên nền tảng Android"
(0,9495); "Ứng dụng AI xây dựng hệ thống điểm danh sinh viên dựa trên nhận diện khuôn mặt"
~ chính đề tài đó lặp lại nguyên văn (0,9510). Chọn `HIGH = 0.90` (gắn cờ 47/529 = 8,9%,
trong khoảng mục tiêu 5–15%), `MID = 0.80` (ranh dưới của lớp "cùng vốn từ chung ngành").

**Giới hạn**: chỉ so trên tóm tắt (như mọi chức năng AI khác trong dự án — xem mục 7 bên
dưới); chỉ khía cạnh `bai_toan` của mỗi láng giềng có mức tính được (theo cosine toàn văn
bản), ba khía cạnh còn lại luôn `khong_du_du_lieu` vì không có mô tả khía cạnh riêng để
tách; ngưỡng hiệu chỉnh trên một cohort/một mô hình — đổi cohort hay mô hình khác có thể
cần đo lại; **AI gợi ý, người quyết** — không có hành động gộp, xoá hay đổi trạng thái nào
chạy tự động từ kết quả rà soát, kể cả khi mức là `cao`.

## 6. Gợi ý người hướng dẫn (ICTU_TEACHER)

`/doi-soat/huong-dan` (`cris/ai/mentor.py`, `python -m cris ai mentors`,
`GET /api/ai/mentors`, `POST /api/ai/mentors/{work_id}/accept`).

**Mục đích**: 4.621/5.375 đồ án (86%, xem README mục "Ba số liệu") ghi người hướng dẫn là
`ICTU_TEACHER` — một tên giữ chỗ do nguồn không có liên kết tới trang giảng viên, không
phải một giảng viên thật. **Giả định** của tính năng (chỉ là gợi ý thống kê, ghi rõ trong
docstring `suggest_mentors`): đồ án cùng đề tài thường có cùng giảng viên hướng dẫn, vì một
giảng viên thường nhận nhiều đồ án cùng hướng qua các khoá/nhóm sinh viên — có thể sai (một
đề tài phổ biến có thể do nhiều giảng viên khác nhau hướng dẫn), nên đây chỉ đưa vào hàng
đợi, không bao giờ tự xác nhận.

**Cách chạy**:

```bash
python -m cris ai embed                                  # cần vector trước
python -m cris ai mentors                                # --k/--min-votes/--min-score để đổi
python -m cris ai mentors --k 5 --min-votes 2 --min-score 0.70   # giá trị mặc định
```

Ghi `ai_suggestion(kind='mentor', target_id=<work_id>, payload={mention_id,
candidates: [{person_id, display_name, degree, votes, score, evidence:
[{work_id, title, score}]}]})`, UPSERT theo `UNIQUE(kind, target_id, model)`; đồ án không
còn ứng viên nào qua ngưỡng ở lần chạy sau thì gợi ý cũ bị xoá (không để lại gợi ý lỗi
thời). `GET /api/ai/mentors?unit=&min_votes=&page=` đọc lại gợi ý đã ghi, kèm `pending_link`
(liên kết đang chờ/đã có cho lượt tên đó, nếu có — để giao diện biết đã đưa vào hàng đợi
chưa). `POST /api/ai/mentors/{work_id}/accept {person_id}` (vai trò `rd_officer`) tạo
`author_link` trạng thái **`ChoXacNhan`** (đang chờ, chưa xác nhận) cho lượt tên giữ chỗ,
`confidence='ai_mentor'`, `basis={ai:true, votes, score}`, qua `cris.link.add_candidate` —
409 nếu lượt tên đã có liên kết đang chờ/đã xác nhận. Liên kết này hiện ra ở
`GET /api/queue/authors` như mọi liên kết khác; **quyết định cuối vẫn ở hàng đợi tác giả**
(`cris.link.decide_link`, BR-18) — route chấp nhận gợi ý không bao giờ tự xác nhận.

**`cris/normalize.py` đã có nhánh dự phòng đọc `meta.GVHD`** (11/09/2026, lát cắt I4): khi
`archive.mentors` rỗng — nguồn không dựng được thẻ `<a class="lv-mentor-link">` khi trang chỉ
có GVHD giữ chỗ — `extract_fields` đọc `meta["GVHD"]` (nhãn đầu của `field_map["mentor"]`,
`cris/rules.py`) và tạo lượt tên vai `mentor`, đúng cách nó đã đọc `meta["Sinh viên"]` cho vai
`student`. Giá trị giữ chỗ (`ICTU_TEACHER`, đã có sẵn trong `RULES_V1.name_norm.placeholders`
— không cần bump `rule_set` version) trở thành một lượt tên `is_placeholder=true`; giá trị tên
thật (có thể nhiều người, `split_names` tách theo `,`/`;` như `archive.mentors`) trở thành các
lượt tên `is_placeholder=false`. Chạy lại toàn bộ đồ án đã đồng bộ trước đó cần `python -m cris
normalize --redo --doc-type do_an` (mới ở lát cắt này — `normalize_pending(force=True,
doc_type=...)`, xem `cris/normalize.py`): các bản ghi `do_an` cũ đã có `work` không được
`normalize_pending` mặc định xử lý lại (nó chỉ chạy phần đang chờ, `NOT EXISTS work`) nên cần
cờ `--redo` để "vá" hồi tố các work đã chuẩn hoá từ trước khi có nhánh GVHD.

**Đo trên dữ liệu thật (11/09/2026, DB thật, sau `normalize --redo --doc-type do_an`, ~41,5
giây cho 5.375 đồ án, rồi `python -m cris ai mentors` với mô hình `local`)**:
`{'created': 0, 'updated': 5375, 'skipped': 0}` từ `normalize --redo`, tạo đúng **4.621** lượt
tên vai `mentor` giữ chỗ (khớp số liệu README "Ba số liệu") — không đồ án `do_an` nào còn
thiếu lượt tên vai `mentor` sau khi chạy (trước đó 4.655/5.375 không có lượt tên mentor nào).
`python -m cris ai mentors` (mặc định `k=5, min_votes=2, min_score=0.70`) trả `scanned=4621
suggested=1381` trong ~12 giây — **29,9%** đồ án đích có ít nhất một ứng viên qua ngưỡng, nằm
trong khoảng hợp lý (không dưới 5%, không trên 80%) nên **giữ nguyên ngưỡng mặc định**, không
cần hiệu chỉnh. Phân vị `score` của ứng viên hàng đầu mỗi đồ án (1.381 đồ án có gợi ý): p10 ≈
1,23, p50 ≈ 1,44, p90 ≈ 1,66 — đều cách xa `min_score=0,70` (biên an toàn, không sát ngưỡng).
Phân vị `votes`: p10 = p50 = p90 = 2 (1.304/1.381 ứng viên hàng đầu dừng đúng ở `min_votes=2`,
77 đạt 3 — tối đa có thể với `k=5` khi láng giềng rải cho nhiều người); `min_votes=2` vừa đủ
chặt để không cho gợi ý chỉ dựa trên một láng giềng, không quá chặt tới mức bỏ sót phần lớn.

Năm ví dụ (điểm cao nhất, cùng một giảng viên vì đề tài "kiểm thử tự động bằng Selenium" phổ
biến ở một khoá — đúng cảnh báo trong docstring `suggest_mentors` về "một đề tài phổ biến"):

| Đồ án đích | Ứng viên | votes | score | Đồ án dẫn chứng |
|---|---|---|---|---|
| Thực nghiệm kiểm thử Website với công cụ kiểm thử tự động Selenium | Nguyễn Lan Oanh | 3 | 2,606 | Tự động hóa kiểm thử website đặt lịch spa sử dụng Selenium với AI hỗ trợ thiết kế testcase |
| Nghiên cứu kiểm thử tự động với Senlenium, TestNG... | Nguyễn Lan Oanh | 3 | 2,561 | Nghiên cứu, triển khai kiểm thử tự động sử dụng Selenium và AI hỗ trợ thiết kế test case cho hệ thống website quản lý đào tạo trung tâm Tiếng Anh |
| Kiểm thử tự động ứng dụng Web sử dụng công cụ Selenium | Nguyễn Lan Oanh | 3 | 2,554 | Tự động hóa kiểm thử website đặt lịch spa sử dụng Selenium với AI hỗ trợ thiết kế testcase |
| Kiểm thử ứng dụng trên nền Web bằng công cụ Selenium | Nguyễn Lan Oanh | 3 | 2,550 | Nghiên cứu và triển khai kiểm thử tự động website bán đồ cho thú cưng sử dụng Selenium kết hợp ứng dụng trí tuệ nhân tạo trong việc thiết kế test case |
| Xây dựng các bộ test dựa trên phần mềm Selenium ứng dụng trên kiểm thử Web | Nguyễn Lan Oanh | 3 | 2,542 | Tự động hóa kiểm thử website đặt lịch spa sử dụng Selenium với AI hỗ trợ thiết kế testcase |

`GET /api/ai/mentors?page=1` trả 50 dòng ở trang đầu (không rỗng); `GET /api/quality` báo
`mentions_placeholder` tăng lên 4.923 (gồm cả vai `student` giữ chỗ có từ trước và 4.621 lượt
tên vai `mentor` mới).

## 7. Giới hạn — nói trước để không ai hiểu nhầm

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

## 8. Kiểm thử

- Test đơn vị dùng provider `fake` (xác định, không tải gì): đối chiếu, khía cạnh, đường
  lui, gom cụm, gợi ý, rà soát trùng đề tài theo khoá, rào chắn "AI không đổi dữ liệu
  nghiệp vụ" (`tests/test_ai_screen.py`); gợi ý người hướng dẫn — dựng lượt tên vai `mentor`
  giữ chỗ/đã liên kết trực tiếp bằng SQL, không cần `cris sync`/`normalize` thật
  (`tests/test_ai_mentor.py`).
- Test mô hình thật `tests/test_ai_local_slow.py`, đánh dấu `slow`: 384 chiều, cùng chủ
  đề gần hơn khác chủ đề, xuyên ngôn ngữ Việt–Anh, 64 đoạn dưới 30 giây. Tự bỏ qua khi
  chưa tải mô hình; CI chạy `-m "not slow"`.
- Chạy: `pytest -q` (nhanh) · `pytest -m slow` (cần mô hình).

## 9. Bảng dữ liệu AI

| Bảng | Nội dung |
|---|---|
| `ai_embedding` | `work_id`, `model`, `dim`, `vector`, `text_hash`, `built_at` — một dòng cho mỗi (công trình, mô hình) |
| `ai_topic`, `ai_topic_keyword` | cụm chủ đề và từ khoá thuộc cụm, kèm trọng số tần suất |
| `ai_suggestion` | gợi ý cho hàng đợi: `kind` (`author_link` / `duplicate` / `topic_overlap` / `mentor`), `target_id`, `payload` |
| `ai_query` | lịch sử đối chiếu đề tài: đầu vào, kết quả, provider, người chạy — để xem lại và gửi giảng viên |

Xoá toàn bộ dấu vết AI mà không ảnh hưởng nghiệp vụ: `TRUNCATE ai_query, ai_suggestion,
ai_topic_keyword, ai_topic, ai_embedding`. Không bảng nghiệp vụ nào tham chiếu tới chúng.
