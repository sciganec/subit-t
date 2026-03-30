"""Tests for State, Op, TransitionResult, apply()."""
import pytest
from subit_t import State, Op, validate_all_transitions
from subit_t.core import S_PRIME, S_SYNC, S_SCAN, S_CORE


def test_state_from_name():
    s = State.from_name("PRIME")
    assert s.who == "ME"
    assert s.where == "EAST"
    assert s.when == "SPRING"
    assert s.name == "PRIME"


def test_state_from_dims():
    s = State.from_dims("ME", "EAST", "SPRING")
    assert s.name == "PRIME"


def test_state_bits_range():
    for bits in range(64):
        s = State(bits)
        assert 0 <= s.bits <= 63


def test_state_invalid_bits():
    with pytest.raises(ValueError):
        State(64)
    with pytest.raises(ValueError):
        State(-1)


def test_state_unknown_name():
    with pytest.raises(KeyError):
        State.from_name("NONEXISTENT")


# ── Operator semantics ────────────────────────────────────────────────────────

def test_init_sets_spring():
    for bits in range(64):
        s = State(bits)
        tr = s.apply(Op.INIT)
        assert tr.result.when == "SPRING"


def test_expand_sets_south():
    for bits in range(64):
        s = State(bits)
        tr = s.apply(Op.EXPAND)
        assert tr.result.where == "SOUTH"


def test_merge_sets_we():
    for bits in range(64):
        s = State(bits)
        tr = s.apply(Op.MERGE)
        assert tr.result.who == "WE"


def test_act_sets_autumn():
    for bits in range(64):
        s = State(bits)
        tr = s.apply(Op.ACT)
        assert tr.result.when == "AUTUMN"


# ── Axis isolation ────────────────────────────────────────────────────────────

def test_init_does_not_change_who_where():
    for bits in range(64):
        s = State(bits)
        r = s.apply(Op.INIT).result
        assert r.who == s.who
        assert r.where == s.where


def test_expand_does_not_change_who_when():
    for bits in range(64):
        s = State(bits)
        r = s.apply(Op.EXPAND).result
        assert r.who == s.who
        assert r.when == s.when


def test_merge_does_not_change_where_when():
    for bits in range(64):
        s = State(bits)
        r = s.apply(Op.MERGE).result
        assert r.where == s.where
        assert r.when == s.when


def test_act_does_not_change_who_where():
    for bits in range(64):
        s = State(bits)
        r = s.apply(Op.ACT).result
        assert r.who == s.who
        assert r.where == s.where


# ── Idempotency ───────────────────────────────────────────────────────────────

def test_init_idempotent_on_spring():
    s = State.from_name("PRIME")  # WHEN=SPRING
    tr = s.apply(Op.INIT)
    assert tr.idempotent is True
    assert tr.result == s


def test_expand_idempotent_on_south():
    s = State.from_name("SYNC")   # WHERE=SOUTH
    tr = s.apply(Op.EXPAND)
    assert tr.idempotent is True


def test_merge_idempotent_on_we():
    s = State.from_name("COUNCIL")  # WHO=WE
    tr = s.apply(Op.MERGE)
    assert tr.idempotent is True


def test_act_idempotent_on_autumn():
    s = State.from_name("COMMIT")  # WHEN=AUTUMN
    tr = s.apply(Op.ACT)
    assert tr.idempotent is True


# ── Key transitions ───────────────────────────────────────────────────────────

def test_driver_merge_gives_sync():
    s = State.from_name("DRIVER")
    r = s.apply(Op.MERGE).result
    assert r.name == "SYNC"


def test_prime_act_gives_drafter():
    s = State.from_name("PRIME")
    r = s.apply(Op.ACT).result
    assert r.name == "DRAFTER"


def test_prime_merge_gives_spark():
    s = State.from_name("PRIME")
    r = s.apply(Op.MERGE).result
    assert r.name == "SPARK"


def test_core_init_gives_imprint():
    s = State.from_name("CORE")
    r = s.apply(Op.INIT).result
    assert r.name == "IMPRINT"


def test_scan_merge_gives_tribunal():
    s = State.from_name("SCAN")
    r = s.apply(Op.MERGE).result
    assert r.name == "TRIBUNAL"


def test_council_expand_gives_deploy():
    s = State.from_name("COUNCIL")
    r = s.apply(Op.EXPAND).result
    assert r.name == "DEPLOY"


# ── Chain ─────────────────────────────────────────────────────────────────────

def test_chain_code_review():
    start = State.from_name("PRIME")
    ops   = [Op.EXPAND, Op.ACT, Op.MERGE]
    chain = start.apply_chain(ops)
    assert len(chain) == 3
    assert chain[0].result.name == "LAUNCHER"
    assert chain[1].result.name == "CLOSER"
    assert chain[2].result.name == "COMMIT"


# ── Full validation ───────────────────────────────────────────────────────────

def test_all_256_transitions_valid():
    violations = validate_all_transitions()
    assert violations == [], f"Violations found: {violations}"


def test_transition_count():
    count = sum(1 for _ in range(64) for _ in Op)
    assert count == 256
