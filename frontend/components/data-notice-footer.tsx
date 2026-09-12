// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

export function DataNoticeFooter({ className = "" }: { className?: string }) {
  return (
    <footer className={`data-notice-footer fixed right-0 bottom-0 left-0 z-10 flex h-[var(--data-footer-h)] items-center justify-center overflow-hidden border-t bg-background/95 px-4 py-1 text-center text-xs leading-4 text-muted-foreground backdrop-blur ${className}`}>
      <span className="line-clamp-2 sm:block sm:truncate">
        Dữ liệu được lấy từ <a href="https://repository.ictu.edu.vn/" target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:text-foreground">DSpace</a> của Trường CNTT&amp;TT – ĐH Thái Nguyên (<a href="https://repository.ictu.edu.vn/" target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:text-foreground">repository.ictu.edu.vn</a>), chỉ nhằm mục đích học tập. Phần mềm mã nguồn mở Apache-2.0 — <a href="https://github.com/maiychrus25/ICTU-CRIS" target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:text-foreground">ICTU-CRIS</a>.
      </span>
    </footer>
  );
}
