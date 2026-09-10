# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Chạy trực tiếp máy chủ phát triển: `python -m cris.web [--host H] [--port P]`.

Đường dẫn chính thức là `python -m cris serve` (xem `cris/cli.py`); mô-đun này là
lối tắt tương đương, hữu ích khi chạy `cris.web` như một gói độc lập.
"""
import argparse

from cris.web.wsgi import serve


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cris.web")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args(argv)
    serve(a.host, a.port)


if __name__ == "__main__":
    main()
