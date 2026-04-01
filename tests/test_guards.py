"""Tests for XOR guards kept for compatibility analysis."""

from subit_t import State
from subit_t.guards import (
    guard_council_prime,
    guard_driver_sync,
    guard_executor_scan,
    guard_winter_collapse,
    make_guard,
)


def s(name):
    return State.from_name(name)


def xor(a, b):
    return a ^ b


def test_guard_driver_sync_triggers():
    cur, imp = s("DRIVER"), s("SYNC")
    raw = xor(cur, imp)
    result = guard_driver_sync(cur, imp, raw)
    assert result is not None
    assert result.replacement.name == "COMMIT"


def test_guard_executor_scan_triggers():
    cur, imp = s("EXECUTOR"), s("SCAN")
    raw = xor(cur, imp)
    result = guard_executor_scan(cur, imp, raw)
    assert result is not None
    assert result.replacement.name == "FILTER"


def test_guard_council_prime_triggers():
    cur, imp = s("COUNCIL"), s("PRIME")
    raw = xor(cur, imp)
    result = guard_council_prime(cur, imp, raw)
    assert result is not None
    assert result.replacement.name == "SPARK"


def test_guard_driver_sync_no_trigger_on_other():
    assert guard_driver_sync(s("DRIVER"), s("PRIME"), xor(s("DRIVER"), s("PRIME"))) is None


def test_guard_executor_scan_no_trigger_on_other():
    assert guard_executor_scan(s("EXECUTOR"), s("PRIME"), xor(s("EXECUTOR"), s("PRIME"))) is None


def test_winter_collapse_triggers_on_active_active_release():
    found = False
    for a_bits in range(64):
        a = State(a_bits)
        if a.when not in ("INITIATE", "SUSTAIN"):
            continue
        for b_bits in range(64):
            if a_bits == b_bits:
                continue
            b = State(b_bits)
            if b.when not in ("INITIATE", "SUSTAIN"):
                continue
            raw = a ^ b
            if raw.when == "RELEASE":
                result = guard_winter_collapse(a, b, raw)
                if result and result.triggered:
                    assert result.replacement.when == "SUSTAIN"
                    found = True
                    break
        if found:
            break
    assert found


def test_winter_collapse_allows_self_cancel():
    a = State.from_name("PRIME")
    assert guard_winter_collapse(a, a, a ^ a) is None


def test_make_guard_triggers():
    guard = make_guard(("DRIVER", "SYNC"), "COMMIT", "test guard")
    result = guard(s("DRIVER"), s("SYNC"), xor(s("DRIVER"), s("SYNC")))
    assert result is not None
    assert result.replacement.name == "COMMIT"
    assert result.reason == "test guard"


def test_make_guard_no_trigger():
    guard = make_guard(("DRIVER", "SYNC"), "COMMIT", "test guard")
    assert guard(s("PRIME"), s("SCAN"), xor(s("PRIME"), s("SCAN"))) is None
