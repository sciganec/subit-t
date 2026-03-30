"""Tests for XOR guards (v1 compatibility layer)."""
import pytest
from subit_t import State
from subit_t.guards import (
    guard_driver_sync, guard_executor_scan, guard_council_prime,
    guard_winter_collapse, make_guard,
)


def s(name): return State.from_name(name)


def xor(a, b): return a ^ b


# ── Three specific guards ─────────────────────────────────────────────────────

def test_guard_driver_sync_triggers():
    cur, imp = s("DRIVER"), s("SYNC")
    raw = xor(cur, imp)
    assert raw.name == "VOID"
    result = guard_driver_sync(cur, imp, raw)
    assert result is not None
    assert result.triggered is True
    assert result.replacement.name == "COMMIT"


def test_guard_executor_scan_triggers():
    cur, imp = s("EXECUTOR"), s("SCAN")
    raw = xor(cur, imp)
    assert raw.name == "SHADOW"
    result = guard_executor_scan(cur, imp, raw)
    assert result is not None
    assert result.replacement.name == "FILTER"


def test_guard_council_prime_triggers():
    cur, imp = s("COUNCIL"), s("PRIME")
    raw = xor(cur, imp)
    assert raw.name == "QUEUE"
    result = guard_council_prime(cur, imp, raw)
    assert result is not None
    assert result.replacement.name == "SPARK"


# ── Guards do not trigger on normal transitions ───────────────────────────────

def test_guard_driver_sync_no_trigger_on_other():
    cur, imp = s("DRIVER"), s("PRIME")
    raw = xor(cur, imp)
    assert guard_driver_sync(cur, imp, raw) is None


def test_guard_executor_scan_no_trigger_on_other():
    cur, imp = s("EXECUTOR"), s("PRIME")
    raw = xor(cur, imp)
    assert guard_executor_scan(cur, imp, raw) is None


# ── Winter collapse guard ─────────────────────────────────────────────────────

def test_winter_collapse_triggers_on_active_active_winter():
    # Find a pair where active+active→WINTER (not self-cancel)
    found = False
    for a_bits in range(64):
        a = State(a_bits)
        if a.when not in ("SPRING", "SUMMER"):
            continue
        for b_bits in range(64):
            if a_bits == b_bits:
                continue  # skip self-cancel
            b = State(b_bits)
            if b.when not in ("SPRING", "SUMMER"):
                continue
            raw = a ^ b
            if raw.when == "WINTER":
                result = guard_winter_collapse(a, b, raw)
                if result and result.triggered:
                    assert result.replacement.when == "SUMMER"
                    found = True
                    break
        if found:
            break
    assert found, "No active+active→WINTER case found to test"


def test_winter_collapse_allows_self_cancel():
    a = State.from_name("PRIME")
    raw = a ^ a  # = CORE (self-cancel is legitimate)
    result = guard_winter_collapse(a, a, raw)
    assert result is None  # self-cancel must pass through


# ── make_guard factory ────────────────────────────────────────────────────────

def test_make_guard_triggers():
    g = make_guard(("DRIVER", "SYNC"), "COMMIT", "test guard")
    cur, imp = s("DRIVER"), s("SYNC")
    raw = xor(cur, imp)
    result = g(cur, imp, raw)
    assert result is not None
    assert result.replacement.name == "COMMIT"
    assert result.reason == "test guard"


def test_make_guard_no_trigger():
    g = make_guard(("DRIVER", "SYNC"), "COMMIT", "test guard")
    cur, imp = s("PRIME"), s("SCAN")
    raw = xor(cur, imp)
    assert g(cur, imp, raw) is None
