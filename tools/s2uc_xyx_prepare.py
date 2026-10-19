"""Separate fixed nonpersistent comparison; materialization only after authorization."""
import argparse
import io
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

from tools import s2uc_multi_qualification as prior
from tools._s2uc_xyx_assessment import assess
from tools._s2uc_bounded_audio import OutputLedger
from tools._s2uc_ema_stock_observer import digest

ROOT=prior.ROOT
PLAN=ROOT/'docs/S2UC_XYX_PLAN_20261003.json'
BINDING=ROOT/'docs/S2UC_XYX_BINDUNG_20261003.json'
TEMPLATE=ROOT/'docs/S2UC_XYX_AUTORISIERUNG_VORLAGE_20261003.json'
AUTH=ROOT/'docs/S2UC_XYX_AUTORISIERUNG_20261003.json'
CONTRACT=ROOT/'docs/S2UC_ZWEI_NICHTPERSISTENTE_FORTSETZUNGEN_GEGENPRUEFVERTRAG_20261003.txt'
QUAL=ROOT/'reports/s2uc/xyx-preparation-qualification-20261003-01'
OUT=ROOT/'reports/s2uc/xyx-counterprobe-20261003-01'
NEW=('tools/_s2uc_xyx_assessment.py','tools/s2uc_xyx_prepare.py','tests/test_s2uc_xyx_prepare.py')


def plan():
    p=prior.plan()
    p['recipes']['Y']=['3/16','5/16','9/16','15/16']
    p['masks']['S']=[11,15]
    p['output']=str(OUT.relative_to(ROOT)).replace('\\','/')
    p['comparison']='NONPERSISTENT_X_Y_X_V1'
    p['criteria']=dict(stable=[11,15],change=[27,31],return_targets=[43,47],
        availability=[23,27,31,35,39,43,47],deadlines=dict(change=27,return_phase=43),
        require='warm unique negative minimum, original key/successor, preceding phase feedback',
        net_H='U strictly below each M/E/K/P',total_G='U strictly below each M/E/K/P',
        first_losses=[19,35],expected_delay_loss=23)
    return p


def hashes():
    code=dict(prior.verify()['code'])
    code.update({name:prior.sha(ROOT/name) for name in NEW})
    return dict(sorted(code.items()))


def auth(status):
    return dict(status=status,action='RUN_NONPERSISTENT_XYX48_ONCE',plan_sha256=prior.sha(PLAN),
        binding_sha256=prior.sha(BINDING),output=plan()['output'],arms=plan()['arms'],frames=48)


def prepare():
    if AUTH.exists() or OUT.exists(): raise RuntimeError('ALREADY_AUTHORIZED_OR_CLAIMED')
    old_bytes=prior.check_qualification()
    prior.save(PLAN,plan())
    prior.save(BINDING,dict(code=hashes(),plan_sha256=prior.sha(PLAN),contract_sha256=prior.sha(CONTRACT),
        python=sys.version,python_executable_sha256=prior.sha(sys.executable),
        reused_qualification_bytes=old_bytes,reused_closure_sha256=prior.sha(prior.QUAL/'closure.json'),
        previous_binding_sha256=prior.sha(prior.BINDING)))
    prior.save(TEMPLATE,auth('PENDING_SEPARATE_AUTHORIZATION'))


def verify():
    if sys.flags.optimize: raise RuntimeError('OPTIMIZATION_FORBIDDEN')
    b=prior.read(BINDING)
    if b['code']!=hashes() or prior.read(PLAN)!=plan() or b['plan_sha256']!=prior.sha(PLAN): raise RuntimeError('XYX_BINDING')
    if b['contract_sha256']!=prior.sha(CONTRACT): raise RuntimeError('XYX_CONTRACT')
    if b['python']!=sys.version or b['python_executable_sha256']!=prior.sha(sys.executable): raise RuntimeError('XYX_RUNTIME')
    if b['reused_qualification_bytes']!=prior.check_qualification() or b['reused_closure_sha256']!=prior.sha(prior.QUAL/'closure.json'): raise RuntimeError('REUSED_QUALIFICATION')
    return b


def resource_report(results):
    out={}
    for arm,r in results.items():
        data=r['resources']
        if arm=='U':
            out[arm]=dict(packed_bytes=data['packed'],additional_python_peak=data['additional_python_peak'],
                controlled_original_frame_upper_bound=data['original_frames_upper_bound'],
                controlled_combined_upper_bound=data['combined_upper_bound'],output_slot_limit=2,
                measured_original_frame_peak=None,measured_combined_peak=None,
                note='Unpopulated tracing counters deliberately not reported as consumption.',
                receipt_bytes=data['receipt_bytes_peak'],utf8_upper=data['utf8_upper'])
        else:
            out[arm]=dict(data)
    return out


def _materialize():
    """Private supplier, reached only after verified authorization and exclusive claim."""
    spec=plan()
    return [(float(Fraction(x)),)*48 for block in spec['blocks'] for x in spec['recipes'][block]]


def validate_source(values):
    spec=plan()
    if len(values)!=48: raise RuntimeError('XYX_SOURCE_LENGTH')
    for i,v in enumerate(values):
        expected=float(Fraction(spec['recipes'][spec['blocks'][i//4]][i%4]))
        if len(v)!=48 or any(type(x) is not float or x!=expected for x in v): raise RuntimeError('XYX_SOURCE_RECIPE')


def _export(folder,supplier,prior_bytes,check):
    ledger=OutputLedger(folder)  # Claim before supplier.
    ledger.LIMIT-=prior_bytes
    results={}; partial={}; error=None
    try:
        ledger.write('claim.json',dict(plan=plan(),charged_previous_bytes=prior_bytes))
        values=supplier()
        validate_source(values)
        ledger.write('source.json',values)
        profile=digest(values)
        for arm in plan()['arms']:
            partial={}
            if arm=='U': r=prior.multi_replay(values,profile,count=48,evidence=partial)
            else: r=prior.old_replay(values,profile,count=48,arm=arm,evidence=partial)
            results[arm]=r; ledger.write(arm+'.json',r); partial={}
        evaluation=assess(results,values,plan())
        ledger.write('assessment.json',evaluation)
        ledger.write('resources.json',dict(arms=resource_report(results),reused_qualification_bytes=prior.check_qualification()))
        check()
        return evaluation
    except BaseException as exc:
        error=type(exc).__name__+':'+str(exc)
        if partial: ledger.write('partial.json',partial)
        raise
    finally:
        ledger.write('closure.json',dict(status='COMPLETE' if error is None else 'FAILED',error=error,
            completed_arms=list(results),charged_previous_bytes=prior_bytes,charged_before_closure=ledger.used,
            files={p.name:dict(bytes=p.stat().st_size,sha256=prior.sha(p)) for p in Path(folder).iterdir() if p.is_file()}),final=True)


def check_preparation():
    c=prior.read(QUAL/'closure.json')
    if c['status']!='PASS': raise RuntimeError('PREPARATION_NOT_PASS')
    for n,item in c['files'].items():
        if prior.sha(QUAL/n)!=item['sha256'] or (QUAL/n).stat().st_size!=item['bytes']: raise RuntimeError('PREPARATION_HASH')
    if prior.read(QUAL/'binding.json')!=verify(): raise RuntimeError('PREPARATION_BINDING')
    return sum(p.stat().st_size for p in QUAL.iterdir() if p.is_file())


def run(path):
    verify()
    if prior.read(Path(path))!=auth('AUTHORIZED_ONCE'): raise RuntimeError('XYX_EXPLICIT_AUTHORIZATION_REQUIRED')
    charged=prior.check_qualification()+check_preparation()
    return _export(OUT,_materialize,charged,verify)


def qualify():
    b=verify()
    if AUTH.exists() or OUT.exists(): raise RuntimeError('OPERATIVE_STATE_PRESENT')
    ledger=OutputLedger(QUAL); ledger.LIMIT-=b['reused_qualification_bytes']
    error=None; success=False
    try:
        ledger.write('binding.json',b)
        suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_xyx_prepare')
        ids=[t.id() for group in suite for t in group]
        stream=io.StringIO(); result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        success=result.wasSuccessful() and not result.skipped
        ledger.write('tests.json',dict(ids=ids,count=result.testsRun,success=success,failures=len(result.failures),
            errors=len(result.errors),skipped=len(result.skipped),output=stream.getvalue()))
        from tests.test_s2uc_xyx_prepare import FACTS
        ledger.write('facts.json',FACTS)
        ledger.write('source-snapshot.json',{n:(ROOT/n).read_text(encoding='utf-8') for n in NEW})
        ledger.write('plan.json',plan()); ledger.write('authorization-template.json',prior.read(TEMPLATE))
        verify()
        if not success: raise RuntimeError('PREPARATION_TEST_FAILURE')
        prior.write_text(ledger,'REPORT.md','\n'.join([
            '# Separate XYX-Laufvorbereitung neutral geprueft','',
            f'{result.testsRun}/{result.testsRun} PASS;0 Fehler/Fehlschlaege/Skips.',
            'Nur neue Vergleichsvorbereitung geprueft; keine Wiederholung der101 Policytests.',
            'Neue48er-Folge weder materialisiert noch ausgefuehrt. Kein Adapter-/Replayaufruf in den Neutraltests.',
            'Tests verwenden abstrakte Entscheidungsfixtures sowie gespeicherte alte Belege als Parserregression.',
            'AUSWAHL_X_Y_X,Nettonutzen H und Gesamtnutzen G getrennt; alle sieben Masken und Einzeldifferenzen.',
            'Originalordinalen,Keys und vorangehende Feedbackketten belegen Auswahl; Ticketreihenfolge ist keine Identitaet.',
            f'{len(b["code"])} Dateien gebunden; alle61 vorher gebundenen Dateien unveraendert.',
            f'Bindung SHA256:{prior.sha(BINDING)}',f'Plan SHA256:{prior.sha(PLAN)}',
            f'Wiederverwendete Qualifikation:{b["reused_qualification_bytes"]} Byte; neue Belege zusaetzlich in gemeinsamer4MiB-Bilanz.',
            '256KiB Abschlussreserve; Frameobergrenzen getrennt von Messpeaks,unbefuellte Zaehler ohne Verbrauchsaussage.',
            'Autorisierungsvorlage PENDING_SEPARATE_AUTHORIZATION; keine operative Einmalautorisierung.',
            'Vorbereiteter Aufruf: C:/Python314/python.exe -m tools.s2uc_xyx_prepare run --authorization docs/S2UC_XYX_AUTORISIERUNG_20261003.json',
            'Naechster Vorschlag: Vorbereitung abnehmen,dann separat ueber den einmaligen gebundenen Vergleich entscheiden.',
            'Unabhaengiger Evaluationsnutzen NICHT_GEPRUEFT;Defaults bleiben deaktiviert.','']))
    except BaseException as exc:
        error=type(exc).__name__+':'+str(exc); raise
    finally:
        ledger.write('closure.json',dict(status='PASS' if success and error is None else 'FAILED',error=error,
            reused_qualification_bytes=b['reused_qualification_bytes'],charged_before_closure=ledger.used,
            materialized_new_source=False,executed_new_comparison=False,policy_requalified=False,
            files={p.name:dict(bytes=p.stat().st_size,sha256=prior.sha(p)) for p in QUAL.iterdir() if p.is_file()}),final=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument('action',choices=('prepare','qualify','run'))
    p.add_argument('--authorization'); a=p.parse_args()
    if a.action=='prepare': prepare()
    elif a.action=='qualify': qualify()
    else:
        if not a.authorization: p.error('--authorization required')
        run(a.authorization)


if __name__=='__main__': main()
