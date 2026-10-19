"""REV1 recipe; research material requires a separately consumed admission."""
import hashlib
import os
from pathlib import Path

NAMES = ('continuation', 'dependent-A', 'dependent-B')


class _Permit:
    def __init__(self, folder):
        self.folder = Path(folder).resolve()
        self.pid = os.getpid()


def admit(auth, folder):
    from tools.s2uc_ura1_prepare_rev1 import validate_admission
    validate_admission(auth, folder)
    return _Permit(folder)


def gate(neutral, permit=None):
    if type(neutral) is not bool:
        raise ValueError('NEUTRAL_FLAG')
    if not neutral:
        if type(permit) is not _Permit or permit.pid != os.getpid():
            raise PermissionError('REV1_RESEARCH_LOCKED')
        if not (permit.folder/'START.json').exists() or (permit.folder/'sources-manifest.json').exists():
            raise PermissionError('SOURCE_PHASE_CLOSED')


class Stream:
    def __init__(self, r, phase, name, *, neutral=True, permit=None, draw=None):
        gate(neutral, permit)
        if type(r) is not int or not 1 <= r <= 32 or type(phase) is not int or phase not in (0, 1) or name not in NAMES:
            raise ValueError('STREAM_SPEC')
        if draw is not None and not neutral:
            raise PermissionError('DRAW_NEUTRAL_ONLY')
        self.r, self.phase, self.name = r, phase, name
        self.neutral, self.cursor, self.draw = neutral, 0, draw

    def below(self, n):
        if type(n) is not int or not 1 <= n <= 128:
            raise ValueError('DRAW_RANGE')
        cutoff = 2**64 - 2**64 % n
        while True:
            if self.cursor >= 4096:
                raise ValueError('DRAW_LIMIT')
            kind = 'neutral/v1' if self.neutral else 'source/v1'
            key = f'MCM-URA1-REV1/{kind}/r={self.r}/phase={self.phase}/stream={self.name}/draw={self.cursor}'
            u = self.draw(self.cursor) if self.draw else int.from_bytes(hashlib.sha256(key.encode('utf-8')).digest()[:8], 'big')
            self.cursor += 1
            if type(u) is not int or not 0 <= u < 2**64:
                raise ValueError('DRAW_VALUE')
            if u < cutoff:
                return u % n

    def shuffle(self, items):
        values = list(items)
        for i in range(len(values)-1, 0, -1):
            j = self.below(i+1)
            values[i], values[j] = values[j], values[i]
        return values


def generate(r, *, neutral=True, permit=None):
    gate(neutral, permit)
    ids, draws = [], {}
    for p in (0, 1):
        streams = {s: Stream(r, p, s, neutral=neutral, permit=permit) for s in NAMES}
        ys = streams['continuation'].shuffle([3]*64 + [4]*64)
        ap = streams['dependent-A'].shuffle([i for i, y in enumerate(ys) if y == 3])
        bp = streams['dependent-B'].shuffle([i for i, y in enumerate(ys) if y == 4])
        a, b = (48, 16) if (r % 2 == 1) == (p == 0) else (16, 48)
        xs = set(ap[:a] + bp[:b])
        ids.extend(v for i, y in enumerate(ys) for v in (0 if i in xs else 1, 2, y, 5))
        draws[str(p)] = {s: stream.cursor for s, stream in streams.items()}
    return dict(replicate=r, orientation=(r-1) % 2, neutral_only=neutral,
                catalog=[[x+j/4096 for j in range(48)] for x in (.125, .875, .5, .25, .75, .0625)],
                ids=ids, draws=draws)
