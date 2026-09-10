# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import math
import sys
import pytest
from cris.ai import provider as P


def _cos(a, b):
    return sum(x * y for x, y in zip(a, b))


def test_default_provider_is_none_and_does_not_import_onnxruntime():
    p = P.get_provider({})
    assert p.name == "none"
    assert "onnxruntime" not in sys.modules


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
