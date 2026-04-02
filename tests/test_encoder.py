"""Tests for the v3 encoder."""

from unittest.mock import patch

from subit_t import Op, encode


def test_encode_returns_result():
    result = encode("Review this code - there is a memory leak")
    assert result.current_state is not None
    assert result.target_state is not None
    assert isinstance(result.operator, Op)


def test_encode_uses_what_not_where():
    result = encode("Review this code - there is a bug here")
    assert result.current_state.what == "REDUCE"


def test_encode_start_signal_moves_when_forward():
    result = encode("Let's start building the authentication module from scratch")
    assert result.operator == Op.WHEN_SHIFT


def test_encode_collective_signal_can_move_who_or_what():
    result = encode("We need to coordinate the team on the API design")
    assert result.operator in {Op.WHO_SHIFT, Op.WHAT_SHIFT, Op.WHEN_SHIFT}


def test_encode_rollback_signal_uses_inv():
    result = encode("Rollback after failure and recover the system")
    assert result.operator == Op.INV
    assert result.axis_diff == "ALL"


def test_encode_has_no_idempotent_dominance():
    texts = [
        "Review this code - I think there is a memory leak in the cleanup function.",
        "We need to coordinate the team on the API design before we proceed.",
        "Finish and commit all pending changes before the release.",
        "Analyze the system logs and identify what caused the outage.",
        "Run the deployment pipeline now - everything is ready.",
        "I'm currently auditing the security module for vulnerabilities.",
    ]
    for text in texts:
        result = encode(text)
        assert result.current_state.apply(result.operator).idempotent is False


def test_encode_distribution_sums_to_one():
    result = encode("Let's start a new project")
    for dist in [result.who_dist, result.what_dist, result.when_dist]:
        assert abs(sum(dist.values()) - 1.0) < 0.01


def test_encode_distribution_keys():
    result = encode("analyze this")
    assert set(result.who_dist.keys()) == {"ME", "WE", "YOU", "THEY"}
    assert set(result.what_dist.keys()) == {"EXPAND", "TRANSFORM", "REDUCE", "PRESERVE"}
    assert set(result.when_dist.keys()) == {"INITIATE", "SUSTAIN", "INTEGRATE", "RELEASE"}


def test_encode_to_dict_contains_what_and_where_alias():
    result = encode("Run the deployment now")
    as_dict = result.to_dict()
    assert "current_state" in as_dict
    assert "target_state" in as_dict
    assert "operator" in as_dict
    assert "distributions" in as_dict
    assert "what" in as_dict["distributions"]
    assert "where" in as_dict["distributions"]


def test_encode_model_assisted_hint_can_shift_result():
    hint = {
        "current_who": "THEY",
        "current_what": "EXPAND",
        "current_when": "SUSTAIN",
        "target_who": "THEY",
        "target_what": "EXPAND",
        "target_when": "SUSTAIN",
        "prefer_inv": True,
        "confidence": 0.9,
        "reason": "live factual lookup",
    }
    with patch("subit_t.encoder._model_suggestion", return_value=hint):
        result = encode("What is the current EUR/USD exchange rate today?", model_assisted=True)
    assert result.operator == Op.INV
    assert result.model_assisted is True
    assert result.model_reason == "live factual lookup"


def test_encode_model_assisted_falls_back_when_no_hint():
    with patch("subit_t.encoder._model_suggestion", return_value=None):
        result = encode("Review this code and find the bug", model_assisted=True)
    assert isinstance(result.operator, Op)
    assert result.model_assisted is False
