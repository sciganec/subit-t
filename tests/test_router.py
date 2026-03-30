"""Tests for Router."""
import pytest
from subit_t import State, Op, Router
from subit_t.core import S_PRIME, S_SCAN, S_CORE


def test_router_route_returns_record():
    router = Router()
    record = router.route(S_PRIME, Op.MERGE)
    assert "transition" in record
    assert record["transition"]["operator"] == "MERGE"


def test_router_dispatch_by_state():
    router = Router()
    called = []

    @router.on(state="SPARK")
    def fn(state, op, ctx):
        called.append(state.name)
        return {"ok": True}

    router.route(S_PRIME, Op.MERGE)  # PRIME + MERGE = SPARK
    assert called == ["SPARK"]


def test_router_dispatch_by_op():
    router = Router()
    called = []

    @router.on(op=Op.ACT)
    def fn(state, op, ctx):
        called.append(op.value)
        return {}

    router.route(S_PRIME, Op.ACT)
    assert "ACT" in called


def test_router_fallback():
    router = Router()
    results = []

    def fallback(state, op, ctx):
        results.append("fallback")
        return {}

    router.register(fallback)
    router.route(S_PRIME, Op.INIT)
    assert results == ["fallback"]


def test_router_history():
    router = Router()
    router.route(S_PRIME, Op.INIT)
    router.route(S_PRIME, Op.MERGE)
    assert len(router.history) == 2


def test_router_op_distribution():
    router = Router()
    router.route(S_PRIME, Op.INIT)
    router.route(S_PRIME, Op.INIT)
    router.route(S_PRIME, Op.ACT)
    dist = router.op_distribution()
    assert dist["INIT"] == 2
    assert dist["ACT"] == 1


def test_router_stuck_detection_over_act():
    router = Router()
    for _ in range(10):
        router.route(S_PRIME, Op.ACT)
    flags = router.stuck_detection()
    assert flags["over_act"] is True


def test_router_stuck_detection_no_init():
    router = Router()
    for _ in range(5):
        router.route(S_PRIME, Op.ACT)
    flags = router.stuck_detection()
    assert flags["no_init"] is True


def test_router_chain():
    router = Router()
    chain = router.chain(S_PRIME, [Op.EXPAND, Op.ACT, Op.MERGE])
    assert len(chain) == 3
    assert chain[-1]["transition"]["result"]["name"] == "COMMIT"


def test_router_idempotent_rate():
    router = Router()
    router.route(State.from_name("PRIME"), Op.INIT)   # PRIME already SPRING → idempotent
    router.route(State.from_name("DRIVER"), Op.ACT)   # not idempotent
    rate = router.idempotent_rate()
    assert 0.0 <= rate <= 1.0


def test_router_reset():
    router = Router()
    router.route(S_PRIME, Op.INIT)
    router.reset()
    assert len(router.history) == 0


def test_router_route_text():
    router = Router()
    record = router.route_text("Review this code for memory leaks")
    assert "encoding" in record
    assert "transition" in record


def test_router_export_history():
    import json
    router = Router()
    router.route(S_PRIME, Op.ACT)
    exported = router.export_history()
    data = json.loads(exported)
    assert isinstance(data, list)
    assert len(data) == 1
