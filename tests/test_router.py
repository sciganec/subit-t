"""Tests for the v3 router."""

import json

from subit_t import Op, Router, State
from subit_t.core import S_PRIME


def test_router_route_returns_record():
    router = Router()
    record = router.route(S_PRIME, Op.WHO_SHIFT)
    assert "transition" in record
    assert record["transition"]["operator"] == "WHO_SHIFT"


def test_router_dispatch_by_state():
    router = Router()
    called = []

    @router.on(state="SPARK")
    def fn(state, op, ctx):
        called.append(state.name)
        return {"ok": True}

    router.route(State.from_name("COUNCIL"), Op.WHAT_SHIFT)
    assert called == ["SPARK"]


def test_router_dispatch_by_op():
    router = Router()
    called = []

    @router.on(op=Op.INV)
    def fn(state, op, ctx):
        called.append(op.value)
        return {}

    router.route(State.from_name("SYNC"), Op.INV)
    assert called == ["INV"]


def test_router_fallback():
    router = Router()
    hits = []

    def fallback(state, op, ctx):
        hits.append("fallback")
        return {}

    router.register(fallback)
    router.route(S_PRIME, Op.WHEN_SHIFT)
    assert hits == ["fallback"]


def test_router_history_and_distribution():
    router = Router()
    router.route(S_PRIME, Op.WHAT_SHIFT)
    router.route(S_PRIME, Op.WHAT_SHIFT)
    router.route(S_PRIME, Op.INV)
    assert len(router.history) == 3
    assert router.op_distribution()["WHAT_SHIFT"] == 2
    assert router.op_distribution()["INV"] == 1


def test_router_stuck_detection_flags_are_v3_named():
    router = Router()
    for _ in range(10):
        router.route(S_PRIME, Op.WHAT_SHIFT)
    flags = router.stuck_detection()
    assert "what_heavy" in flags
    assert flags["what_heavy"] is True


def test_router_chain():
    router = Router()
    chain = router.chain(State.from_name("DRIVER"), [Op.WHO_SHIFT, Op.WHAT_SHIFT, Op.INV])
    assert len(chain) == 3


def test_router_idempotent_rate_is_zero_under_v3():
    router = Router()
    router.route(State.from_name("PRIME"), Op.WHO_SHIFT)
    router.route(State.from_name("DRIVER"), Op.INV)
    assert router.idempotent_rate() == 0.0


def test_router_route_text():
    router = Router()
    record = router.route_text("Review this code for memory leaks")
    assert "encoding" in record
    assert "transition" in record


def test_router_export_history():
    router = Router()
    router.route(S_PRIME, Op.WHEN_SHIFT)
    exported = json.loads(router.export_history())
    assert isinstance(exported, list)
    assert len(exported) == 1
