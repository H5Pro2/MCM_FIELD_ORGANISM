"""Independent CR1 reconstruction; only admission is shared with production."""
import hashlib
import json
from collections import Counter
from tools._s2uc_ura1_cr1_sources import gate


def verify(record, r, *, neutral=True, permit=None):
    gate(neutral, permit)
    if type(r) is not int or r < 1 or r > 32:
        raise ValueError('REFERENCE_REPLICATE')
    counters, ids, contingencies = {}, [], []
    for phase in range(2):
        counters[str(phase)] = {}

        def permute(sequence, name):
            result = list(sequence)
            cursor = 0
            for length in range(len(result), 1, -1):
                limit = ((1 << 64)//length)*length
                while True:
                    if cursor == 4096:
                        raise ValueError('REFERENCE_DRAW_LIMIT')
                    text = ('MCM-URA1-CR1/' + ('neutral/v1' if neutral else 'source/v1') + '/r=' + str(r)
                            + '/phase=' + str(phase) + '/stream=' + name + '/draw=' + str(cursor))
                    value = int(hashlib.sha256(text.encode('ascii')).hexdigest()[:16], 16)
                    cursor += 1
                    if value < limit:
                        break
                pick = value % length
                last = result[length-1]
                result[length-1] = result[pick]
                result[pick] = last
            counters[str(phase)][name] = cursor
            return result

        target = permute([3 for _ in range(64)] + [4 for _ in range(64)], 'continuation')
        cue = [1]*128
        counts = ((48, 16), (16, 48))[(r+1+phase) % 2]
        for val, name, count in ((3, 'dependent-A', counts[0]), (4, 'dependent-B', counts[1])):
            positions = [i for i in range(128) if target[i] == val]
            for pos in permute(positions, name)[:count]:
                cue[pos] = 0
        for i in range(128):
            ids.extend((cue[i], 2, target[i], 5))
        counts_actual = Counter(zip(cue, target))
        wanted = (counts[0], counts[1], 64-counts[0], 64-counts[1])
        if tuple(counts_actual[k] for k in ((0, 3), (0, 4), (1, 3), (1, 4))) != wanted:
            raise ValueError('REFERENCE_CONTINGENCY')
        contingencies.append(list(wanted))
    expected = dict(replicate=r, orientation=(r+1) % 2, neutral_only=neutral,
                    catalog=[[float(base+j/4096) for j in range(48)] for base in (1/8, 7/8, 1/2, 1/4, 3/4, 1/16)],
                    ids=ids, draws=counters)
    canonical = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)
    if canonical(record) != canonical(expected):
        raise ValueError('SOURCE_REFERENCE')
    return dict(reference_equal=True, frames=1024, contingencies=contingencies, draws=counters)
