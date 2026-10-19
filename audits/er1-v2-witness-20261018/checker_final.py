"""Archive evidence audit; no policy, observer or original witness imports."""
import json
import struct
from collections import Counter, defaultdict

def require(ok, code):
    if not ok:
        raise ValueError(code)

def key(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'))

def compact(stock, source):
    result = {}
    for role in ('retained', 'candidate'):
        items = stock['retained'] if role == 'retained' else ([stock['candidate']] if stock['candidate'] else [])
        result[role] = []
        for item in items:
            ids = item['ordinals']
            require(len(ids) == 4 and ids == list(range(ids[0], ids[0]+4)), 'ORIGIN_SHAPE')
            require(item['values'] == [source[i-1] for i in ids], 'ORIGIN_VALUES')
            result[role].append((tuple(ids), item['generation']))
    result['marks'] = {int(k): v for k, v in stock['observation_end'].items()}
    return result

def cells(bank):
    b = bytes.fromhex(bank)
    require(len(b) == 416, 'BANK_SIZE')
    result = {}
    for i in range(6):
        gen, ec, ep, role, off, quality, valid = struct.unpack_from('<QddBBBB4x', b, i*32)
        if valid:
            require((role, gen, off) not in result, 'DUPLICATE_CELL')
            result[(role, gen, off)] = (ec, ep)
    return result

def project(reader, arm, source, checkpoint):
    def records(name):
        for data in reader.records(arm[name]['$sequence']):
            checkpoint()
            yield json.loads(data)
    frames = {0: dict(retained=[], candidate=[], marks={})}
    banks = {}; feedback = {}
    for event in records('events'):
        stage = event['stage']; state = event['state']; i = state['accepted']
        if stage == 'perception:after':
            require(i not in banks, 'DUPLICATE_FRAME')
            frames[i] = compact(state['stock'], source)
            banks[i] = cells(state['bank'])
        elif stage == 'feedback:after':
            require(i+1 not in feedback, 'DUPLICATE_FEEDBACK')
            feedback[i+1] = cells(state['bank'])
    require(set(frames) == set(range(len(source)+1)), 'FRAME_COMPLETENESS')
    rows = {x['target']: x for x in records('rows')}
    require(set(rows) == set(range(3, len(source), 2)), 'TARGET_COMPLETENESS')
    history = defaultdict(list); targets = {}; forecast_count = 0
    for f in records('forecasts'):
        forecast_count += 1
        target = f['index']+1
        if target not in rows:
            require(target == len(source)+1, 'UNEXPECTED_CENSOR')
            continue
        require(target not in targets and target in feedback, 'FORECAST_COMPLETENESS')
        row = rows[target]; receipt = f['receipt']; selected = f['selected']
        require(len(receipt['matches']) == len(receipt['hypotheses']), 'HYPOTHESIS_COUNT')
        hypotheses = {}; chosen = None
        for m, h in zip(receipt['matches'], receipt['hypotheses']):
            if not h['eligible']:
                continue
            origin = tuple(m['ordinals']); off = m['offset']
            role = 0 if m['role'] == 'retained' else 1
            k = (role, m['generation'], off)
            require((origin, m['generation']) in frames[f['index']][m['role']], 'MATCH_ORIGIN')
            require(off in (0, 1) and off+2 < len(origin), 'OFFSET')
            actual = banks[f['index']].get(k)
            require(actual == (h['ec'], h['ep']) if h['ec'] is not None else actual is None, 'WARM_CELL')
            require(k not in hypotheses, 'DUPLICATE_HYPOTHESIS')
            hypotheses[k] = (origin, off)
            if selected is not None and tuple(selected) == k:
                require(chosen is None, 'MULTIPLE_SELECTION')
                require(f['output'] == source[origin[off+2]-1], 'SELECTED_OUTPUT')
                chosen = dict(origin=origin, generation=m['generation'], offset=off,
                              warm=h['ec'] is not None, prior=list(history[(origin, off)]))
        require((selected is None) == (chosen is None), 'SELECTED_MATCH')
        error = sum(abs(a-b) for a,b in zip(f['output'], source[target-1], strict=True))/len(f['output'])
        require(error == row['error'], 'OBSERVED_ERROR')
        targets[target] = dict(chosen=chosen, output=f['output'], error=error)
        seen = set()
        for u in row['updates']:
            k = tuple(u['key']); require(k in hypotheses and k not in seen, 'FEEDBACK_KEY'); seen.add(k)
            origin, off = hypotheses[k]
            require(u['original'] == origin[off+2], 'FEEDBACK_OFFSET')
            if u['live']:
                require(k in feedback[target], 'LIVE_FEEDBACK_CELL')
                require((origin,k[1]) in frames[target-1]['retained' if k[0]==0 else 'candidate'], 'LIVE_FEEDBACK_ORIGIN')
                history[(origin, off)].append(target)
        require(seen == set(hypotheses), 'FEEDBACK_COMPLETENESS')
    require(forecast_count == len(source)//2 and set(targets)==set(rows), 'FORECAST_COUNT')
    return dict(frames=frames, targets=targets)

def reconstruct(data, source):
    """Enumerate candidates from raw stock transitions, never from reported witnesses."""
    expected = []; rejected = []
    for name, opponent in (('E','F'),('F','E')):
        a = data[name]; b = data[opponent]
        for end in range(4, len(source)+1, 4):
            old = a['frames'][end-4]; new = a['frames'][end]
            before = b['frames'][end-4]['retained']; after = b['frames'][end]['retained']
            lost = [x for x in before if x not in after]
            removed = [list(x[0]) for x in old['retained'] if x not in new['retained']]
            for identity, generation in old['retained']:
                if (identity,generation) not in new['retained'] or not any(x[0]==identity for x in lost):
                    continue
                require(generation in old['marks'], 'MISSING_ENDMARK')
                last = old['marks'][generation]
                intervening = [i for i in range(last+4,end,4) if source[i-4:i] != [source[j-1] for j in identity]]
                if not intervening:
                    continue
                # Competition requires a promotion in the arm that loses the origin.
                # The keeper may only confirm its different stock (contract section 4).
                if not any(x not in before for x in after):
                    rejected.append(dict(keeper=name,origin=list(identity),promotion_end=end,reason='NO_COMPETITION_PROMOTION'))
                    continue
                if any((identity,generation) not in a['frames'][i]['retained'] for i in range(last,end+1)):
                    rejected.append(dict(keeper=name,origin=list(identity),promotion_end=end,reason='BROKEN_ORIGIN'))
                    continue
                base=dict(keeper=name,origin=list(identity),promotion_end=end,last_observation=last,
                          unequal_blocks=intervening,other_victim=list(identity),keeper_victims=removed,
                          newer_keeper_victims=[v for v in removed if v[0]>identity[0]])
                expected.append(base|dict(stage='retention'))
                for target, observation in a['targets'].items():
                    chosen=observation['chosen']
                    if target<=end or chosen is None or chosen['origin']!=identity or not chosen['warm']:
                        continue
                    prior=[i for i in chosen['prior'] if i<end and i<target-1 and all(
                        (identity,generation) in a['frames'][j]['retained']+a['frames'][j]['candidate']
                        for j in range(i-1,target))]
                    if not prior:
                        continue
                    if any((identity,generation) not in a['frames'][i]['retained'] for i in range(end,target)):
                        continue
                    expected.append(base|dict(stage='warm_use',offset=chosen['offset'],prior_live_feedback=prior,
                        target=target,output=observation['output'],keeper_error=observation['error'],
                        other_error=b['targets'][target]['error'],local_gain=observation['error']<b['targets'][target]['error']))
    return expected, rejected

def compare(expected, reported):
    a=Counter(map(key,expected));b=Counter(map(key,reported))
    return dict(missing=[json.loads(k) for k in (a-b).elements()],
                unsupported=[json.loads(k) for k in (b-a).elements()],
                duplicate_records=[dict(record=json.loads(k),count=n) for k,n in b.items() if n>1])

def counts(records):
    result={}
    for arm in ('E','F'):
        r=[x for x in records if x['keeper']==arm];w=[x for x in r if x['stage']=='warm_use']
        targets=Counter(x['target'] for x in w)
        result[arm]=dict(retention_events=sum(x['stage']=='retention' for x in r),warm_uses=len(w),
            local_gains=sum(x['local_gain'] for x in w),unique_warm_targets=len(targets),
            unique_gain_targets=len({x['target'] for x in w if x['local_gain']}),
            multi_assigned_targets={str(k):v for k,v in targets.items() if v>1})
    return result
