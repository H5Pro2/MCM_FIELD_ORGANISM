"""Read sealed A1 archives only; no policy imports, source generator or replay."""
import base64
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'reports/s2uc/a1-comparison-20261004-01'
OUT = ROOT / 'reports/s2uc/a1-selection-diagnosis-20261004-01'
EXPECTED = '85ef6239c3e3fc8e161284c9ffbe19ddbdcb06bc1201e73850f04862c807a769'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def save(name, value):
    with (OUT / name).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n')


def same(h, ordinals, offset):
    return h['ordinals'] == ordinals and h['offset'] == offset


def chain(case, ordinals, offset):
    report = read(ARCHIVE / (case + '-assessment.json'))
    arm = read(ARCHIVE / (case + '-A1.json'))
    cells = None
    feedback = []
    rows = []
    for index, row in enumerate(report['rows']):
        a = row['arms']['A1']
        h = next((x for x in a['hypotheses'] if same(x, ordinals, offset)), None)
        if h is None:
            continue
        t = row['target']
        assert h['before'] == cells
        assert h['prior_feedback'] == [x['at'] for x in feedback]
        assert all(x['at'] < t for x in feedback)
        update = next(x for x in a['updates'] if same(x, ordinals, offset))
        assert update['live']
        receipt_index = (t - 3) // 2
        receipt = arm['forecasts'][receipt_index]
        chosen = a['selected']
        selected = bool(chosen and same(chosen, ordinals, offset))
        item = dict(case=case, target=t, ordinals=ordinals, offset=offset,
            before_prediction=dict(available_through=t-1, original_successor=h['original'],
                cells=cells, margin=None if cells is None else cells[1]-cells[0],
                previous_feedback=list(feedback),
                prior_context_wins=sum(x['ec']<x['ep'] for x in feedback),
                prior_context_losses=sum(x['ec']>x['ep'] for x in feedback),
                prior_ties=sum(x['ec']==x['ep'] for x in feedback),
                competitors=[{k:x[k] for k in ('key','ordinals','offset','original','before','prior_feedback')} for x in a['hypotheses']],
                selected_this_line=selected, selected_original=None if chosen is None else chosen['original'],
                decision=a['reason'], receipt=receipt),
            after_target=dict(ec=update['ec'], ep=update['ep'], actual_match=h['actual_match'],
                modal_match=h['modal_match'], U_error=row['arms']['U']['error'], A1_error=a['error'], delta=row['delta']),
            evidence=dict(assessment=f'{case}-assessment.json#/rows/{index}',
                receipt=f'{case}-A1.json#/forecasts/{receipt_index}'))
        rows.append(item)
        cells = [update['ec'], update['ep']] if cells is None else [
            .5*cells[0]+.5*update['ec'], .5*cells[1]+.5*update['ep']]
        feedback.append(dict(at=t, ec=update['ec'], ep=update['ep'], cells_after=cells,
            evidence=f'{case}-assessment.json#/rows/{index}/arms/A1/updates'))
        item['after_target']['cells_after'] = cells
    return rows


def main():
    assert sha(ARCHIVE / 'closure.json') == EXPECTED
    closure = read(ARCHIVE / 'closure.json')
    for name, value in closure['files'].items():
        p = ARCHIVE / name
        assert sha(p) == value['sha256'] and p.stat().st_size == value['bytes']
    assert not OUT.exists()
    OUT.mkdir()
    chains = {case:chain(case, ordinals, 0) for case, ordinals in (
        ('T1-1-3',[1,2,3,4]), ('F7',[1,2,3,4]), ('F3',[1,2,3,4]), ('F4',[13,14,15,16]))}
    extra = []
    for path in sorted(ARCHIVE.glob('T1-*-assessment.json')):
        case = read(path)
        for i, row in enumerate(case['rows']):
            for h in row['gained_warm']:
                history = chain(case['id'], h['ordinals'], h['offset'])
                entry = next(x for x in history if x['target']==row['target'])
                extra.append(entry)
    assert len(extra)==5
    f7 = chains['F7']
    selected = [x for x in f7 if x['before_prediction']['selected_this_line']]
    assert len(f7)==15 and len(selected)==10
    assert sum(x['after_target']['delta']<0 for x in selected)==8
    assert sum(x['after_target']['delta']>0 for x in selected)==2
    # Compare bytes already stored in the run archive, without generating,
    # restoring or writing any source. Ten complete 48-wide Float64 frames.
    stored = {c:read(ARCHIVE/(c+'-source.json'))['values'] for c in ('F3','F7')}
    assert all(v['width']==48 and v['encoding']=='FLOAT64_LE_BASE64' for v in stored.values())
    data = {c:base64.b64decode(v['data'], validate=True) for c,v in stored.items()}
    assert data['F3'][:10*48*8] == data['F7'][:10*48*8]
    assert data['F3'][10*48*8:11*48*8] != data['F7'][10*48*8:11*48*8]
    records = {c:read(ARCHIVE/(c+'-A1.json')) for c in ('F3','F7')}
    normalized = {c:[{k:v for k,v in f.items() if k!='profile'} for f in a['forecasts'][:5]] for c,a in records.items()}
    assert normalized['F3']==normalized['F7']
    assert records['F3']['rows'][:4]==records['F7']['rows'][:4]
    assert records['F3']['events'][:10]==records['F7']['events'][:10]
    collision=dict(cases=['F3','F7'],prediction_target=11,identical_observed_frames=10,
        prefix_bytes=3840,prefix_sha256=hashlib.sha256(data['F3'][:3840]).hexdigest(),
        receipts_equal_except_profile=True,prior_feedback_rows_equal=True,stock_events_equal=True,
        first_target_bytes_different=True,
        exception='Profiles are distinct whole-story scope digests, not semantic or permitted forecasting features.',
        F3_delta=next(x for x in chains['F3'] if x['target']==11)['after_target']['delta'],
        F7_delta=next(x for x in chains['F7'] if x['target']==11)['after_target']['delta'])
    save('chains.json',chains)
    save('t1-extra-five.json',extra)
    save('indistinguishable-prefix.json',collision)
    decisions = [x for case,rows in chains.items() for x in rows if
        case=='F7' or (case=='T1-1-3' and x['target']==17) or
        (case in ('F3','F4') and x['after_target']['delta']>0)]
    flat=[]
    for x in decisions:
        b=x['before_prediction'];a=x['after_target'];cells=b['cells']
        flat.append(dict(case=x['case'],target=x['target'],original=b['original_successor'],
            pre_Ec=None if cells is None else cells[0],pre_Ep=None if cells is None else cells[1],
            pre_feedback_targets=','.join(str(f['at']) for f in b['previous_feedback']),
            pre_wins=b['prior_context_wins'],pre_losses=b['prior_context_losses'],
            selected_this_line=b['selected_this_line'],selected_original=b['selected_original'],decision=b['decision'],
            post_ec=a['ec'],post_ep=a['ep'],post_actual=a['actual_match'],post_modal=a['modal_match'],
            post_delta=a['delta'],evidence=x['evidence']['assessment']))
    with (OUT/'decisions.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    save('verification.json',dict(status='PASS_ARCHIVE_DIAGNOSIS',archive_closure_sha256=EXPECTED,
        verified_archive_files=len(closure['files']),chains={c:len(v) for c,v in chains.items()},
        F7_selected=10,F7_selected_gain=8,F7_selected_harm=2,F7_selected_equal=0,
        extra_T1_occurrences=5,decision_table_rows=len(flat),
        checks=['archive hashes','causal feedback cutoff','EMA arithmetic against stored cells',
                'all five T1 extras','all F7 line decisions','F3/F7 exact archived prefix and state collision'],
        replays=0,source_materializations=0,policy_changes=0,threshold_searches=0,
        script_sha256=sha(Path(__file__))))
    print(json.dumps(collision,indent=2))


if __name__=='__main__':
    main()
