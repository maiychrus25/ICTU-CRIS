// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

export function DataNoticeFooter({ className = "" }: { className?: string }) {
  return (
    <footer className={`data-notice-footer border-t px-4 py-4 text-center text-[11px] leading-5 text-muted-foreground ${className}`}>
      Dữ liệu được lấy từ <a href="https://repository.ictu.edu.vn/" target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:text-foreground">DSpace</a> của Trường CNTT&amp;TT – ĐH Thái Nguyên (<a href="https://repository.ictu.edu.vn/" target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:text-foreground">repository.ictu.edu.vn</a>), chỉ nhằm mục đích học tập. Phần mềm mã nguồn mở Apache-2.0 — <a href="https://github.com/maiychrus25/ICTU-CRIS" target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:text-foreground">ICTU-CRIS</a>.
    </footer>
  );
}
