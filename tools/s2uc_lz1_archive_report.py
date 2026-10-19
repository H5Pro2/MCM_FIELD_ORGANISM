"""Read-only assessment of the completed, sealed LZ1 run; no replay imports."""
import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'reports/s2uc/lz1-comparison-20261004-01'
OUT=ROOT/'reports/s2uc/lz1-assessment-20261004-01'

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def table(name,rows):
    with (OUT/name).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    closure=read(ARCHIVE/'closure.json')
    if closure['status']!='COMPLETE':raise ValueError('REQUIRES_COMPLETE_SEALED_RUN')
    for n,v in closure['files'].items():
        if sha(ARCHIVE/n)!=v['sha256'] or (ARCHIVE/n).stat().st_size!=v['bytes']:raise ValueError('ARCHIVE_CHANGED:'+n)
    OUT.mkdir(exist_ok=False)
    assessment=read(ARCHIVE/'assessment.json')
    plan=read(ROOT/'docs/S2UC_LZ1_V1_20261004_PLAN.json')
    targets=[];means=[];cycles=[];resources=[];case_summaries=[]
    for spec in plan['cases']:
        case=json.loads(gzip.decompress((ARCHIVE/(spec['id']+'-case.json.gz')).read_bytes()))
        assert case['complete'] and case['reference_equal'] and not case['neutral_only']
        assert [row['target'] for row in case['rows']]==plan['masks']['G']
        for row,u in zip(case['rows'],case['U']['rows'],strict=True):
            assert row['target']==u['target']
            h=u['selected']
            targets.append(dict(case=case['id'],replicate=case['replicate'],condition=case['condition'],
                target=row['target'],primary_Y=row['target'] in plan['masks']['G_Y'],
                P=row['P'],U=row['U'],H64=row['H64'],U_minus_P=row['U']-row['P'],
                U_minus_H64=row['U']-row['H64'],H64_prediction_catalog_id=row['H64_prediction'],
                U_original='' if h is None else h['original'],
                U_line='' if h is None else str(h['ordinals'])+':'+str(h['offset']),
                U_decision=u['reason'],H64_prior_count=row['H64_prior_count'],
                cumulative_U_minus_P=row['cumulative_differences']['U-P'],
                cumulative_U_minus_H64=row['cumulative_differences']['U-H64']))
        for mask,m in case['metrics'].items():
            means.append(dict(case=case['id'],replicate=case['replicate'],condition=case['condition'],
                mask=mask,count=len(plan['masks'][mask]),**m))
        cycles.append(dict(case=case['id'],condition=case['condition'],**case['cycle'],
            full_confirmations=len(case['U']['full_confirmations']),
            U_reference_advances=case['U']['reference_advances'],U_cleanup=case['U']['cleanup']))
        resources.append(case['resources'])
        case_summaries.append(dict(id=case['id'],condition=case['condition'],metrics=case['metrics']))
    assert len(targets)==49824 and sum(x['primary_Y'] for x in targets)==24576
    table('targets.csv',targets);table('case-mask-means.csv',means)
    save('cycles.json',cycles)
    contrasts=[dict(condition=x['condition'],mask=x['mask'],contrast=x['contrast'],primary=x['primary'],
        mean=x['mean'],ci_low=x['ci'][0],ci_high=x['ci'][1],level=x['level'],verdict=x['verdict']) for x in assessment['contrasts']]
    table('contrasts.csv',contrasts);table('harms.csv',assessment['harms'])
    group_means={c:{m:{a:sum(x['metrics'][m][a] for x in case_summaries if x['condition']==c)/32
        for a in ('P','U','H64')} for m in plan['masks']} for c in ('S','W','N')}
    primary=[x for x in assessment['contrasts'] if x['primary']]
    verdicts=dict(Technik='AUSWERTBAR',
        Information_H64='BELEGT_S_UND_W' if all(x['ci'][1]<0 for x in primary if x['contrast']=='H64-P') else 'NICHT_DURCHGAENGIG_NACHGEWIESEN',
        Nutzung_U='BELEGT_S_UND_W' if all(x['ci'][1]<0 for x in primary if x['contrast']=='U-P') else 'NICHT_DURCHGAENGIG_NACHGEWIESEN')
    comparison=[x for x in assessment['contrasts'] if x['mask']=='G_Y' and x['condition'] in ('S','W') and x['contrast']=='U-H64']
    verdicts['Vergleich_U_H64']='U_SCHLECHTER_S_UND_W_SEKUNDAER' if all(x['ci'][0]>0 for x in comparison) else 'SIEHE_KONTRASTE'
    facts=dict(status='SEALED_ARCHIVE_VERIFIED',archive_closure_sha256=sha(ARCHIVE/'closure.json'),
        prestart_sha256=sha(ROOT/'docs/S2UC_LZ1_V1_20261004_VORSTARTBINDUNG.json'),
        authorization_sha256=sha(ROOT/'docs/S2UC_LZ1_V1_20261004_AUTORISIERUNG.json'),
        verified_archive_files=len(closure['files']),counts=read(ARCHIVE/'worker-complete.json'),
        verdicts=verdicts,group_means=group_means,primary=primary,comparison=comparison,
        U_max={k:max(x['U'][k] for x in resources) for k in resources[0]['U']},
        H64_heap_max=max(x['H64_heap_peak'] for x in resources),H64_ring_bytes=73728,
        cycles={k:sum(x[k] for x in cycles) for k in ('targets','two_live_hypotheses','live_feedback','warm_hypotheses','selected','full_confirmations','U_reference_advances')},
        cleanup_all=all(x['U_cleanup'] for x in cycles),
        run_export_bytes=sum(p.stat().st_size for p in ARCHIVE.iterdir() if p.is_file()),
        preparation_bytes=closure['charged_previous_bytes'],supervisor_seconds=closure['elapsed_before_terminal_write'],
        one_shot_consumed=True,replays_by_report=0,script_sha256=sha(Path(__file__)))
    save('verification.json',facts)
    print(json.dumps({k:facts[k] for k in ('verdicts','primary','comparison','U_max','H64_heap_max','cycles','run_export_bytes','preparation_bytes','supervisor_seconds','archive_closure_sha256')},indent=2))
    print('SECONDARY',json.dumps([x for x in contrasts if x['mask'] in ('G_Y','G_skeleton','Y_129_160','Y_161_256') and not x['primary']],indent=2))

if __name__=='__main__':main()
