"""Tests for v3 cyclic State, Op and transition semantics."""

from subit_t import Op, State, validate_all_transitions


def test_state_from_name():
    state = State.from_name("PRIME")
    assert state.who == "ME"
    assert state.what == "EXPAND"
    assert state.when == "INITIATE"
    assert state.name == "PRIME"


def test_state_from_dims_accepts_new_names():
    assert State.from_dims("ME", "EXPAND", "INITIATE").name == "PRIME"


def test_state_from_dims_accepts_legacy_names():
    assert State.from_dims("ME", "EAST", "SPRING").name == "PRIME"


def test_who_shift_cycles_driver_to_sync():
    assert State.from_name("DRIVER").apply(Op.WHO_SHIFT).result.name == "SYNC"


def test_what_shift_cycles_prime_to_launcher():
    assert State.from_name("PRIME").apply(Op.WHAT_SHIFT).result.name == "LAUNCHER"


def test_when_shift_cycles_drafter_to_prime():
    assert State.from_name("DRAFTER").apply(Op.WHEN_SHIFT).result.name == "PRIME"


def test_inv_rolls_back_sync_to_prime():
    assert State.from_name("SYNC").apply(Op.INV).result.name == "PRIME"


def test_all_operators_move():
    state = State.from_name("PRIME")
    for op in Op:
        assert state.apply(op).result != state
        assert state.apply(op).idempotent is False


def test_four_who_shifts_return_to_start():
    state = State.from_name("DRIVER")
    current = state
    for _ in range(4):
        current = current.apply(Op.WHO_SHIFT).result
    assert current == state


def test_composability_example():
    state = State.from_name("DRIVER")
    left = state.apply(Op.WHO_SHIFT).result.apply(Op.WHO_SHIFT).result
    right = State.from_name("FORCE")
    assert left == right


def test_validate_all_transitions_has_no_violations():
    assert validate_all_transitions() == []
