# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Nhà cung cấp vector ngữ nghĩa, chọn bằng biến môi trường.

    CRIS_AI_PROVIDER = none  (mặc định) | fake | local
    CRIS_AI_MODEL_DIR = thư mục chứa mô hình cục bộ (chỉ cho local)

`none` là trạng thái an toàn: mọi chức năng khác vẫn chạy, chỗ gợi ý hiện
"AI chưa bật". `fake` là một provider thật dùng cho kiểm thử — vector xác định
từ túi từ, không cần thư viện ngoài. `local` chạy mô hình ONNX trên CPU và
chỉ được import khi được chọn, nên gói lõi không kéo theo thư viện AI.
"""
import hashlib
import math
import os
import re
import unicodedata
from typing import Protocol


class AIDisabled(RuntimeError):
    """Provider là `none`: chức năng cần vector không có sẵn, hãy dùng đường lui."""


class AIUnavailable(RuntimeError):
    """Provider được chọn nhưng thiếu thư viện hoặc mô hình."""


class Provider(Protocol):
    name: str
    model_id: str
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...

    def explain(self, prompt: str) -> str | None: ...


class NoneProvider:
    name = "none"
    model_id = "none"
    dim = 0

    def embed(self, texts):
        raise AIDisabled("AI chưa bật: đặt CRIS_AI_PROVIDER=local (hoặc fake để kiểm thử)")

    def explain(self, prompt):
        return None


_WORD = re.compile(r"[^\W_]+", re.UNICODE)


def _tokens(text):
    text = unicodedata.normalize("NFC", (text or "").lower())
    return _WORD.findall(text)


class FakeProvider:
    """Vector xác định từ túi từ: cùng văn bản → cùng vector; chia sẻ nhiều từ → gần nhau.

    Mỗi từ ánh xạ sang một vector giả ngẫu nhiên cố định (từ SHA-256 của từ);
    vector văn bản là tổng các vector từ, chuẩn hoá về độ dài 1. Đủ để kiểm thử
    đối chiếu, gom cụm và xếp hạng mà không tải mô hình.
    """
    name = "fake"

    def __init__(self, dim=32):
        self.dim = dim
        self.model_id = f"fake-{dim}"

    def _word_vec(self, word):
        h = hashlib.sha256(word.encode("utf-8")).digest()
        # mở rộng băm cho đủ dim byte, mỗi byte → [-1, 1]
        buf = h
        while len(buf) < self.dim:
            buf += hashlib.sha256(buf).digest()
        return [(b / 127.5) - 1.0 for b in buf[: self.dim]]

    def embed(self, texts):
        out = []
        for t in texts:
            acc = [0.0] * self.dim
            for w in _tokens(t):
                for i, x in enumerate(self._word_vec(w)):
                    acc[i] += x
            norm = math.sqrt(sum(x * x for x in acc)) or 1.0
            out.append([x / norm for x in acc])
        return out

    def explain(self, prompt):
        return None


VALID = ("none", "fake", "local")

# Cache theo tiến trình, khoá bởi (tên provider, thư mục mô hình). Nạp phiên ONNX
# mất ~1,8 s; web tạo provider mỗi request nên không cache thì mỗi lần đối chiếu
# đội thêm chừng đó (đo 10/09: 5,9 s so với 3,4 s ở tầng nghiệp vụ, vượt NFR-41).
_CACHE: dict = {}


def _build(name, model_dir):
    if name == "none":
        return NoneProvider()
    if name == "fake":
        return FakeProvider()
    if name == "local":
        from cris.ai.local import LocalProvider  # import muộn: gói lõi không cần onnxruntime
        return LocalProvider(model_dir=model_dir)
    raise ValueError(f"CRIS_AI_PROVIDER={name!r} không hợp lệ; chọn một trong {', '.join(VALID)}")


def get_provider(env=None):
    env = os.environ if env is None else env
    name = (env.get("CRIS_AI_PROVIDER") or "none").strip().lower()
    key = (name, env.get("CRIS_AI_MODEL_DIR") or "")
    p = _CACHE.get(key)
    if p is None:
        p = _build(name, key[1] or None)
        _CACHE[key] = p
    return p


def clear_provider_cache():
    """Cho kiểm thử và cho lệnh đổi cấu hình lúc chạy."""
    _CACHE.clear()
