"""Joint decoder allowance and lossless finite visual diagnostic envelope."""
import json
import struct
from tools import _s2oe_visual_consistency as v

VERSION = 's2oe.visual-completion.v1'
ORDER = (2,2,8,8)
TABLE_LIMIT = 57344
# Eight complete IEEE-754 hex vectors, four bounded worker records, bindings,
# bounded original error, all 704 equality flags and structural overhead.
TABLE_UPPER = 36864 + 12288 + 2048 + 4096 + 704 + 1024


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


class FourWorkers:
    def __init__(self):
        self.used=0
        self.records=[]
        self.closed=False
        self.active=False

    def next(self,source,profile,run_id):
        v.need(not self.closed and not self.active and len(self.records)<4, 'DIAGNOSTIC_CLOSED_OR_BUSY')
        v.need(self.used<400,'GLOBAL_FRAME_LIMIT')
        remaining=400-self.used
        self.active=True
        child=None
        evidence=None
        failure=None
        try:
            child=v.open_video(source,profile,run_id)
            rgb,evidence=child.video_point(ORDER[len(self.records)],remaining)
            return rgb,evidence
        except BaseException as exc:
            self.closed=True
            failure=getattr(exc,'code',type(exc).__name__)
            raise
        finally:
            try:
                if child is not None:
                    try:
                        child.close()
                    finally:
                        n=child.counters['video_frames']
                        self.used+=n
                        self.records.append(dict(frames=n,remaining_before=remaining,
                            total_after=self.used,counters=dict(child.counters),
                            resources=dict(child.resources),frame=evidence,error=failure))
                        if n>remaining:
                            self.closed=True
                            v.need(False,'GLOBAL_FRAME_LIMIT')
            finally:
                self.active=False

    def close(self):
        v.need(not self.active,'DIAGNOSTIC_BUSY')
        self.closed=True
        return dict(complete=len(self.records)==4 and self.used<=400 and all(x['error'] is None for x in self.records),
                    frames=self.used,workers=len(self.records))


def pack_values(values):
    v.bind_values(values)
    return b''.join(struct.pack('>d',x) for x in values).hex()


def unpack_values(value):
    v.need(type(value) is str and len(value)==4608,'VECTOR_ENCODING_INVALID')
    try:
        raw=bytes.fromhex(value)
        values=tuple(x[0] for x in struct.iter_unpack('>d',raw))
    except (ValueError,struct.error) as exc:
        raise v.worker.WorkerError('VECTOR_ENCODING_INVALID') from exc
    v.bind_values(values)
    v.need(pack_values(values)==value,'VECTOR_ENCODING_INVALID')
    return values


def envelope(vectors,workers,bindings,error=None):
    v.need(len(vectors)<=8 and len(workers)<=4,'ENVELOPE_COUNT_INVALID')
    v.need(len(canonical(bindings))<=2048,'BINDINGS_LIMIT')
    v.need(len(canonical(error))<=4096,'ERROR_LIMIT')
    for item in workers:
        v.need(len(canonical(item))<=3072,'WORKER_EVIDENCE_LIMIT')
    if error is None:
        v.need(len(vectors)==8 and len(workers)==4,'INCOMPLETE_ENVELOPE')
    encoded=[pack_values(x) for x in vectors]
    # Fixed index roles: [full, occluded] per worker; no repeated payload values.
    pairs=((0,2,288),(4,6,288),(0,1,32),(2,3,32),(4,5,32),(6,7,32))
    flags=[]
    for left,right,count in pairs:
        flags.append(None if right>=len(encoded) else ''.join(
            '1' if encoded[left][16*i:16*i+16]==encoded[right][16*i:16*i+16] else '0'
            for i in range(count)))
    data=dict(version=VERSION,encoding='binary64-big-endian-hex',vectors=encoded,
              pairs=pairs,equalities=flags,workers=workers,bindings=bindings,error=error)
    raw=canonical(data)
    v.need(len(raw)<=TABLE_LIMIT,'TABLE_LIMIT')
    return raw


def restore(raw):
    v.need(type(raw) is bytes and len(raw)<=TABLE_LIMIT,'TABLE_LIMIT')
    data=json.loads(raw)
    v.need(data['version']==VERSION and data['encoding']=='binary64-big-endian-hex',
           'ENVELOPE_VERSION_INVALID')
    vectors=[unpack_values(x) for x in data['vectors']]
    v.need(envelope(vectors,data['workers'],data['bindings'],data['error'])==raw,
           'ENVELOPE_BINDING_INVALID')
    return vectors,data
