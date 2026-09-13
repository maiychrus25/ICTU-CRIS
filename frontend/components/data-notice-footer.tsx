// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

export function DataNoticeFooter({ className = "" }: { className?: string }) {
  return (
    <footer className={`data-notice-footer fixed right-0 bottom-0 left-0 z-10 flex h-[var(--data-footer-h)] items-center justify-center overflow-hidden border-t bg-background/95 px-4 py-1 text-center text-xs leading-4 text-muted-foreground backdrop-blur ${className}`}>
      <span className="line-clamp-2">
        Dữ liệu từ <a href="https://repository.ictu.edu.vn/" target="_blank" rel="noreferrer" className="text-foreground underline underline-offset-2">DSpace ICTU (repository.ictu.edu.vn)</a>, chỉ dùng cho học tập · <a href="https://github.com/maiychrus25/ICTU-CRIS" target="_blank" rel="noreferrer" className="text-foreground underline underline-offset-2">Apache-2.0</a>.
      </span>
    </footer>
  );
}
