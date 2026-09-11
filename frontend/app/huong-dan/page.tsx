// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import {
  Bot, Building2, CheckCircle2, CircleAlert, ExternalLink, GraduationCap, Landmark, LockKeyhole, School,
} from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { ApiError } from "@/lib/api";
import { stateLabels } from "@/lib/labels";
import { useMe } from "@/lib/queries";
import { cn } from "@/lib/utils";

type RoleGuide = {
  id: string;
  title: string;
  summary: string;
  userRoles: string[];
  icon: typeof Building2;
  steps: { title: string; description: string; href: string; linkLabel: string }[];
  images: { src: string; alt: string; caption: string; width: number; height: number }[];
};

const roleGuides: RoleGuide[] = [
  {
    id: "phong-khcn",
    title: "Phòng KH-CN",
    summary: "Đối soát dữ liệu toàn trường, vận hành kỳ báo cáo và chịu trách nhiệm cho các quyết định cuối.",
    userRoles: ["rd_officer"],
    icon: Building2,
    steps: [
      {
        title: "Tra cứu và xuất CSV",
        description: "Nhập từ khoá, chọn loại tài liệu, năm, đơn vị hoặc chủ đề rồi bấm Tra cứu. Nút Tải CSV xuất đúng tập kết quả đang lọc, ở dạng UTF-8 để mở bằng Excel.",
        href: "/tra-cuu/",
        linkLabel: "Mở Tra cứu",
      },
      {
        title: "Xử lý hàng đợi tác giả",
        description: "Ở tab Chờ xác nhận, kiểm tra công trình, ứng viên và lý do gợi ý AI; chọn các lượt tên rồi Xác nhận, Bác bỏ kèm lý do, hoặc Chuyển cho người khác.",
        href: "/doi-soat/tac-gia/",
        linkLabel: "Mở Hàng đợi tác giả",
      },
      {
        title: "Quyết định nhóm nghi trùng",
        description: "Mở từng nhóm, so các cột và chú ý ô khác nhau. Với dấu hiệu đồ án nhóm, ưu tiên Giữ riêng; khi gộp, chọn bản sống sót và giá trị cho từng trường trước khi xác nhận thao tác không thể hoàn tác.",
        href: "/doi-soat/trung-lap/",
        linkLabel: "Mở Hàng đợi nghi trùng",
      },
      {
        title: "Vận hành kỳ báo cáo",
        description: "Mở kỳ với phạm vi và hạn nộp, theo dõi tiến độ từng đơn vị, sau đó Đóng nộp. Chỉ Chốt kỳ khi đã kiểm tra các hồ sơ Đạt yêu cầu và danh sách hồ sơ sẽ bị bỏ qua.",
        href: "/ky-bao-cao/",
        linkLabel: "Mở Kỳ báo cáo",
      },
      {
        title: "Chỉnh tay nhưng giữ xuất xứ",
        description: "Từ kết quả tra cứu, mở chi tiết công trình và dùng nút bút chì ở trường được phép sửa. Nhập lý do bắt buộc; sau khi lưu, giá trị gốc vẫn còn và cột Nguồn ghi người sửa cùng thời điểm.",
        href: "/tra-cuu/",
        linkLabel: "Tìm công trình cần chỉnh",
      },
      {
        title: "Kiểm tra nhật ký",
        description: "Lọc theo loại thực thể, mã bản ghi hoặc người thao tác để xem lại quyết định, trạng thái trước–sau và thời điểm thực hiện.",
        href: "/nhat-ky/",
        linkLabel: "Mở Nhật ký",
      },
    ],
    images: [
      { src: "/huong-dan/tra-cuu.png", alt: "Màn hình tra cứu công trình với bộ lọc và bảng kết quả", caption: "Tra cứu, lọc và tải CSV từ cùng một tập kết quả.", width: 1440, height: 900 },
      { src: "/huong-dan/cong-trinh.png", alt: "Chi tiết công trình với bảng xuất xứ dữ liệu và danh sách tác giả", caption: "Chi tiết công trình giữ song song giá trị đang dùng, giá trị gốc và nguồn.", width: 1440, height: 900 },
      { src: "/huong-dan/hang-doi-tac-gia.png", alt: "Hàng đợi tác giả với ứng viên và gợi ý AI", caption: "Gợi ý AI nằm cạnh dữ liệu cần kiểm tra; người dùng vẫn chọn quyết định.", width: 1440, height: 900 },
      { src: "/huong-dan/nghi-trung.png", alt: "Chi tiết nhóm nghi trùng so sánh các bản ghi cạnh nhau", caption: "Các bản ghi nghi trùng được đặt cạnh nhau trước khi gộp hoặc giữ riêng.", width: 1440, height: 900 },
    ],
  },
  {
    id: "khoa",
    title: "Khoa",
    summary: "Kê khai trong phạm vi đơn vị và duyệt nội bộ trước khi chuyển hồ sơ cho Phòng KH-CN.",
    userRoles: ["faculty_officer", "faculty_head"],
    icon: School,
    steps: [
      {
        title: "Kê khai công trình cho đơn vị",
        description: "Chuyên viên khoa mở kỳ đang nhận hồ sơ, vào tab Hồ sơ kê khai, chọn công trình và đúng đơn vị của mình; thêm ghi chú hoặc minh chứng cần thiết.",
        href: "/ky-bao-cao/",
        linkLabel: "Mở Kỳ báo cáo",
      },
      {
        title: "Trình khoa duyệt",
        description: "Mở hồ sơ Nháp, kiểm tra công trình, minh chứng và dòng thời gian rồi bấm Trình khoa duyệt. Nội dung cần sửa phải hoàn tất trước bước này.",
        href: "/ky-bao-cao/",
        linkLabel: "Tìm hồ sơ kê khai",
      },
      {
        title: "Trưởng khoa duyệt hoặc trả về",
        description: "Trưởng khoa mở hồ sơ Chờ khoa duyệt và chọn Phê duyệt nếu đủ thông tin; nếu chưa đạt, chọn Trả về và ghi lý do bắt buộc để người lập sửa lại.",
        href: "/ky-bao-cao/",
        linkLabel: "Mở danh sách hồ sơ",
      },
      {
        title: "Gửi Phòng KH-CN",
        description: "Với hồ sơ Khoa đã duyệt, dùng hành động Gửi phòng kiểm tra. Từ đây Phòng KH-CN tiếp nhận; mọi sửa đổi trọng yếu sẽ đưa hồ sơ về Nháp và huỷ dấu đã duyệt cũ.",
        href: "/ky-bao-cao/",
        linkLabel: "Theo dõi tiến độ hồ sơ",
      },
    ],
    images: [],
  },
  {
    id: "giang-vien",
    title: "Giảng viên",
    summary: "Theo dõi hồ sơ công bố của mình, tự kê khai và rà soát đề tài trước khi đi tiếp.",
    userRoles: ["lecturer"],
    icon: GraduationCap,
    steps: [
      {
        title: "Xem hồ sơ công bố",
        description: "Tra cứu một công trình của mình, mở tên giảng viên đã liên kết để xem thống kê theo loại, theo năm, danh sách công trình và số liên kết đang chờ.",
        href: "/tra-cuu/",
        linkLabel: "Tra cứu hồ sơ công bố",
      },
      {
        title: "Kê khai của tôi",
        description: "Chọn công trình đã liên kết với hồ sơ cá nhân, thêm vào kỳ đang mở và Trình khoa duyệt. Theo dõi trạng thái hoặc lý do trả về ngay trong danh sách của mình.",
        href: "/ke-khai-cua-toi/",
        linkLabel: "Mở Kê khai của tôi",
      },
      {
        title: "Đối chiếu đề tài",
        description: "Nhập tiêu đề, mô tả và tối đa bốn khía cạnh: bài toán, đối tượng, phạm vi, phương pháp. Đọc giải thích theo từng khía cạnh và nhớ kết quả chỉ dựa trên tóm tắt, không phải toàn văn.",
        href: "/doi-chieu/",
        linkLabel: "Mở Đối chiếu đề tài",
      },
      {
        title: "Rà soát theo khoá",
        description: "Chọn khoá và mức cần xem, kiểm tra các đề tài được gắn cờ cùng những đề tài khoá trước ở gần nhất; dùng Đối chiếu chi tiết khi cần xem đủ bốn khía cạnh.",
        href: "/doi-chieu/ra-soat/",
        linkLabel: "Mở Rà soát theo khoá",
      },
    ],
    images: [
      { src: "/huong-dan/giang-vien.png", alt: "Hồ sơ giảng viên với thống kê và danh sách công trình", caption: "Hồ sơ công bố gom các công trình đã liên kết với một giảng viên.", width: 1440, height: 900 },
      { src: "/huong-dan/doi-chieu.png", alt: "Màn hình đối chiếu đề tài theo bốn khía cạnh", caption: "Đối chiếu giải thích riêng bài toán, đối tượng, phạm vi và phương pháp.", width: 1440, height: 900 },
      { src: "/huong-dan/ra-soat.png", alt: "Màn hình rà soát đề tài đồ án theo khoá", caption: "Rà soát theo khoá giúp tìm các trường hợp cần giảng viên xem lại.", width: 1440, height: 900 },
    ],
  },
  {
    id: "lanh-dao",
    title: "Lãnh đạo",
    summary: "Đọc số liệu tổng hợp và đi từ chỉ số về dữ liệu đứng sau, không cần xử lý hàng đợi.",
    userRoles: ["school_leader"],
    icon: Landmark,
    steps: [
      {
        title: "Xem tổng quan",
        description: "Đọc các chỉ số chính, biểu đồ theo năm và loại, thống kê theo đơn vị cùng nhóm giảng viên nổi bật. Bấm vào hàng đợi hoặc tên giảng viên để truy ngược số liệu.",
        href: "/tong-quan/",
        linkLabel: "Mở Tổng quan",
      },
      {
        title: "Khám phá chủ đề",
        description: "Mở một cụm chủ đề để xem từ khoá đại diện và các công trình thành viên, sau đó dùng Tra cứu theo chủ đề này để đi tới danh sách nguồn.",
        href: "/chu-de/",
        linkLabel: "Mở Chủ đề",
      },
      {
        title: "Theo dõi chất lượng dữ liệu",
        description: "Xem độ phủ liên kết và các cảnh báo theo loại tài liệu. Khi chỉ số có nút Mở hàng đợi, dùng liên kết đó để xem các bản ghi tạo nên con số.",
        href: "/chat-luong-du-lieu/",
        linkLabel: "Mở Chất lượng dữ liệu",
      },
    ],
    images: [
      { src: "/huong-dan/tong-quan.png", alt: "Màn hình tổng quan với các chỉ số và biểu đồ công trình", caption: "Tổng quan trên màn hình máy tính.", width: 1440, height: 900 },
      { src: "/huong-dan/mobile-tong-quan.png", alt: "Màn hình tổng quan trên điện thoại", caption: "Các chỉ số tổng quan vẫn đọc được trên thiết bị di động.", width: 390, height: 844 },
    ],
  },
];

const declarationStates = [
  ["Nhap", "Đang soạn và còn có thể bổ sung nội dung, minh chứng."],
  ["ChoBoSung", "Đang chờ người cung cấp hoàn thiện thông tin được yêu cầu."],
  ["ChoKhoaDuyet", "Đã trình và đang chờ trưởng khoa xem xét."],
  ["KhoaDaDuyet", "Khoa đã phê duyệt và đóng băng phiên bản được duyệt."],
  ["ChoPhongKiemTra", "Đã gửi Phòng KH-CN để kiểm tra cấp trường."],
  ["DatYeuCau", "Phòng KH-CN đã chấp nhận, hồ sơ chờ kỳ được chốt."],
  ["DaChot", "Đã nằm trong dữ liệu chốt của kỳ báo cáo."],
  ["Rut", "Đơn vị hoặc người kê khai đã rút hồ sơ khỏi luồng."],
] as const;

const glossary = [
  ["Xuất xứ", "Dấu vết cho biết một giá trị đến từ bản ghi nguồn nào hoặc do ai chỉnh tay, vào lúc nào. Giá trị gốc không bị ghi đè khi dữ liệu đang dùng thay đổi."],
  ["Lượt tên", "Một lần tên tác giả hoặc người hướng dẫn xuất hiện trên một công trình nguồn. Cùng một người có thể có nhiều lượt tên với cách viết khác nhau."],
  ["Liên kết tác giả", "Mối nối giữa một lượt tên và đúng hồ sơ giảng viên. Liên kết có trạng thái để phân biệt kết quả tự động, đang chờ người xác nhận, đã xác nhận hoặc đã bác bỏ."],
  ["Nghi trùng", "Nhóm từ hai bản ghi trở lên có dấu hiệu mô tả cùng một công trình. Người có thẩm quyền phải so sánh rồi chọn gộp, giữ riêng hoặc bỏ qua."],
  ["Khía cạnh", "Một góc so sánh đề tài: bài toán, đối tượng, phạm vi hoặc phương pháp. Mỗi khía cạnh được giải thích riêng thay vì gộp thành một phần trăm tổng hợp."],
  ["Kỳ báo cáo", "Khoảng thời gian Phòng KH-CN mở để các đơn vị kê khai, duyệt và nộp công trình. Khi kỳ đã chốt, dữ liệu báo cáo không được sửa ngầm."],
  ["Chế độ mở", "Khi chưa có tài khoản nào được đặt mật khẩu, hệ thống cho phép dùng các chức năng theo cấu hình vận hành ban đầu. Ngay khi bật đăng nhập, quyền thao tác được kiểm tra theo tài khoản và vai trò."],
] as const;

const faqs = [
  ["Dữ liệu cá nhân của giảng viên được xử lý thế nào?", "Kho mã nguồn chỉ dùng dữ liệu kiểm thử đã ẩn danh; dữ liệu cá nhân thật không được đưa vào Git. Phần AI chỉ nhận tiêu đề, tóm tắt, từ khoá và mô tả đề tài, không nhận các trường cá nhân."],
  ["Không có toàn văn thì AI so sánh gì?", "AI so trên tiêu đề, tóm tắt và từ khoá. Kết quả là gợi ý để người dùng xem lại, không phải kết luận đạo văn hay dẫn chứng theo trang."],
  ["Tỷ lệ liên kết tác giả 86,6% có nghĩa là đã đúng hết chưa?", "Chưa. Đây là tỷ lệ bài báo có ít nhất một liên kết tự động hoặc ứng viên đã vào hàng đợi; các ca chưa chắc chắn vẫn phải được người dùng xác nhận hoặc bác bỏ."],
  ["Ngưỡng rà soát Cao/Vừa có phải số tuỳ ý không?", "Không. Ngưỡng 0,90/0,80 được hiệu chuẩn trên phân bố điểm thật của 529 đồ án khoá 21 và kiểm tra thủ công các cặp quanh ngưỡng. Khi đổi mô hình hoặc tập dữ liệu, ngưỡng có thể cần đo lại."],
  ["AI có tự gộp, tự nối hoặc tự xoá dữ liệu không?", "Không. AI chỉ tạo gợi ý; các thao tác gộp, nối, sửa hay bác bỏ đều cần người có quyền chủ động thực hiện. Đây là nguyên tắc BR-18: AI gợi ý, người quyết."],
  ["Ai được sửa dữ liệu và có truy ngược được sau khi sửa không?", "Chỉ Phòng KH-CN được chỉnh tay chín trường mô tả và phải ghi lý do; không được sửa tác giả, đơn vị hay minh chứng. Hệ thống giữ giá trị gốc, ghi người sửa, thời điểm và sự kiện trong nhật ký."],
] as const;

export default function UserGuidePage() {
  const me = useMe();
  const currentRoles = new Set(me.data?.user?.roles ?? []);
  const isCurrentRole = (guide: RoleGuide) => guide.userRoles.some((role) => currentRoles.has(role));

  return (
    <>
      <PageHeader title="Hướng dẫn sử dụng" description="Đi theo vai trò của anh/chị hoặc đọc từ đầu để hiểu cách dữ liệu đi từ nguồn tới quyết định." />

      <section aria-labelledby="guide-purpose-title" className="mb-8 border-b pb-8">
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.14em] text-primary">Bắt đầu từ dữ liệu thật</p>
        <h2 id="guide-purpose-title" className="text-xl font-semibold">Hệ thống này làm gì</h2>
        <div className="mt-3 max-w-4xl space-y-2 text-[15px] leading-7 text-muted-foreground">
          <p>ICTU-CRIS hợp nhất <strong className="font-semibold text-foreground tabular-nums">7.618 công trình</strong> và <strong className="font-semibold text-foreground tabular-nums">410 giảng viên</strong> thành một nguồn sự thật có thể truy ngược về bản ghi gốc.</p>
          <p>Chuẩn hoá tên và đưa trường hợp chưa chắc chắn cho người dùng quyết định giúp độ phủ liên kết tác giả tăng từ <strong className="font-semibold text-foreground tabular-nums">8%</strong> lên <strong className="font-semibold text-foreground tabular-nums">86%</strong>.</p>
          <p>Dữ liệu nguồn vẫn có giới hạn lớn: <strong className="font-semibold text-foreground tabular-nums">4.621/5.375 đồ án</strong> ghi người hướng dẫn là <code className="rounded bg-muted px-1.5 py-0.5 text-sm text-foreground">ICTU_TEACHER</code>, nên hệ thống luôn trình bày rõ điều đã biết và điều cần con người kiểm tra.</p>
        </div>
      </section>

      <div className="grid items-start gap-8 lg:grid-cols-[220px_minmax(0,1fr)]">
        <aside className="guide-toc hidden lg:sticky lg:top-20 lg:block" aria-label="Mục lục hướng dẫn">
          <p className="mb-3 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">Theo vai trò</p>
          <nav className="space-y-1 border-l pl-3">
            {roleGuides.map((guide) => {
              const current = isCurrentRole(guide);
              return <Link key={guide.id} href={`#${guide.id}`} className={cn("flex items-center justify-between gap-2 rounded-md px-2 py-2 text-sm hover:bg-muted hover:text-foreground", current ? "bg-primary/10 font-semibold text-primary" : "text-muted-foreground")}><span>{guide.title}</span>{current && <Badge variant="outline" className="border-primary/30 text-primary">Vai trò của bạn</Badge>}</Link>;
            })}
          </nav>
          <p className="mt-6 mb-3 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">Tra cứu nhanh</p>
          <nav className="space-y-1 border-l pl-3">
            <Link href="#ai" className="block rounded-md px-2 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground">AI trong hệ thống</Link>
            <Link href="#thuat-ngu" className="block rounded-md px-2 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground">Thuật ngữ</Link>
            <Link href="#cau-hoi" className="block rounded-md px-2 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground">Câu hỏi thường gặp</Link>
          </nav>
        </aside>

        <div className="min-w-0">
          <div className="mb-6 rounded-lg border bg-card px-4 py-3 text-sm text-muted-foreground" role="status">
            {me.isLoading ? "Đang xác định vai trò để đánh dấu phần hướng dẫn phù hợp…" : me.isError ? `Không thể xác định vai trò. Hướng dẫn đầy đủ vẫn dùng được. ${me.error instanceof ApiError ? me.error.detail : ""}` : currentRoles.size ? "Phần phù hợp với vai trò đang đăng nhập đã được đánh dấu trong mục lục." : "Chưa đăng nhập; anh/chị có thể đọc hướng dẫn của mọi vai trò."}
          </div>

          {roleGuides.map((guide) => {
            const Icon = guide.icon;
            const current = isCurrentRole(guide);
            return (
              <section key={guide.id} id={guide.id} aria-labelledby={`${guide.id}-title`} className="scroll-mt-20 border-b py-9 first:pt-0">
                <div className="flex items-start gap-3">
                  <span className="grid size-10 shrink-0 place-items-center rounded-lg bg-primary/10 text-primary"><Icon className="size-5" /></span>
                  <div>
                    <div className="flex flex-wrap items-center gap-2"><h2 id={`${guide.id}-title`} className="text-xl font-semibold">{guide.title}</h2>{current && <Badge><CheckCircle2 />Vai trò của bạn</Badge>}</div>
                    <p className="mt-1 max-w-3xl text-sm leading-6 text-muted-foreground">{guide.summary}</p>
                  </div>
                </div>

                <ol className="mt-6 space-y-5">
                  {guide.steps.map((step, index) => (
                    <li key={step.title} className="grid grid-cols-[28px_minmax(0,1fr)] gap-3">
                      <span aria-hidden className="grid size-7 place-items-center rounded-full border bg-background text-xs font-semibold tabular-nums">{index + 1}</span>
                      <div>
                        <h3 className="font-semibold">{step.title}</h3>
                        <p className="mt-1 max-w-4xl leading-6 text-muted-foreground">{step.description}</p>
                        <Link href={step.href} className="mt-1.5 inline-flex items-center gap-1 font-medium text-primary underline-offset-4 hover:underline">{step.linkLabel}<ExternalLink className="size-3.5" /></Link>
                      </div>
                    </li>
                  ))}
                </ol>

                {guide.images.length > 0 && <div className={cn("mt-7 grid gap-5", guide.images.length > 1 && "xl:grid-cols-2")}>{guide.images.map((guideImage) => <figure key={guideImage.src} className="overflow-hidden rounded-lg border bg-card"><img src={guideImage.src} alt={guideImage.alt} width={guideImage.width} height={guideImage.height} loading="lazy" className={cn("h-auto w-full", guideImage.height > guideImage.width && "mx-auto max-h-[560px] w-auto")} /><figcaption className="border-t px-3 py-2 text-xs text-muted-foreground">{guideImage.caption}</figcaption></figure>)}</div>}
              </section>
            );
          })}

          <section id="ai" aria-labelledby="ai-title" className="scroll-mt-20 border-b py-9">
            <div className="flex items-center gap-3"><span className="grid size-10 place-items-center rounded-lg bg-primary/10 text-primary"><Bot className="size-5" /></span><div><h2 id="ai-title" className="text-xl font-semibold">AI làm gì — và không làm gì</h2><p className="mt-1 text-sm text-muted-foreground">AI tạo tín hiệu để người dùng kiểm tra nhanh hơn; quyền quyết định không chuyển cho máy.</p></div></div>
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              <div><h3 className="flex items-center gap-2 font-semibold"><CheckCircle2 className="size-4 text-primary" />AI hỗ trợ</h3><ul className="mt-3 space-y-2 text-muted-foreground"><li>Gợi ý ứng viên cho liên kết tác giả.</li><li>Ước lượng tương đồng trong nhóm nghi trùng.</li><li>Đối chiếu đề tài theo bốn khía cạnh.</li><li>Rà soát đề tài có dấu hiệu gần nhau theo khoá.</li><li>Gom công trình thành các cụm chủ đề.</li></ul></div>
              <div><h3 className="flex items-center gap-2 font-semibold"><CircleAlert className="size-4 text-primary" />Giới hạn bắt buộc</h3><ul className="mt-3 space-y-2 text-muted-foreground"><li>Không tự gộp, tự nối, tự sửa hoặc tự xoá dữ liệu (BR-18).</li><li>So trên tiêu đề, tóm tắt và từ khoá — không phải toàn văn.</li><li>Kết quả không phải kết luận đạo văn hay quyết định duyệt đề tài.</li><li>Mô hình chạy cục bộ; dữ liệu không được gửi ra dịch vụ AI bên ngoài.</li></ul></div>
            </div>
          </section>

          <section id="thuat-ngu" aria-labelledby="glossary-title" className="scroll-mt-20 border-b py-9">
            <h2 id="glossary-title" className="text-xl font-semibold">Thuật ngữ</h2>
            <dl className="mt-5 divide-y border-y">{glossary.map(([term, definition]) => <div key={term} className="grid gap-1 py-4 sm:grid-cols-[180px_minmax(0,1fr)] sm:gap-5"><dt className="font-semibold">{term}</dt><dd className="leading-6 text-muted-foreground">{definition}</dd></div>)}</dl>
            <div className="mt-6">
              <h3 className="font-semibold">Hồ sơ kê khai và 8 trạng thái</h3>
              <p className="mt-1 max-w-4xl leading-6 text-muted-foreground">Hồ sơ kê khai gắn một công trình với một đơn vị trong một kỳ báo cáo, kèm minh chứng và toàn bộ lịch sử duyệt. Luồng thông thường đi từ Nháp tới Đã chốt; Chờ bổ sung và Đã rút là các nhánh xử lý riêng.</p>
              <dl className="mt-4 grid gap-x-6 gap-y-3 sm:grid-cols-2">{declarationStates.map(([state, description], index) => <div key={state} className="grid grid-cols-[24px_minmax(0,1fr)] gap-2"><span aria-hidden className="pt-0.5 text-xs text-muted-foreground tabular-nums">{index + 1}.</span><div><dt className="font-medium">{stateLabels[state]}</dt><dd className="mt-0.5 text-sm leading-5 text-muted-foreground">{description}</dd></div></div>)}</dl>
            </div>
          </section>

          <section id="cau-hoi" aria-labelledby="faq-title" className="scroll-mt-20 py-9">
            <h2 id="faq-title" className="text-xl font-semibold">Câu hỏi thường gặp</h2>
            <div className="mt-5 divide-y border-y">{faqs.map(([question, answer]) => <details key={question} className="group py-4"><summary className="cursor-pointer list-none pr-8 font-semibold marker:content-none">{question}<span aria-hidden className="float-right text-muted-foreground transition-transform group-open:rotate-45">+</span></summary><p className="mt-3 max-w-4xl leading-6 text-muted-foreground">{answer}</p></details>)}</div>
          </section>

          <div className="flex items-start gap-3 rounded-lg border bg-muted/40 p-4 text-sm"><LockKeyhole className="mt-0.5 size-4 shrink-0 text-primary" /><p><strong>Nguyên tắc xuyên suốt:</strong> người lập không tự duyệt, người duyệt không sửa nội dung, và mọi quyết định quan trọng đều để lại xuất xứ hoặc nhật ký có thể kiểm tra lại.</p></div>
        </div>
      </div>
    </>
  );
}
