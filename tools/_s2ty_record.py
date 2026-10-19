"""Canonical neutral success record for S2TY event control."""
from __future__ import annotations
import json
from typing import Any
from tools import _s2ty_event_control as control

VERSION="s2ty.success-record.v1"
def canonical(value:object)->bytes:return json.dumps(value,allow_nan=False,sort_keys=True,separators=(",",":")).encode("utf-8")
def encode_events(events):
 out=[]
 for event in events:
  row={"ordinal":event["ordinal"],"kind":event["kind"],"segment":event["segment"]}
  if event.get("values") is not None: row["values_hex"]=[value.hex() for value in event["values"]]
  out.append(row)
 return out
def decode_events(rows):
 out=[]
 for row in rows:
  event={"ordinal":row["ordinal"],"kind":row["kind"],"segment":row["segment"],"values":None}
  if "values_hex" in row:event["values"]=tuple(float.fromhex(value) for value in row["values_hex"])
  out.append(event)
 return out
def build(events,profile,owner):
 result=control.run(events,profile,owner)
 return dict(version=VERSION,status=result["status"],profile=profile,owner=owner,inputs=encode_events(events),result=result)
def dumps(record):return canonical(record)
def loads(data:bytes):
 record=json.loads(data);assert record["version"]==VERSION
 return record
