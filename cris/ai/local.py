# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Provider cục bộ: mô hình embedding đa ngữ chạy bằng onnxruntime trên CPU.

Mô hình: paraphrase-multilingual-MiniLM-L12-v2 (sentence-transformers, Apache-2.0),
bản ONNX lượng tử hoá 8-bit do Xenova xuất, 118 MB, 384 chiều, có tiếng Việt.
Đo 09/2026 trên CPU 4 nhân: 64 đoạn ~200 token trong 1,8 s → toàn kho 5.709
công trình khoảng 3 phút.

Thư viện (onnxruntime, tokenizers, numpy) được import bên trong lớp để gói lõi
không cần chúng; cài bằng `pip install -e ".[ai]"`.
"""
import hashlib
import os
import pathlib
import tempfile
import urllib.request

from cris.ai.provider import AIUnavailable

REPO = "Xenova/paraphrase-multilingual-MiniLM-L12-v2"
MODEL_ID = "paraphrase-multilingual-MiniLM-L12-v2-q8"
DIM = 384
# (tên tệp cục bộ) -> (đường dẫn trong repo, SHA-256). Đo ngày 10/09/2026.
FILES = {
    "tokenizer.json": ("tokenizer.json",
                       "b60b6b43406a48bf3638526314f3d232d97058bc93472ff2de930d43686fa441"),
    "model_quantized.onnx": ("onnx/model_quantized.onnx",
                             "66fc00f5f29afcaff34092e1bdd20008ca3918265a82fb9695a551e510cc4ebc"),
}


def default_model_dir():
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    return os.path.join(base, "ictu-cris", "models", "paraphrase-multilingual-MiniLM-L12-v2")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_model(model_dir=None, download=True, log=None):
    """Bảo đảm hai tệp mô hình có mặt và đúng băm; tải nếu thiếu và được phép.

    Trả về dict tên tệp -> đường dẫn. Tải vào tệp tạm rồi mới đổi tên, nên một
    lần tải dở không để lại tệp hỏng.
    """
    model_dir = pathlib.Path(model_dir or default_model_dir())
    model_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, (remote, sha) in FILES.items():
        dst = model_dir / name
        if dst.exists() and _sha256(dst) == sha:
            paths[name] = str(dst)
            continue
        if not download:
            raise AIUnavailable(f"thiếu tệp mô hình {dst}; chạy `python -m cris ai download`")
        url = f"https://huggingface.co/{REPO}/resolve/main/{remote}"
        if log:
            log(f"tải {url}")
        fd, tmp = tempfile.mkstemp(dir=model_dir, prefix=name + ".", suffix=".part")
        os.close(fd)
        try:
            urllib.request.urlretrieve(url, tmp)
            got = _sha256(tmp)
            if got != sha:
                raise AIUnavailable(f"băm không khớp cho {name}: mong {sha[:12]}…, nhận {got[:12]}…")
            os.replace(tmp, dst)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        paths[name] = str(dst)
    return paths


class LocalProvider:
    name = "local"
    model_id = MODEL_ID
    dim = DIM

    def __init__(self, model_dir=None, batch=32, max_tokens=256, download=True):
        try:
            import numpy  # noqa: F401
            import onnxruntime as ort
            from tokenizers import Tokenizer
        except ImportError as e:  # pragma: no cover - phụ thuộc môi trường
            raise AIUnavailable("thiếu thư viện AI; cài bằng: pip install -e '.[ai]'") from e
        paths = ensure_model(model_dir, download=download)
        self._np = numpy
        self._tok = Tokenizer.from_file(paths["tokenizer.json"])
        self._tok.enable_truncation(max_tokens)
        self._sess = ort.InferenceSession(paths["model_quantized.onnx"], providers=["CPUExecutionProvider"])
        self._inputs = {i.name for i in self._sess.get_inputs()}
        self.batch = batch

    def _run(self, texts):
        np = self._np
        enc = self._tok.encode_batch(texts)
        L = max(len(e.ids) for e in enc)
        ids = np.array([e.ids + [0] * (L - len(e.ids)) for e in enc], dtype=np.int64)
        att = np.array([e.attention_mask + [0] * (L - len(e.attention_mask)) for e in enc], dtype=np.int64)
        feed = {"input_ids": ids, "attention_mask": att}
        if "token_type_ids" in self._inputs:
            feed["token_type_ids"] = np.zeros_like(ids)
        hidden = self._sess.run(None, feed)[0]                       # (B, L, H)
        mask = att[..., None].astype(np.float32)
        pooled = (hidden * mask).sum(1) / np.maximum(mask.sum(1), 1e-9)   # mean pooling
        norm = np.linalg.norm(pooled, axis=1, keepdims=True)
        return pooled / np.maximum(norm, 1e-9)

    def embed(self, texts):
        out = []
        for i in range(0, len(texts), self.batch):
            out.extend(self._run(texts[i:i + self.batch]).tolist())
        return out

    def explain(self, prompt):
        return None
