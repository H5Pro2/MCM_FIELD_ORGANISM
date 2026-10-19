"""Declarative complete raster; no policy, score, filesystem or runtime imports."""
from itertools import product

RECIPES = {'X': ('3/16', '5/16', '13/16', '15/16'),
           'Y': ('3/16', '5/16', '9/16', '15/16')}


def cases():
    result = []
    for duration in (3, 5):
        for chars in product('XY', repeat=4):
            word = ''.join(chars)
            blocks = [c for c in word for _ in range(duration)]
            length = len(blocks)*4
            switches = []
            for phase in range(1, 4):
                if word[phase] != word[phase-1]:
                    first = phase*duration*4+3
                    switches.append(dict(phase=phase, wanted=word[phase],
                        direction=word[phase-1]+word[phase],
                        kind='return' if word[phase] in word[:phase] else 'change',
                        targets=list(range(first, first+4*duration, 4))))
            g = list(range(3, length, 2)); h = list(range(7, length, 4))
            stable = len(set(word)) == 1
            result.append(dict(id=f'D{duration}-{word}', duration=duration, word=word,
                blocks=blocks, frames=length, stable=stable, switches=switches,
                masks=dict(G=g, H=h, N=[t for t in g if t not in h],
                    F=[s['targets'][0] for s in switches],
                    A=[t for s in switches for t in s['targets'][1:]],
                    S=h if stable else [], S_w=list(range(11, length, 4)) if stable else [])))
    return result


def materialize(spec):
    """Only the separately authorized runner may call this for raster cases."""
    if spec not in cases():
        raise ValueError('SOURCE_SPEC')
    return [tuple([int(x.split('/')[0])/int(x.split('/')[1])]*48)
            for block in spec['blocks'] for x in RECIPES[block]]


def validate(values, spec):
    if spec not in cases() or len(values) != spec['frames']:
        raise ValueError('SOURCE_SHAPE')
    for i, vector in enumerate(values):
        n, d = RECIPES[spec['blocks'][i//4]][i%4].split('/')
        if len(vector) != 48 or any(type(x) is not float or x != int(n)/int(d) for x in vector):
            raise ValueError('SOURCE_VALUE')
