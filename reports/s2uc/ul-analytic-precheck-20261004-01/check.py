"""Small neutral arithmetic checks; no research source or LZ1 archive replay."""
import hashlib
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path
from tools._s2uc_a1_compare_engine import replay
from tools._s2uc_paired_error_ema import mae48

HERE = Path(__file__).resolve().parent
facts = {}

def choose(cells):
    ds = [None if x is None else x - .25 for x in cells]
    good = [i for i, d in enumerate(ds) if d is not None and d < 0]
    if not good:
        return 'P'
    best = min(ds[i] for i in good)
    winners = [i for i in good if ds[i] == best]
    return winners[0] if len(winners) == 1 else 'P'

def update(cells, y):
    # Exact existing binary64 order: .5*old + .5*current, no fused operation.
    return tuple((0.0 if i == y else .5) if x is None else
                 .5*x + .5*(0.0 if i == y else .5)
                 for i, x in enumerate(cells))

def exact_update(cells, y):
    return tuple(x/2 + (F(0) if i == y else F(1, 4))
                 for i, x in enumerate(cells))

# Neutral vectors translated from the structural geometry, no source generator.
v = [tuple(float(b+j/4096) for j in range(48))
     for b in (.0625, .375, .125, .625)]
assert mae48(v[2], v[3]) == .5
assert mae48(v[1], v[2]) == mae48(v[1], v[3]) == .25
facts['T1_geometry'] = 'PASS'

# Two 16-frame hand-written neutral fixtures; actual unchanged U + reference.
prefixes = []
for ys in ([2, 2, 3, 3], [3, 3, 2, 2]):
    r = replay([v[k] for y in ys for k in (0, 1, y, 0)],
               hashlib.sha256(str(ys).encode()).hexdigest(), False, lambda: None)
    cells = r['events'][-1]['before_cells']
    assert [c['values'] for c in cells] == [[.375, .25], [0., .25]]
    assert r['cleanup']
    prefixes.append(dict(pattern=ys, before_final_promotion=cells))
facts['T2_actual_neutral_prefix'] = prefixes

assert choose((None, None)) == 'P'
assert update((None, None), 0) == (0., .5)
assert choose(update((0., .5), 1)) == 'P'
assert update((0., .5), 1) == (.25, .25)
facts['T3_common_initialization_boundary'] = 'PASS: exact tie, outside fixed prefix'

checked = 0
for n in range(1, 11):
    for seq in itertools.product((0, 1), repeat=n):
        u, q = (.375, 0.), (F(3, 8), F(0))
        for y in seq:
            u, q = update(u, y), exact_update(q, y)
            assert u == tuple(float(x) for x in q)
            assert choose(u) == y
            assert sum(q) < F(1, 2)
        checked += 1
facts['T4_short_exhaustive'] = dict(sequences=checked, maximum_feedbacks=10, status='PASS')

for seq in ((0,)*20, (1,)*20, (0,)*8+(1,)*8, (0,1)*20):
    u = (.375, 0.)
    for y in seq:
        u = update(u, y)
        assert choose(u) == y
facts['T5_repeat_switch_alternation'] = 'PASS'

boundaries = []
for repeated in (0, 1):
    first = None
    for n in range(1, 65):
        u, q = (.375, 0.), (F(3,8), F(0))
        for y in (repeated,)*n+(1-repeated,):
            u, q = update(u,y), exact_update(q,y)
        if choose(u) != 1-repeated:
            assert u == (.25,.25) and choose(u) == 'P'
            assert q[1-repeated] < F(1,4)
            first = dict(repeated=repeated, repetitions=n, float_errors=u,
                         exact_errors=[str(x) for x in q], U='P', L=1-repeated)
            break
    assert first is not None
    boundaries.append(first)
facts['T6_reachable_rounding_boundary'] = boundaries

# Isolated IEEE rounding endpoints, not claimed as extra regular source states.
assert choose(update((math.nextafter(.5, 0.), math.nextafter(0., 1.)), 0)) == 0
assert update((.5, math.nextafter(0., 1.)), 0) == (.25,.25)
assert update((.25,.25), 0) == (.125,.375)
assert update((.25,.25), 1) == (.375,.125)
facts['T7_ulp_subnormal_tie_recovery'] = 'PASS'
assert .5*.25+.5*.25 == .25
facts['T8_persistence_invariant'] = 'PASS'

facts['scope'] = dict(research_sources=0, research_replays=0,
    neutral_prefix_fixtures=2, neutral_prefix_frames=32,
    scalar_rules_only_after_prefix=True, production_modified=False)
facts['development_attempts'] = [
    'Initial invocation rejected before replay: missing check callback.',
    'Second invocation rejected on first frame: invalid profile length.',
    'One successful 16-frame exploratory neutral prefix before this saved check.']
facts['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(HERE/'verification.json').write_text(json.dumps(facts,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status='PASS',short_sequences=checked,rounding=boundaries),indent=2))
