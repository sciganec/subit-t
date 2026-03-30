"""Tests for two-phase encoder."""
import pytest
from subit_t import encode, Op


def test_encode_returns_result():
    r = encode("Review this code — I think there's a memory leak")
    assert r.current_state is not None
    assert r.target_state is not None
    assert isinstance(r.operator, Op)


def test_encode_review_gives_west_domain():
    r = encode("Review this code — there's a bug here")
    assert r.current_state.where == "WEST"


def test_encode_start_gives_spring_or_init():
    r = encode("Let's start building the authentication module from scratch")
    # Either current is SPRING or operator is INIT
    assert r.current_state.when == "SPRING" or r.operator == Op.INIT


def test_encode_collective_signal():
    r = encode("We need to coordinate the team on the API design")
    assert r.current_state.who == "WE" or r.operator == Op.MERGE


def test_encode_finish_gives_act():
    r = encode("Finish and commit all pending changes before the release")
    assert r.operator == Op.ACT or r.current_state.when == "AUTUMN"


def test_encode_no_idempotent_dominance():
    """Encoder should not produce idempotent transitions for most inputs."""
    test_cases = [
        "Review this code — I think there's a memory leak in the cleanup function.",
        "We need to coordinate the team on the API design before we proceed.",
        "Finish and commit all pending changes before the release.",
        "Analyze the system logs and identify what caused the outage.",
        "Run the deployment pipeline now — everything is ready.",
        "I'm currently auditing the security module for vulnerabilities.",
    ]
    idempotent_count = 0
    for text in test_cases:
        r = encode(text)
        tr = r.current_state.apply(r.operator)
        if tr.idempotent:
            idempotent_count += 1

    # Majority should NOT be idempotent
    assert idempotent_count <= len(test_cases) // 2, (
        f"{idempotent_count}/{len(test_cases)} transitions are idempotent — encoder needs tuning"
    )


def test_encode_distribution_sums_to_one():
    r = encode("Let's start a new project")
    for dist in [r.who_dist, r.where_dist, r.when_dist]:
        assert abs(sum(dist.values()) - 1.0) < 0.01


def test_encode_distribution_keys():
    r = encode("analyze this")
    assert set(r.who_dist.keys())   == {"ME", "WE", "YOU", "THEY"}
    assert set(r.where_dist.keys()) == {"EAST", "SOUTH", "WEST", "NORTH"}
    assert set(r.when_dist.keys())  == {"SPRING", "SUMMER", "AUTUMN", "WINTER"}


def test_encode_to_dict():
    r = encode("Run the deployment now")
    d = r.to_dict()
    assert "current_state" in d
    assert "target_state" in d
    assert "operator" in d
    assert "distributions" in d


def test_encode_op_confidence():
    r = encode("Review this code — I think there's a memory leak")
    assert 0.0 <= r.op_confidence <= 1.0
