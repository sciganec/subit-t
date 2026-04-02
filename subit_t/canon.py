"""
SUBIT-T Canon - 64 archetypal states.

State = WHO x WHAT x WHEN
Each dimension has 4 values encoded as 2-bit integers.
Total: 4^3 = 64 states, represented as 6-bit integers (0-63).
"""

# WHO - Orientation of attention

WHO = {"ME": 0b10, "WE": 0b11, "YOU": 0b01, "THEY": 0b00}
WHO_I = {v: k for k, v in WHO.items()}

WHO_LABEL = {
    "ME": "self-directed",
    "WE": "co-directed",
    "YOU": "other-directed",
    "THEY": "system-directed",
}

WHO_DESCRIPTION = {
    "ME": "Agent acts autonomously, from its own initiative and internal state.",
    "WE": "Agent acts as part of a collective, coordinating with others.",
    "YOU": "Agent responds to and is directed by an external input or agent.",
    "THEY": "Agent observes and acts at the system level, detached from direct action.",
}


# WHAT - Operation on information

WHAT = {
    "EXPAND": 0b10,
    "TRANSFORM": 0b11,
    "REDUCE": 0b01,
    "PRESERVE": 0b00,
}
WHAT_I = {v: k for k, v in WHAT.items()}

WHAT_LABEL = {
    "EXPAND": "expand",
    "TRANSFORM": "transform",
    "REDUCE": "reduce",
    "PRESERVE": "preserve",
}

WHAT_DESCRIPTION = {
    "EXPAND": "Increases the space of possibilities. Generation, divergence, ideation.",
    "TRANSFORM": "Changes form while preserving quantity. Execution, implementation, conversion.",
    "REDUCE": "Narrows the space of possibilities. Analysis, convergence, critique.",
    "PRESERVE": "Fixes state without transformation. Memory, storage, observation.",
}

# WHEN - Phase of cognitive cycle

WHEN = {
    "INITIATE": 0b10,
    "SUSTAIN": 0b11,
    "INTEGRATE": 0b01,
    "RELEASE": 0b00,
}
WHEN_I = {v: k for k, v in WHEN.items()}

WHEN_LABEL = {
    "INITIATE": "initiate",
    "SUSTAIN": "sustain",
    "INTEGRATE": "integrate",
    "RELEASE": "release",
}

WHEN_DESCRIPTION = {
    "INITIATE": "Opening a new cycle. First impulse, maximum uncertainty, fresh start.",
    "SUSTAIN": "Maintaining active process. Peak activity, full capacity, flow state.",
    "INTEGRATE": "Integrating results. Synthesis, closing, convergence of outputs.",
    "RELEASE": "Completing the cycle. Idle, ready, latent potential for next cycle.",
}


def _make_bits(who: str, what: str, when: str) -> int:
    """
    Build a 6-bit state integer from WHO, WHAT, WHEN labels.
    """
    if what not in WHAT:
        raise KeyError(f"Unknown WHAT value: '{what}'")
    if when not in WHEN:
        raise KeyError(f"Unknown WHEN value: '{when}'")
    
    return (WHO[who] << 4) | (WHAT[what] << 2) | WHEN[when]


# Canon entries: (WHO, WHAT, WHEN, name)
_ENTRIES = [
    ("ME", "EXPAND", "INITIATE", "PRIME"),
    ("ME", "EXPAND", "SUSTAIN", "AUTHOR"),
    ("ME", "EXPAND", "INTEGRATE", "DRAFTER"),
    ("ME", "EXPAND", "RELEASE", "SEED"),
    ("ME", "TRANSFORM", "INITIATE", "LAUNCHER"),
    ("ME", "TRANSFORM", "SUSTAIN", "DRIVER"),
    ("ME", "TRANSFORM", "INTEGRATE", "CLOSER"),
    ("ME", "TRANSFORM", "RELEASE", "ENGINE"),
    ("ME", "REDUCE", "INITIATE", "PROBE"),
    ("ME", "REDUCE", "SUSTAIN", "AUDITOR"),
    ("ME", "REDUCE", "INTEGRATE", "REFINER"),
    ("ME", "REDUCE", "RELEASE", "WATCHER"),
    ("ME", "PRESERVE", "INITIATE", "LOGGER"),
    ("ME", "PRESERVE", "SUSTAIN", "ARCHIVIST"),
    ("ME", "PRESERVE", "INTEGRATE", "INDEXER"),
    ("ME", "PRESERVE", "RELEASE", "HERMIT"),
    ("WE", "EXPAND", "INITIATE", "SPARK"),
    ("WE", "EXPAND", "SUSTAIN", "CHORUS"),
    ("WE", "EXPAND", "INTEGRATE", "MERGE"),
    ("WE", "EXPAND", "RELEASE", "POOL"),
    ("WE", "TRANSFORM", "INITIATE", "DEPLOY"),
    ("WE", "TRANSFORM", "SUSTAIN", "SYNC"),
    ("WE", "TRANSFORM", "INTEGRATE", "COMMIT"),
    ("WE", "TRANSFORM", "RELEASE", "STANDBY"),
    ("WE", "REDUCE", "INITIATE", "COUNCIL"),
    ("WE", "REDUCE", "SUSTAIN", "TRIBUNAL"),
    ("WE", "REDUCE", "INTEGRATE", "VERDICT"),
    ("WE", "REDUCE", "RELEASE", "QUORUM"),
    ("WE", "PRESERVE", "INITIATE", "LEDGER"),
    ("WE", "PRESERVE", "SUSTAIN", "REGISTRY"),
    ("WE", "PRESERVE", "INTEGRATE", "DIGEST"),
    ("WE", "PRESERVE", "RELEASE", "ORIGIN"),
    ("YOU", "EXPAND", "INITIATE", "RESPONDER"),
    ("YOU", "EXPAND", "SUSTAIN", "ADAPTER"),
    ("YOU", "EXPAND", "INTEGRATE", "ECHO"),
    ("YOU", "EXPAND", "RELEASE", "BUFFER"),
    ("YOU", "TRANSFORM", "INITIATE", "HANDLER"),
    ("YOU", "TRANSFORM", "SUSTAIN", "EXECUTOR"),
    ("YOU", "TRANSFORM", "INTEGRATE", "RESOLVER"),
    ("YOU", "TRANSFORM", "RELEASE", "QUEUE"),
    ("YOU", "REDUCE", "INITIATE", "INTAKE"),
    ("YOU", "REDUCE", "SUSTAIN", "SCAN"),
    ("YOU", "REDUCE", "INTEGRATE", "FILTER"),
    ("YOU", "REDUCE", "RELEASE", "LISTENER"),
    ("YOU", "PRESERVE", "INITIATE", "INTAKE_LOG"),
    ("YOU", "PRESERVE", "SUSTAIN", "CACHE"),
    ("YOU", "PRESERVE", "INTEGRATE", "SNAPSHOT"),
    ("YOU", "PRESERVE", "RELEASE", "VOID"),
    ("THEY", "EXPAND", "INITIATE", "GHOST"),
    ("THEY", "EXPAND", "SUSTAIN", "ORACLE"),
    ("THEY", "EXPAND", "INTEGRATE", "SIGNAL"),
    ("THEY", "EXPAND", "RELEASE", "SHADOW"),
    ("THEY", "TRANSFORM", "INITIATE", "TRIGGER"),
    ("THEY", "TRANSFORM", "SUSTAIN", "FORCE"),
    ("THEY", "TRANSFORM", "INTEGRATE", "SWEEP"),
    ("THEY", "TRANSFORM", "RELEASE", "DAEMON"),
    ("THEY", "REDUCE", "INITIATE", "INSPECTOR"),
    ("THEY", "REDUCE", "SUSTAIN", "MONITOR"),
    ("THEY", "REDUCE", "INTEGRATE", "VALIDATOR"),
    ("THEY", "REDUCE", "RELEASE", "SENTINEL"),
    ("THEY", "PRESERVE", "INITIATE", "IMPRINT"),
    ("THEY", "PRESERVE", "SUSTAIN", "LEDGER_SYS"),
    ("THEY", "PRESERVE", "INTEGRATE", "FOSSIL"),
    ("THEY", "PRESERVE", "RELEASE", "CORE"),
]


CANON: dict[int, tuple[str, str, str, str]] = {
    _make_bits(who, what, when): (who, what, when, name)
    for who, what, when, name in _ENTRIES
}

BY_NAME: dict[str, int] = {
    name: _make_bits(who, what, when)
    for who, what, when, name in _ENTRIES
}


STATE_TYPE: dict[str, str] = {
    "CORE": "core",
    "PRIME": "core",
    "SYNC": "core",
    "SCAN": "core",
    "DRIVER": "core",
    "COUNCIL": "core",
    "EXECUTOR": "core",
    "MONITOR": "core",
    "DAEMON": "core",
    "SENTINEL": "core",
}

for _, _, _, state_name in _ENTRIES:
    STATE_TYPE.setdefault(state_name, "transient")


STATE_WEIGHT: dict[str, float] = {
    state_name: (1.0 if STATE_TYPE[state_name] == "core" else 0.7)
    for _, _, _, state_name in _ENTRIES
}
