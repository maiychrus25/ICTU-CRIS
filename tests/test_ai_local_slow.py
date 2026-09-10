# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Kiểm mô hình cục bộ thật. Chậm và cần tệp mô hình, nên đánh dấu `slow`;
CI chạy `-m "not slow"`. Tự bỏ qua khi thiếu thư viện [ai] hoặc thiếu mô hình
(không tải trong test — chạy `python -m cris ai download` trước)."""
import os
import time
import pytest

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def local():
    pytest.importorskip("onnxruntime")
    pytest.importorskip("tokenizers")
    pytest.importorskip("numpy")
    from cris.ai import local as L
    from cris.ai.provider import AIUnavailable
    try:
        return L.LocalProvider(model_dir=os.environ.get("CRIS_AI_MODEL_DIR"), download=False)
    except AIUnavailable as e:
        pytest.skip(str(e))


def _cos(a, b):
    return sum(x * y for x, y in zip(a, b))


def test_local_provider_shape(local):
    v = local.embed(["Xây dựng website bán hàng"])[0]
    assert local.dim == 384 and len(v) == 384
    assert abs(_cos(v, v) - 1.0) < 1e-4


def test_vietnamese_same_topic_is_closer_than_different_topic(local):
    q, same, cross, far = local.embed([
        "Xây dựng ứng dụng học tiếng Anh cho trẻ em có tích hợp AI hỗ trợ luyện phát âm",
        "Ứng dụng Android học từ vựng tiếng Anh ngành công nghệ thông tin",
        "A pronunciation practice system for children based on pre-trained deep learning models",
        "Thiết kế hệ thống đèn chiếu sáng thông minh ứng dụng IoT",
    ])
    assert _cos(q, same) > _cos(q, far)
    assert _cos(q, cross) > _cos(q, far)          # xuyên ngôn ngữ Việt–Anh


def test_throughput_64_passages_under_30_seconds(local):
    batch = [("Nghiên cứu này xây dựng hệ thống " + "quản lý dữ liệu " * 40) for _ in range(64)]
    t = time.time()
    out = local.embed(batch)
    assert len(out) == 64
    assert time.time() - t < 30
