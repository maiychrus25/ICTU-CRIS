# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""CSS nhúng dùng chung cho toàn bộ giao diện web (không tệp rời).

Yêu cầu tối thiểu (UX-10): đọc được trên màn hình hẹp, bảng cuộn ngang
trong khung riêng, vùng bấm tối thiểu 44px, trạng thái focus thấy rõ.
"""

CSS = """
:root {
  color-scheme: light;
  --fg: #1a1a1a;
  --bg: #ffffff;
  --muted: #666666;
  --border: #d0d0d0;
  --accent: #0b5fff;
  --danger: #b3261e;
  --warn: #9a6700;
  --ok: #1a7f37;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  color: var(--fg);
  background: var(--bg);
  line-height: 1.5;
}
.site-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: .75rem;
  padding: .75rem 1rem;
  border-bottom: 1px solid var(--border);
}
.site-header .brand { font-size: 1.05rem; }
.site-header nav { display: flex; flex-wrap: wrap; gap: .25rem; }
.site-header nav a {
  padding: .55rem .75rem;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  color: var(--fg);
  border-radius: 6px;
}
.site-header nav a:hover { background: #f0f0f0; }
.site-header nav a.active { background: var(--accent); color: #fff; }
main { padding: 1rem; max-width: 1100px; margin: 0 auto; }
h1 { font-size: 1.3rem; margin: 0 0 .75rem; }
a { color: var(--accent); }
button, input[type=submit], .btn {
  min-height: 44px;
  padding: .5rem 1rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: #f5f5f5;
  color: var(--fg);
  font-size: 1rem;
  cursor: pointer;
}
input, select, textarea {
  min-height: 44px;
  padding: .4rem .6rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
}
label { display: inline-block; margin: .35rem 0; }
:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
.table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 6px; margin: .75rem 0; }
table { border-collapse: collapse; width: 100%; min-width: 480px; }
th, td { padding: .55rem .65rem; text-align: left; border-bottom: 1px solid var(--border); white-space: nowrap; }
thead th { background: #f7f7f7; }
td.empty { color: var(--muted); white-space: normal; }
.badge { display: inline-block; padding: .15rem .55rem; border-radius: 999px; font-size: .8rem; border: 1px solid var(--border); white-space: nowrap; }
.badge-ok { background: #e6f4ea; color: var(--ok); border-color: #b7dfc2; }
.badge-warn { background: #fff4e5; color: var(--warn); border-color: #f1d9a8; }
.badge-danger { background: #fbeaea; color: var(--danger); border-color: #f0c2bf; }
.badge-default { background: #eef1f4; color: var(--fg); }
.pager { display: flex; align-items: center; gap: .75rem; margin: 1rem 0; flex-wrap: wrap; }
.pager-link { padding: .5rem .75rem; min-height: 44px; display: inline-flex; align-items: center; border: 1px solid var(--border); border-radius: 6px; text-decoration: none; color: var(--fg); }
.pager-link.disabled { color: var(--muted); border-color: transparent; pointer-events: none; }
.pager-status { color: var(--muted); }
.error-page { color: var(--danger); }
@media (max-width: 640px) {
  main { padding: .6rem; }
  .site-header { padding: .6rem; }
  th, td { padding: .45rem .5rem; }
}
"""
