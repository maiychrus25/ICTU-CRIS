# Kiểm chứng giả định của đề tài bằng dữ liệu thực

Ngày đo: 09–10/09/2026. Nguồn: toàn bộ 8.034 bản ghi + 410 hồ sơ giảng viên đã kéo từ
`repository.ictu.edu.vn`, cộng mẫu 40 tệp PDF.

Tài liệu đối chiếu:
- `ictu-research-service-overview.md` — Dịch vụ khai thác tri thức nghiên cứu
- Phân tích người dùng và quy trình quản lý công bố khoa học ICTU

Mục đích: hai tài liệu đó nêu đúng vấn đề nhưng phần lớn còn ở dạng giả định. Dưới đây là
những giả định **kiểm chứng được bằng dữ liệu công khai**, kèm số đo. Phần nào không kiểm
chứng được từ kho thì ghi rõ là không kiểm chứng được.

---

## Tóm tắt cho người đọc vội

| Giả định trong tài liệu | Số đo thực tế | Kết luận |
|---|---|---|
| "Có toàn văn đọc được" (mức 2, §3.3) | 39/40 PDF là **1 trang tóm tắt do máy sinh** | **Không tồn tại.** Phải bỏ mức 2 hoặc đổi nguồn |
| "Loại trùng là yêu cầu thực tế" (§3.2) | 11 nhóm bài báo trùng (0,6%) | Đúng, nhưng nhỏ hơn nhiều so với vấn đề khác |
| "Liên kết tác giả" (§3.2) | Hiện **8%** bài báo nối được với giảng viên | **Đây mới là vấn đề lớn nhất** |
| "Một bài nhiều khoa → đếm lặp" (§4) | **0 bài** thuộc >1 đơn vị; 37% không có đơn vị | Rủi ro tài liệu lo chưa xảy ra; rủi ro thật là chỗ khác |
| "Chỉ so tên là không đủ" (§3.1) | 703 đồ án cùng mở đầu "xây dựng website" | Đúng, và đo được |
| Tóm tắt có dùng cho đối chiếu ngữ nghĩa được không | Trùng 6-gram giữa các tóm tắt = **0,000** | Dùng được |

---

## 1. Mức dữ liệu thực có: chỉ có tóm tắt, không có toàn văn

Tài liệu §3.3 chia hai mức năng lực: *"có thông tin thư mục hoặc tóm tắt"* và *"có toàn
văn đọc được"*, và ghi nhận *"một PDF mẫu trên kho chỉ có một trang tóm tắt"*.

Đo trên mẫu ngẫu nhiên 40 PDF trong tổng 5.644 tệp:

```
Số trang  : median 1  | min 1 | max 8
Ký tự text: median 1.304 | min 687 | max 4.799
39/40 tệp có đúng 1 trang. Tệp 8 trang duy nhất là hướng dẫn Zotero, không phải công trình.
```

Kiểm tra metadata cho thấy các tệp này **do máy sinh, không phải bản gốc tải lên**:

```
Producer : ReportLab PDF Library - (opensource)
Page size: A4
Nội dung : tiêu đề (tiếng Anh) + tác giả + Abstract + Keywords
```

Nghĩa là: một PDF đồ án chỉ chứa tiêu đề, tên sinh viên, tóm tắt tiếng Anh và từ khoá.
Không có chương, không có phương pháp, không có kết quả, không có tài liệu tham khảo.

**Hệ quả cho đề tài:**

- Mức 2 trong §3.3 (*"tìm đoạn liên quan, dẫn chứng theo trang"*) **không thực hiện được**
  trên nguồn này. Không có trang nào để dẫn.
- Mọi kế hoạch RAG trên toàn văn đều không có nguyên liệu.
- §3.1 (đối chiếu đề tài) vẫn làm được, nhưng phải nói rõ là **đối chiếu ở mức tóm tắt**,
  không phải đối chiếu nội dung công trình.
- Nếu vẫn muốn mức 2, phải xác định nguồn khác: bản nộp gốc ở khoa, hoặc thư viện trường.
  Đây là một câu hỏi phải mang đi khảo sát.

Điểm tích cực: tóm tắt **không phải văn mẫu**. Đo trùng lặp cụm 6 từ giữa 39 tóm tắt:

```
Cụm 6 từ dùng chung ở >=5 tài liệu : 0
Jaccard 6-gram trung bình giữa 2 tóm tắt bất kỳ : 0,000
Cặp có độ trùng > 0,15 : 0/400
```

Chỉ lặp công thức mở đầu (`"This study investigates the application..."` 3 lần trong 39),
đúng như văn phong học thuật bình thường. Nội dung thực sự khác nhau, nên dùng được cho
tìm kiếm ngữ nghĩa và đối chiếu đề tài.

---

## 2. Liên kết tác giả — vấn đề lớn nhất, và cũng là đóng góp đo được rõ nhất

Tài liệu §3.2 nêu nhu cầu *"liên kết tác giả"* và §2 nêu *"liên kết tác giả chưa chắc chắn"*.
Đây không phải một vấn đề phụ. Đo trên toàn bộ 410 hồ sơ giảng viên và 1.907 bài báo:

```
Hiện tại  :  155/1907 bài báo được nối với hồ sơ giảng viên  ( 8%)
             48/410 giảng viên có ít nhất 1 bài báo trên hồ sơ (12%)
             1.752 bài báo không nối với giảng viên nào
```

Ca đối chiếu cụ thể — **TS. Nguyễn Văn Tảo**:

```
Hồ sơ giảng viên tự báo          :  5 bài báo
Tên ông xuất hiện trong tác giả  : 29 bài báo
Tìm kiếm của chính site trả về   : 23 bài báo
```

Ba con số cho cùng một người, trên cùng một hệ thống.

**Chức năng "thống kê công bố khoa học" ở §3.2 hiện chỉ nhìn thấy 8% kho.** Một trưởng bộ
môn dùng màn hình này để tổng hợp sẽ nhận số liệu sai lệch một bậc, không phải sai vài phần
trăm.

### Khôi phục được bao nhiêu

Thử nối lại bằng khớp tên đã chuẩn hoá (bỏ dấu, bỏ thứ tự từ, cắt tiền tố học hàm/học vị):

```
Hiện tại :  155/1907 bài báo (8%)  |  48/410 giảng viên
Khớp tên : 1638/1907 bài báo (86%) | 265/410 giảng viên
>>> Khôi phục thêm 1.525 bài báo và 217 giảng viên
```

Từ 8% lên 86% chỉ bằng chuẩn hoá tên. Đây là con số nên đưa vào phần "đóng góp của đề tài"
(§6 tài liệu tổng quan) — nó đo được, so sánh được trước/sau, và kiểm chứng được thủ công
trên một mẫu.

### Vì sao liên kết đứt

Tên tác giả trong 1.907 bài báo tồn tại song song hai hệ chính tả:

```
Tổng lượt tác giả : 5.762  |  chuỗi tên phân biệt : 2.788
  có dấu tiếng Việt : 1.855 (32%)   vd: "Trần Lê Duy"
  không dấu / Latin : 3.907 (68%)   vd: "The-Vinh Nguyen", "Minh-Hue Luong Thi"
  dạng đảo họ-tên có gạch nối : 1.035 (18%)
```

Hồ sơ giảng viên lưu tên **có dấu** (`"PGS.TS. Phùng Trung Nghĩa"`), còn 68% lượt tác giả
ghi **không dấu theo kiểu quốc tế**. Đây là lý do kỹ thuật khiến liên kết đứt.

Vấn đề tương tự ở tên GVHD của đồ án và luận văn:

```
1.065 lượt ghi GVHD -> 202 chuỗi tên phân biệt -> 148 người sau chuẩn hoá
39 người bị ghi bằng nhiều cách viết khác nhau (93 chuỗi gộp về 39 người)
```

Ví dụ một người có 4 biến thể:

```
"Nguyễn Đình Dũng" / "TS Nguyễn Đình Dũng" / "TS. Nguyễn Đình Dũng" / "ThS. Nguyễn Đình Dũng"
"Nguyễn Văn Tảo" / "T.s Nguyễn Văn Tảo" / "TS Nguyễn Văn Tảo" / "TS. Nguyễn Văn Tảo"
"Trần Văn Khánh" / "TS Trần Văn Khánh" / "Trần Văn-Khánh"
```

**Cảnh báo thiết kế:** biến thể thứ nhất và thứ tư của Nguyễn Đình Dũng ghi **học vị khác
nhau** (TS vs ThS). Tương tự Vũ Vinh Quang có cả "TS" và "Th.S". Chuẩn hoá tên không được
âm thầm chọn một học vị — đây là mâu thuẫn dữ liệu cần người xác nhận, đúng như tài liệu
nói *"người có chuyên môn xác nhận những trường hợp mơ hồ"*.

### Một hạn chế của số đo trên

17% bài báo (316 bài) có danh sách tác giả **bị cắt cụt bởi dấu "…"** ở trang danh mục:

```
"Minh-Hue Luong Thi, The-Vinh Nguyen, Van-Viet Nguyen,Duc-Quang Vu, Trung-Nghia P…"
```

Trang chi tiết có đủ danh sách. Nghĩa là con số 86% ở trên **còn thiếu** — muốn đủ phải đọc
1.907 trang chi tiết. Khi triển khai thật thì phải lấy từ trang chi tiết, không lấy từ danh mục.

---

## 3. Bài toán "một bài nhiều khoa" — rủi ro thật nằm chỗ khác

Tài liệu §4 phần "Tình huống cần xử lý đúng ngay từ đầu" đặt vấn đề:

> *Một bài báo có hai tác giả thuộc hai khoa. [...] Không được cộng cơ học hai số của khoa
> rồi gọi đó là tổng số công trình duy nhất của trường.*

Đo thực tế trên 13 đơn vị trong bộ lọc:

```
CNTT 363 | KHCB 267 | HTTTKT 109 | KT&CN 107 | KT&QT 97 | ICTU 56 | NT&TT 44
TĐH 39 | ĐTVT 38 | TTĐPT 35 | ĐTTT 29 | HTTKT 7 | "Trường ĐH CNTT&TT" 3

Cộng cơ học 13 đơn vị : 1.194
Bài báo duy nhất       : 1.194
>>> Đếm lặp khi cộng cơ học : 0 bài
>>> Bài thuộc >1 đơn vị      : 0  (tối đa 1 đơn vị/bài)
```

**Trường `dept` là đơn trị.** Một bài báo được gán đúng một đơn vị. Tình huống tài liệu lo
ngại hiện **không thể xảy ra** — vì mô hình dữ liệu không biểu diễn được nó.

Nhưng điều đó không có nghĩa là không có vấn đề. Có hai vấn đề khác, đo được:

**a) 713/1.907 bài báo (37%) không được gán đơn vị nào.** Báo cáo theo khoa hôm nay chỉ phủ
63% kho. Đây là con số phải nói với Phòng KH-CN & HTQT trước khi họ tin vào bất kỳ bảng
tổng hợp nào.

**b) Chính tên đơn vị cũng chưa chuẩn hoá.** `"ICTU"` (56 bài) và `"Trường Đại học Công nghệ
thông tin và truyền thông"` (3 bài) là cùng một thực thể ghi hai cách.

**Hệ quả cho thiết kế:** nhu cầu mà tài liệu nêu là đúng và phải làm, nhưng cách làm không
phải là "chống đếm lặp" mà là **đổi mô hình dữ liệu**: quan hệ công trình ↔ đơn vị phải là
nhiều-nhiều và suy ra từ quan hệ công trình ↔ tác giả ↔ đơn vị, chứ không phải một trường
văn bản gán tay. Đây cũng là lý do mục 2 ở trên là điều kiện tiên quyết: không nối được tác
giả thì không suy ra được đơn vị.

---

## 4. Loại trùng bản ghi — có thật, nhưng cần hai quy tắc khác nhau

Tài liệu §3.2 dẫn chứng hai bản ghi cùng DOI. Đo trên toàn bộ kho:

### Bài báo: 11 nhóm trùng, 11 bản ghi dư (0,6%)

Điểm đáng chú ý là **metadata giữa các bản trùng mâu thuẫn nhau**, nên gộp không phải là
xoá bớt một bản mà là đối soát:

| Công trình | Bản 1 | Bản 2 |
|---|---|---|
| Cocktail Party Effect Using Parallel Intra and Inter Self-attention | 2025 | 2024 |
| Integrating ESM-2 and Graph Neural Networks... | ACS Omega | ACS omega |
| A Large Language Model-Based Question Answering System... | Journal on Information Technologies & Communications | Bộ thông tin truyền thông |

Bản ghi trùng có slug kết thúc bằng `-2`, tức WordPress tự thêm hậu tố khi nhập lần hai.
Đây là dấu vết của việc **nhập dữ liệu hai lần**, không phải hai công trình khác nhau.

### Đồ án: 43 nhóm trùng tiêu đề — nhưng 34 nhóm KHÔNG được gộp

Đây là ràng buộc thiết kế quan trọng nhất của phần loại trùng:

```
Khác sinh viên (đồ án nhóm — KHÔNG được gộp) : 34 nhóm
Cùng sinh viên (nghi trùng thật — nên gộp)   :  9 nhóm
```

Ví dụ nhóm 8 bản ghi cùng tiêu đề *"Xây dựng chuỗi sản phẩm truyền thông chào mừng kỷ niệm
10 năm ngày truyền thống..."* — tám sinh viên khác nhau, cùng khoá 14. Đây là đồ án nhóm,
tám bản ghi đều hợp lệ.

**Quy tắc loại trùng phải phân biệt hai trường hợp**, nếu chỉ khớp tiêu đề thì sẽ xoá mất
52 bản ghi thật. Khoá gộp tối thiểu là (tiêu đề chuẩn hoá + sinh viên + khoá).

---

## 5. Đối chiếu đề tài — khả thi, và đo được vì sao "chỉ so tên" không đủ

Tài liệu §3.1 lấy ví dụ *"ứng dụng học tiếng Anh bằng AI"* với hai hướng khác nhau. Ví dụ
này có thật trong kho. Truy vấn thử trên 5.375 đồ án:

```
Đồ án chạm >= 3 từ khoá : 66
  [6] Xây dựng ứng dụng học tiếng Anh cho trẻ em có tích hợp AI hỗ trợ luyện phát âm
  [4] Xây dựng ứng dụng học từ vựng Tiếng Anh ngành CNTT trên nền tảng android
  [4] Xây dựng ứng dụng học tiếng Anh trên điện thoại di động nền tảng Android
  [4] Xây dựng chương trình luyện thi Tiếng Anh chuẩn A2 trên thiết bị di động
  [4] Xây dựng Website ôn luyện thi tiếng anh B1
```

Đúng như tài liệu mô tả: cùng chủ đề nhưng khác đối tượng (trẻ em / sinh viên CNTT), khác
mục tiêu (luyện phát âm / học từ vựng / luyện thi chứng chỉ). Có nguyên liệu để giải thích
điểm giống và khác.

### Vì sao không thể chỉ so tiêu đề — con số cụ thể

```
5.375 đồ án -> 810 khuôn mở đầu (3 từ đầu)
   703×  "xây dựng website..."
   404×  "xây dựng hệ..."
   350×  "xây dựng ứng..."
   292×  "xây dựng chương..."
   221×  "thiết kế hệ..."
```

13% toàn bộ đồ án bắt đầu bằng đúng ba từ *"Xây dựng website"*. Khớp tiêu đề sẽ cho hàng
trăm kết quả giả.

### Từ khoá không dùng trực tiếp làm trục chủ đề được

```
5.375 đồ án -> 10.951 từ khoá phân biệt (23.400 lượt, TB 4,4/đồ án)
Từ khoá chỉ xuất hiện đúng 1 lần : 8.362 (76%)
Top: công nghệ thông tin(425) · thương mại điện tử(335) · website bán hàng(166)
     tự động hoá(153) · thái nguyên(138) · ứng dụng di động(125) · IoT(115)
```

Từ vựng không được kiểm soát: hơn ba phần tư từ khoá chỉ xuất hiện một lần. Muốn dùng làm
bộ lọc chủ đề thì phải gom cụm trước, không dùng thẳng được. Đây là một hạng mục công việc
cụ thể nên đưa vào phạm vi.

---

## 6. Dữ liệu cho quy trình phê duyệt — tài liệu đã kết luận đúng

Tài liệu quy trình §6 ghi:

> *Kho công khai ICTU là nguồn tài liệu tham chiếu. Nó không đủ để suy ra kỳ báo cáo, hồ sơ
> chờ duyệt, lịch sử trả lại hoặc quyết định nội bộ.*

Xác nhận: đúng. Đã rà toàn bộ bề mặt công khai, không có gì liên quan đến kỳ báo cáo, trạng
thái duyệt, hay lịch sử xử lý. Kho là WordPress với 6 custom post type, không có bảng quy
trình, không có trường trạng thái, không có người dùng nào ngoài 2 tài khoản quản trị.

Nhưng có ba thứ **tái sử dụng được** cho hệ thống mới, không phải nhập lại:

| Dữ liệu | Độ phủ | Dùng để |
|---|---|---|
| Hồ sơ giảng viên: email | 410/410 (100%) | Định danh người dùng, gửi thông báo |
| Hồ sơ giảng viên: ORCID | 372/410 (91%) | Khoá nối tác giả tin cậy nhất |
| Hồ sơ giảng viên: Google Scholar | 368/410 (90%) | Đối chiếu công bố ngoài kho |
| Đơn vị của bài báo | 1.194/1.907 (63%) | Phân nhóm theo khoa |
| Năm xuất bản | 1.907/1.907 (100%) | Chia kỳ báo cáo |

**ORCID phủ 91% là phát hiện quan trọng.** Tài liệu không nhắc tới ORCID, nhưng đây là khoá
nối tác giả chuẩn quốc tế và đã có sẵn. Nó giải quyết trực tiếp bài toán ở mục 2 — chính xác
hơn nhiều so với khớp tên — và còn cho phép đối soát với nguồn ngoài mà không cần đoán tên.

Riêng nhu cầu hợp tác quốc tế mà tài liệu quy trình nêu (*"không suy ra hợp tác quốc tế chỉ
vì tên tác giả là tiếng Anh"*): cảnh báo này đặc biệt đúng ở đây, vì **68% lượt tác giả
trong kho ghi không dấu kiểu Latin** — trong đó phần lớn là người Việt. Suy ra quốc tịch từ
dạng chữ sẽ sai hàng loạt. Kho **không có trường đơn vị công tác hay quốc gia** của tác giả,
nên chức năng này chưa có nguyên liệu.

---

## 7. Ba lỗi chặn phải sửa trước khi đồng bộ

Chi tiết đầy đủ trong `README.md`. Ba lỗi ảnh hưởng trực tiếp tới đề tài:

1. **`ICTU_TEACHER`** — 4.621/5.375 đồ án (86%) không có tên GVHD, chỉ có placeholder. Mọi
   thống kê "giảng viên hướng dẫn bao nhiêu đồ án" hiện chỉ đúng trên 14% kho. Đây là dữ
   liệu **đã mất ở nguồn nhập**, không khôi phục được bằng thuật toán.

2. **Phân trang bỏ sót 11 đồ án** — duyệt hết 269 trang chỉ ra 5.364/5.375 bản ghi. Bất kỳ
   quy trình đồng bộ nào lật trang tuần tự đều mất 11 bản ghi này mà không báo lỗi. Đã liệt
   kê trong `out/_doan_unreachable.json`.

3. **Danh sách tác giả bị cắt ở trang danh mục** — 17% bài báo. Đồng bộ phải đọc trang chi
   tiết, không đọc danh mục.

---

## 8. Đề xuất điều chỉnh phạm vi

Dựa trên số đo, không dựa trên phán đoán:

| Hạng mục trong tài liệu | Đề xuất | Lý do |
|---|---|---|
| §3.3 mức 2 "toàn văn, dẫn theo trang" | **Đưa ra ngoài phạm vi** | Không có toàn văn trong kho |
| §3.2 liên kết tác giả | **Đưa lên hạng mục trung tâm** | 8% → 86%, đo được, là đóng góp rõ nhất |
| §3.2 loại trùng | Giữ, nhưng tách 2 quy tắc | 34/43 nhóm đồ án trùng tên là đồ án nhóm |
| §4 chống đếm lặp đa khoa | Đổi thành **thiết kế quan hệ nhiều-nhiều** | Hiện 0 bài đa khoa; 37% không có khoa |
| Gom cụm từ khoá | **Bổ sung vào phạm vi** | 76% từ khoá chỉ xuất hiện 1 lần |
| Dùng ORCID làm khoá nối | **Bổ sung vào phạm vi** | Đã có sẵn 91%, tài liệu chưa nhắc tới |

Về tên đề tài: tài liệu quy trình đề xuất *"Xây dựng hệ thống hỗ trợ tổng hợp, đối soát và
phê duyệt dữ liệu công bố khoa học tại ICTU"*. Số đo ủng hộ hướng này, với một lưu ý: phần
**"đối soát"** hiện có nhiều nguyên liệu và giá trị đo được nhất; phần **"phê duyệt"** hoàn
toàn phải xây mới vì kho không có dữ liệu quy trình nào.

---

## 9. Bổ sung vào danh sách câu hỏi khảo sát

Tài liệu quy trình §8 đã có danh sách tốt. Số đo ở trên đẻ thêm sáu câu, nên hỏi trong cùng
buổi:

1. **Bản nộp gốc (toàn văn) của đồ án, luận văn đang nằm ở đâu?** Kho chỉ có tóm tắt 1 trang
   do máy sinh. Nếu có bản gốc ở khoa hoặc thư viện thì phạm vi đề tài thay đổi đáng kể.

2. **Tóm tắt tiếng Anh trong PDF do ai tạo?** Cấu trúc tệp cho thấy do máy sinh hàng loạt.
   Cần biết nó dịch từ tóm tắt tiếng Việt hay sinh mới — ảnh hưởng tới mức tin cậy khi dùng
   làm cơ sở đối chiếu.

3. **4.621 đồ án mất tên GVHD — nguồn nhập gốc còn không?** Nếu còn, đây là việc khôi phục
   dữ liệu; nếu mất, phải chấp nhận và thiết kế hệ thống trên 14% có tên.

4. **Trường "đơn vị" của bài báo được gán theo tác giả nào?** 37% bài không có đơn vị. Cần
   biết quy tắc gán hiện tại trước khi thiết kế quan hệ mới.

5. **ORCID trên hồ sơ giảng viên do ai nhập và có được đối chiếu không?** Phủ 91%, là khoá
   nối tốt nhất đang có — nhưng phải biết độ tin cậy.

6. **Quy tắc đếm công trình đồng tác giả nội bộ là gì?** Đã đo: 56 bài có nhiều hơn một
   giảng viên ICTU, cao nhất 7 người/bài. Tài liệu nói đúng rằng quy tắc này *"phải theo quy
   định của ICTU, không để đội phát triển tự quyết"* — nên đây là câu hỏi bắt buộc.

---

## Tái lập số liệu

```bash
cd ~/Documents/ictu-repository-audit
python3 harvest.py archives      # 8.034 bản ghi
python3 gv_detail.py             # 410 hồ sơ giảng viên + số đếm + liên kết
python3 normalize.py             # chuẩn hoá trường "Loại bài"
```

Tệp phân tích: `out/giang-vien.details.jsonl`, `out/_baibao_by_dept.json`,
`out/_pdf_probe.json`, `out/_gvhd_linkage.json`, `out/_doan_unreachable.json`.
