"""Bounded canonical JSON using the historical stdlib encoding options."""
import json

from tools._media_restart_work import require

VERSION = "media.bounded-json.v1"
MAX_BYTES = 4194304
TEXT_CHUNK = 4096
ENCODER = json.JSONEncoder(allow_nan=False, ensure_ascii=True,
                          sort_keys=True, separators=(",", ":"))


class Meter:
    def __init__(self, limit=MAX_BYTES):
        require(type(limit) is int and 0 < limit <= MAX_BYTES, "MEDIA_SERIALIZATION_BOUND")
        self.limit, self.size = limit, 0

    def charge(self, amount):
        require(self.size+amount <= self.limit, "MEDIA_SERIALIZATION_LIMIT",
                dict(limit=self.limit, accounted_bytes=self.size, next_bytes=amount,
                     complete_size_known=False))
        self.size += amount

    def atom(self, value):
        if isinstance(value, str):
            self.charge(2)
            # Measure escaped strings without first allocating their complete
            # escaped representation. Escaping is independent across chunks.
            for start in range(0, len(value), TEXT_CHUNK):
                self.charge(len(ENCODER.encode(value[start:start+TEXT_CHUNK]))-2)
        else:
            require(value is None or isinstance(value, (bool, int, float)), "MEDIA_JSON_TYPE")
            if isinstance(value, int):
                require(value.bit_length() <= self.limit*4, "MEDIA_SERIALIZATION_LIMIT",
                        dict(limit=self.limit, accounted_bytes=self.size,
                             integer_bits=value.bit_length(), complete_size_known=False))
            self.charge(len(ENCODER.encode(value)))

    def container(self, length):
        self.charge(2+max(0, length-1))


def measure(value, limit=MAX_BYTES):
    meter = Meter(limit)
    active = set()
    def visit(node, depth=0):
        require(depth <= 64, "MEDIA_SERIALIZATION_DEPTH")
        if isinstance(node, (dict, list, tuple)):
            require(id(node) not in active, "MEDIA_SERIALIZATION_CYCLE")
            active.add(id(node))
            meter.container(len(node))
            if isinstance(node, dict):
                for key, item in node.items():
                    require(isinstance(key, str), "MEDIA_JSON_KEY")
                    meter.atom(key)
                    meter.charge(1)
                    visit(item, depth+1)
            else:
                for item in node:
                    visit(item, depth+1)
            active.remove(id(node))
        else:
            meter.atom(node)
    visit(value)
    return meter.size


def canonical(value, limit=MAX_BYTES):
    size = measure(value, limit)
    output = bytearray()
    for text in ENCODER.iterencode(value):
        part = text.encode("ascii")
        require(len(output)+len(part) <= limit, "MEDIA_SERIALIZATION_LIMIT")
        output.extend(part)
    require(len(output) == size, "MEDIA_SERIALIZATION_CHANGED")
    return bytes(output)


def read_bounded(path, limit=MAX_BYTES):
    require(type(limit) is int and 0 < limit <= MAX_BYTES, "MEDIA_SERIALIZATION_BOUND")
    require(path.stat().st_size <= limit, "MEDIA_EVIDENCE_FILE_LIMIT")
    with path.open("rb") as stream:
        value = stream.read(limit+1)
    require(len(value) <= limit, "MEDIA_EVIDENCE_FILE_LIMIT")
    return value
