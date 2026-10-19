"""Seal existing neutral evidence and immutable dependencies, never authorize research."""
import json
import sys
from pathlib import Path
from tools.s2uc_ura1_prepare_rev1 import ROOT, PREP, TARGET, AUTH, NAMESPACE, LIMITS, validate_binding, authorization
from tools.s2uc_ura1_runtime_qualify import sha, runtime
from tools._s2uc_ura1_fs_accounting_v4 import treebytes

BASE = ROOT/'reports/s2uc/ura1-v4-preparation-20261015-01/prestart.json'
BASE_SHA = 'deaae277655ecf078de791190e840d42b2f42fb113288fc903b54b49342ccee3'
MATRIX_SHA = '0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965'


def save(name, value):
    with (PREP/name).open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def main():
    if TARGET.exists() or AUTH.exists() or (PREP/'prestart.json').exists():
        raise PermissionError('EXCLUSIVE_PREPARATION_ONLY')
    if sha(BASE) != BASE_SHA:
        raise ValueError('INHERITED_PRESTART')
    base = json.loads(BASE.read_bytes())
    for name, digest in base['files'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('INHERITED_FILE_CHANGED:'+name)
    if sha(PREP/'bootstrap.bin') != MATRIX_SHA:
        raise ValueError('MATRIX_CHANGED')
    unit = json.loads((PREP/'unit-tests.json').read_bytes())
    if unit['status'] != 'PASS' or unit['tests'] != 18 or unit['errors'] or unit['failures'] or unit['skipped']:
        raise ValueError('UNIT_QUALIFICATION')
    complete = json.loads((PREP/'integration-complete/terminal.json').read_bytes())
    fault = json.loads((PREP/'integration-admin/terminal.json').read_bytes())
    if (complete['status'], complete['completed_cases'], complete['arms_created'], complete['distinct_arms']) != ('TERMINAL_COMPLETE',[1,2],4,4):
        raise ValueError('NEUTRAL_COMPLETENESS')
    if fault['status'] != 'TECHNICAL_ABORT' or 'budget:admin' not in fault['first_failure'] or fault['completed_cases'] != [1] or fault['active_case'] != 2:
        raise ValueError('NEUTRAL_BUDGET_ABORT')
    for terminal in (complete, fault):
        if terminal['research'] or terminal['cleanup'] != 'CONFIRMED' or not terminal['worker_ended'] or not terminal['file_cleanup_confirmed']:
            raise ValueError('NEUTRAL_CLEANUP')
        if terminal['job']['peak_job_committed_bytes'] >= LIMITS['job']:
            raise ValueError('NEUTRAL_MEMORY')
    closure = json.loads((PREP/'integration-complete/closure.json').read_bytes())
    for name, item in closure['files'].items():
        file = PREP/'integration-complete'/name
        if file.stat().st_size != item['bytes'] or sha(file) != item['sha256']:
            raise ValueError('INTEGRATION_CLOSURE:'+name)
    for number in (1,2):
        proof = json.loads((PREP/f'integration-complete/case-{number:02d}-continuity.json').read_bytes())
        if not proof['neutral_only'] or proof['integrity'] != 'PASS_DELTA_INTEGRITY':
            raise ValueError('CONTINUITY_INTEGRITY')
        a,b = proof['proofs']
        if a['state_sha256'] != b['state_sha256'] or [a['mode'],b['mode']] != ['U','R']:
            raise ValueError('CONTINUITY_PAIRED')
        for value in (a,b):
            if value['cells'] < 1 or value['boundary_after'] != 16 or value['frames'] != 32 or not all(value[k] for k in ('same_arm_and_bank','identical_state_at_next_entry','reference_feedback','cleanup')):
                raise ValueError('CONTINUITY_STATE')
    save('inheritance.json',dict(status='PASS', base_prestart=str(BASE.relative_to(ROOT)), base_sha256=BASE_SHA,
                                inherited_files=len(base['files']), all_inherited_hashes_equal=True,
                                unchanged_proof_scope=['U/R selection and feedback','stock/ticket/cell reference','archive codec and integrity',
                                                       'F01-F14 filesystem correction','terminal cleanup and cumulative resource accounting'],
                                fs_correction_sha256='a1bdca305b43ceba1e5755cd70557d1eec7b4b0b31352c0425d87902004face4',
                                matrix_sha256=MATRIX_SHA, historical_sources_reused=False))
    save('integration-verification.json',dict(status='PASS', tests={
        'G01':dict(result='PASS',scope='two 32-frame mirrored continuous U/R hand cases',policy_frames=128,
                   reference_equal=True,closure_hashes_equal=True,seconds=complete['seconds'],job=complete['job']),
        'G02':dict(result='PASS_EXPECTED_TECHNICAL_ABORT',scope='injected administration overflow on case 2',
                   completed_cases=[1],active_case=2,cleanup='CONFIRMED',worker_ended=True,
                   seconds=fault['seconds'],job=fault['job'])},
        full_1024_frame_execution=False,research_authorization_created=False))
    save('resource-plan.json',dict(limits=LIMITS, active_process_limit=2, maximum_research_stories=32, maximum_research_arms=64,
        historical_v4_global_plan_seconds=50531.048367999465, historical_v4_actual_seconds=6727.4106344,
        inherited_plan_reference='reports/s2uc/ura1-v4-preparation-20261015-01/resource-plan.json',
        history_is_not_rev1_measurement=True, rev1_full_series_duration_measured=False,
        source_cap_32_times_case_bytes=32*LIMITS['source_case'], archive_cap_32_times_gzip_bytes=32*LIMITS['gzip'],
        final_category_ceiling_bytes=sum(LIMITS[k] for k in ('preparation','source_total','archives','administration','closure')),
        note='No new large qualification. Same frames/arms and unchanged hard checks. Larger source draw metadata and more descriptive masks remain bounded; a new stock trajectory can still cause a technical abort. Temp files also count in total export.'))
    files=dict(base['files'])
    files[str(BASE.relative_to(ROOT)).replace('\\','/')]=BASE_SHA
    new_paths=list((ROOT/'tools').glob('*ura1_rev1*.py'))+[ROOT/'tools/s2uc_ura1_prepare_rev1.py',ROOT/'tests/test_s2uc_ura1_rev1.py',
               ROOT/'docs/S2UC_URA1_REV1_TRANSFER_KONZEPTVERTRAG_20261015.md']
    new_paths += [p for p in PREP.rglob('*') if p.is_file()]
    for path in new_paths:
        files[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path)
    if any(name in files for name in ('README.md','AKTUELLER_FORSCHUNGSWEG.md','docs/README.md')):
        raise ValueError('MUTABLE_OVERVIEW_BOUND')
    binding=PREP/'prestart.json'
    call=[sys.executable,'-m','tools.s2uc_ura1_prepare_rev1','run',str(binding),str(AUTH)]
    save('prestart.json',dict(version='URA1_REV1_NEUTRALLY_QUALIFIED',namespace=NAMESPACE,target=str(TARGET),limits=LIMITS,
                             runtime=runtime(),files=files,call=call,research_authorized=False,old_sources_reuse=False,
                             inherited_prestart_sha256=BASE_SHA,
                             authorization_schema=dict(kind='URA1_REV1_RESEARCH_ONCE',prestart_sha256='exact SHA256 of this prestart.json',allow_research=True)))
    digest=sha(binding)
    (PREP/'prestart.sha256').write_text(digest+'\n',encoding='ascii')
    validate_binding(binding)
    try:
        authorization(AUTH,digest)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError('NO_AUTHORIZATION_EXPECTED')
    size=treebytes(PREP)
    if size+4096>LIMITS['preparation']:
        raise ValueError('PREPARATION_LIMIT')
    receipt=dict(status='PASS',prestart_sha256=digest,bound_files=len(files),
         bound_dependency_bytes=sum((ROOT/name).stat().st_size for name in files),
         preparation_bytes_before_this_receipt=size,preparation_ceiling=LIMITS['preparation'],
         inherited_files_unchanged=len(base['files']),binding_validation=True,missing_authorization_rejected=True,
         target_absent=not TARGET.exists(),authorization_absent=not AUTH.exists(),call=call,
         note='This post-seal receipt and mutable overview files are outside prestart to avoid circular hashes.')
    receipt['preparation_bytes']=size
    for _ in range(8):
        total=size+len((json.dumps(receipt,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
        if receipt['preparation_bytes']==total:break
        receipt['preparation_bytes']=total
    save('seal-verification.json',receipt)
    print(json.dumps(dict(status='PASS',prestart_sha256=digest,bound_files=len(files),preparation_bytes=treebytes(PREP),call=call)))


if __name__ == '__main__': main()
