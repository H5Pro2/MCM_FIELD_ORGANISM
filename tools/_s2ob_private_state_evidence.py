"""Lossless wire representation only; never modifies or advances native memory."""
import base64
import binascii
from copy import deepcopy
import hashlib
import json
import math
import struct

SCHEMA = "s2ob.state.binary64-be.v1"
MAX_BYTES = 98304
MAX_VALUES = 5568  # 9*336 + 3*(48+288) + 8*48 + 4*288


class StateEvidenceError(ValueError):
    def __init__(self,code,balance=None):
        self.code,self.balance=code,balance
        super().__init__(code)


def require(ok,code):
    if not ok: raise StateEvidenceError(code)


def canonical(value):
    return json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")


def vectors(body):
    banks=((body["b4_state"]["entries"],9,(("values",336),)),
           (body["tspm_state"]["fast_state"]["slots"],3,(("auditory_values",48),("visual_values",288))),
           (body["tspm_state"]["auditory_ppb1_state"]["slots"],8,(("prototype_values",48),)),
           (body["tspm_state"]["visual_ppb1_state"]["slots"],4,(("prototype_values",288),)))
    for slots,count,keys in banks:
        require(type(slots) in (list,tuple) and len(slots)==count,"STATE_VECTOR_FORM_INVALID")
        for slot in slots:
            for key,dimension in keys: yield slot,key,dimension


def encode(native):
    try:
        require(type(native) is dict,"STATE_NATIVE_FORM_INVALID")
        raw=canonical(native); body=deepcopy(native); count=0
        for slot,key,dimension in vectors(body):
            xs=slot[key]
            require(type(xs) in (list,tuple) and len(xs) in (0,dimension)
                and all(type(x) is float and math.isfinite(x) for x in xs),"STATE_VECTOR_FORM_INVALID")
            count+=len(xs)
            binary=struct.pack(">"+"d"*len(xs),*xs)
            slot[key]={"f64be":base64.b64encode(binary).decode("ascii")}
        require(count<=MAX_VALUES,"STATE_VALUE_COUNT_INVALID")
        encoded=dict(schema=SCHEMA,native_sha256=hashlib.sha256(raw).hexdigest(),body=body)
        measured=len(canonical(encoded))
        if measured>MAX_BYTES:
            raise StateEvidenceError("STATE_EVIDENCE_LIMIT",dict(belegklasse="STATE",native_bytes=len(raw),
                encoded_bytes=measured,limit=MAX_BYTES,state_digest=native.get("state_digest")))
        return encoded
    except StateEvidenceError: raise
    except (KeyError,TypeError,ValueError,OverflowError) as exc:
        raise StateEvidenceError("STATE_NATIVE_FORM_INVALID") from exc


def decode(encoded):
    try:
        require(type(encoded) is dict and set(encoded)=={"schema","native_sha256","body"}
            and encoded["schema"]==SCHEMA and len(canonical(encoded))<=MAX_BYTES,"STATE_ENCODING_INVALID")
        body=deepcopy(encoded["body"]); count=0
        for slot,key,dimension in vectors(body):
            wire=slot[key]
            require(type(wire) is dict and set(wire)=={"f64be"} and type(wire["f64be"]) is str
                and len(wire["f64be"]) in (0,4*((8*dimension+2)//3)),"STATE_ENCODING_INVALID")
            binary=base64.b64decode(wire["f64be"],validate=True)
            require(len(binary) in (0,8*dimension) and base64.b64encode(binary).decode("ascii")==wire["f64be"],"STATE_ENCODING_INVALID")
            xs=list(struct.unpack(">"+"d"*(len(binary)//8),binary))
            require(all(math.isfinite(x) for x in xs),"STATE_ENCODING_INVALID")
            slot[key]=xs;count+=len(xs)
        require(count<=MAX_VALUES and hashlib.sha256(canonical(body)).hexdigest()==encoded["native_sha256"],"STATE_NATIVE_DIGEST_INVALID")
        return body
    except StateEvidenceError: raise
    except (KeyError,TypeError,ValueError,OverflowError,binascii.Error) as exc:
        raise StateEvidenceError("STATE_ENCODING_INVALID") from exc
