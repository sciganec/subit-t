"""
SUBIT-T Canon — 64 archetypal states.

State = WHO × WHERE × WHEN
Each dimension has 4 values encoded as 2-bit integers.
Total: 4³ = 64 states, represented as 6-bit integers (0–63).
"""

WHO   = {"ME": 0b10, "WE": 0b11, "YOU": 0b01, "THEY": 0b00}
WHERE = {"EAST": 0b10, "SOUTH": 0b11, "WEST": 0b01, "NORTH": 0b00}
WHEN  = {"SPRING": 0b10, "SUMMER": 0b11, "AUTUMN": 0b01, "WINTER": 0b00}

WHO_I   = {v: k for k, v in WHO.items()}
WHERE_I = {v: k for k, v in WHERE.items()}
WHEN_I  = {v: k for k, v in WHEN.items()}

WHO_LABEL   = {"ME": "autonomous", "WE": "collective", "YOU": "reactive", "THEY": "observer"}
WHERE_LABEL = {"EAST": "generate", "SOUTH": "execute", "WEST": "analyze", "NORTH": "store"}
WHEN_LABEL  = {"SPRING": "initiate", "SUMMER": "active", "AUTUMN": "closing", "WINTER": "idle"}

_ENTRIES = [
    ("ME",   "EAST",  "SPRING", "PRIME"),
    ("ME",   "EAST",  "SUMMER", "AUTHOR"),
    ("ME",   "EAST",  "AUTUMN", "DRAFTER"),
    ("ME",   "EAST",  "WINTER", "SEED"),
    ("ME",   "SOUTH", "SPRING", "LAUNCHER"),
    ("ME",   "SOUTH", "SUMMER", "DRIVER"),
    ("ME",   "SOUTH", "AUTUMN", "CLOSER"),
    ("ME",   "SOUTH", "WINTER", "ENGINE"),
    ("ME",   "WEST",  "SPRING", "PROBE"),
    ("ME",   "WEST",  "SUMMER", "AUDITOR"),
    ("ME",   "WEST",  "AUTUMN", "REFINER"),
    ("ME",   "WEST",  "WINTER", "WATCHER"),
    ("ME",   "NORTH", "SPRING", "LOGGER"),
    ("ME",   "NORTH", "SUMMER", "ARCHIVIST"),
    ("ME",   "NORTH", "AUTUMN", "INDEXER"),
    ("ME",   "NORTH", "WINTER", "HERMIT"),
    ("WE",   "EAST",  "SPRING", "SPARK"),
    ("WE",   "EAST",  "SUMMER", "CHORUS"),
    ("WE",   "EAST",  "AUTUMN", "MERGE"),
    ("WE",   "EAST",  "WINTER", "POOL"),
    ("WE",   "SOUTH", "SPRING", "DEPLOY"),
    ("WE",   "SOUTH", "SUMMER", "SYNC"),
    ("WE",   "SOUTH", "AUTUMN", "COMMIT"),
    ("WE",   "SOUTH", "WINTER", "STANDBY"),
    ("WE",   "WEST",  "SPRING", "COUNCIL"),
    ("WE",   "WEST",  "SUMMER", "TRIBUNAL"),
    ("WE",   "WEST",  "AUTUMN", "VERDICT"),
    ("WE",   "WEST",  "WINTER", "QUORUM"),
    ("WE",   "NORTH", "SPRING", "LEDGER"),
    ("WE",   "NORTH", "SUMMER", "REGISTRY"),
    ("WE",   "NORTH", "AUTUMN", "DIGEST"),
    ("WE",   "NORTH", "WINTER", "ORIGIN"),
    ("YOU",  "EAST",  "SPRING", "RESPONDER"),
    ("YOU",  "EAST",  "SUMMER", "ADAPTER"),
    ("YOU",  "EAST",  "AUTUMN", "ECHO"),
    ("YOU",  "EAST",  "WINTER", "BUFFER"),
    ("YOU",  "SOUTH", "SPRING", "HANDLER"),
    ("YOU",  "SOUTH", "SUMMER", "EXECUTOR"),
    ("YOU",  "SOUTH", "AUTUMN", "RESOLVER"),
    ("YOU",  "SOUTH", "WINTER", "QUEUE"),
    ("YOU",  "WEST",  "SPRING", "INTAKE"),
    ("YOU",  "WEST",  "SUMMER", "SCAN"),
    ("YOU",  "WEST",  "AUTUMN", "FILTER"),
    ("YOU",  "WEST",  "WINTER", "LISTENER"),
    ("YOU",  "NORTH", "SPRING", "INTAKE_LOG"),
    ("YOU",  "NORTH", "SUMMER", "CACHE"),
    ("YOU",  "NORTH", "AUTUMN", "SNAPSHOT"),
    ("YOU",  "NORTH", "WINTER", "VOID"),
    ("THEY", "EAST",  "SPRING", "GHOST"),
    ("THEY", "EAST",  "SUMMER", "ORACLE"),
    ("THEY", "EAST",  "AUTUMN", "SIGNAL"),
    ("THEY", "EAST",  "WINTER", "SHADOW"),
    ("THEY", "SOUTH", "SPRING", "TRIGGER"),
    ("THEY", "SOUTH", "SUMMER", "FORCE"),
    ("THEY", "SOUTH", "AUTUMN", "SWEEP"),
    ("THEY", "SOUTH", "WINTER", "DAEMON"),
    ("THEY", "WEST",  "SPRING", "INSPECTOR"),
    ("THEY", "WEST",  "SUMMER", "MONITOR"),
    ("THEY", "WEST",  "AUTUMN", "VALIDATOR"),
    ("THEY", "WEST",  "WINTER", "SENTINEL"),
    ("THEY", "NORTH", "SPRING", "IMPRINT"),
    ("THEY", "NORTH", "SUMMER", "LEDGER_SYS"),
    ("THEY", "NORTH", "AUTUMN", "FOSSIL"),
    ("THEY", "NORTH", "WINTER", "CORE"),
]


def _make_bits(who: str, where: str, when: str) -> int:
    return (WHO[who] << 4) | (WHERE[where] << 2) | WHEN[when]


# bits → (who, where, when, name)
CANON: dict[int, tuple[str, str, str, str]] = {
    _make_bits(w, wh, wn): (w, wh, wn, name)
    for w, wh, wn, name in _ENTRIES
}

# name → bits
BY_NAME: dict[str, int] = {
    name: _make_bits(w, wh, wn)
    for w, wh, wn, name in _ENTRIES
}
