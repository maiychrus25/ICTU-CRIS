# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import math
import sys
import pytest
from cris.ai import provider as P


def _cos(a, b):
    return sum(x * y for x, y in zip(a, b))


def test_default_provider_is_none():
    assert P.get_provider({}).name == "none"


def test_core_package_does_not_import_ai_libraries():
    """Gói lõi (web, CLI, provider none) không kéo onnxruntime/numpy vào tiến trình.

    Chạy trong tiến trình con: test khác trong cùng phiên (ví dụ test `slow`) có thể
    đã import các thư viện này, nên kiểm trong tiến trình hiện tại không có ý nghĩa.
    """
    import subprocess
    code = ("import sys; from cris.ai import provider, embed; provider.get_provider({}); "
            "import cris.web.wsgi, cris.cli; "
            "print(sorted(m for m in ('onnxruntime','numpy','tokenizers') if m in sys.modules))")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                         env={"CRIS_AI_PROVIDER": "none", "PATH": "/usr/bin:/bin"}, timeout=60)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "[]"


def test_unknown_provider_name_is_rejected_with_valid_choices():
    with pytest.raises(ValueError, match="none, fake, local"):
        P.get_provider({"CRIS_AI_PROVIDER": "gpt"})


def test_none_provider_embed_raises_ai_disabled():
    with pytest.raises(P.AIDisabled):
        P.NoneProvider().embed(["x"])
    assert P.NoneProvider().explain("x") is None


def test_fake_provider_is_deterministic_and_unit_length():
    p = P.FakeProvider()
    a, b = p.embed(["Xây dựng website bán hàng", "Xây dựng website bán hàng"])
    assert a == b
    assert math.isclose(math.sqrt(sum(x * x for x in a)), 1.0, abs_tol=1e-9)
    assert len(a) == p.dim == 32


def test_fake_provider_texts_sharing_words_are_closer():
    p = P.FakeProvider()
    q, near, far = p.embed([
        "ứng dụng học tiếng Anh cho trẻ em",
        "ứng dụng Android học từ vựng tiếng Anh",
        "thiết kế hệ thống đèn chiếu sáng IoT",
    ])
    assert _cos(q, near) > _cos(q, far)


def test_fake_provider_empty_text_gives_zero_vector_without_error():
    v = P.FakeProvider().embed([""])[0]
    assert all(x == 0.0 for x in v)


def test_get_provider_fake_via_env():
    p = P.get_provider({"CRIS_AI_PROVIDER": " FAKE "})
    assert p.name == "fake" and p.model_id == "fake-32"


def test_get_provider_is_cached_per_process_and_keyed_by_env():
    P.clear_provider_cache()
    a = P.get_provider({"CRIS_AI_PROVIDER": "fake"})
    b = P.get_provider({"CRIS_AI_PROVIDER": "fake"})
    assert a is b                                   # cùng cấu hình → cùng đối tượng, không nạp lại
    c = P.get_provider({"CRIS_AI_PROVIDER": "none"})
    assert c is not a and c.name == "none"          # cấu hình khác → đối tượng khác
    P.clear_provider_cache()
    assert P.get_provider({"CRIS_AI_PROVIDER": "fake"}) is not a
