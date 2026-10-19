"""Neutral qualification and separately authorized, exclusively claimed comparison."""
import argparse
import ast
import io
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

from tools.s2uc_factor_material import ROOT, sha, read
from tools.s2uc_promotion_qualification import verify as verify_previous
from tools._s2uc_bounded_audio import OutputLedger
from tools._s2uc_multi_observer import replay as multi_replay
from tools._s2uc_promotion_replay import replay as old_replay
from tools._s2uc_ema_stock_observer import digest

PLAN = ROOT/'docs/S2UC_MULTI_PLAN_20261003.json'
BINDING = ROOT/'docs/S2UC_MULTI_BINDUNG_20261003.json'
TEMPLATE = ROOT/'docs/S2UC_MULTI_AUTORISIERUNG_VORLAGE_20261003.json'
AUTH = ROOT/'docs/S2UC_MULTI_AUTORISIERUNG_20261003.json'
CONTRACT = ROOT/'docs/S2UC_MEHRHYPOTHESEN_FEHLERBEWERTUNG_VERTRAG_20261003.txt'
QUAL = ROOT/'reports/s2uc/multi-neutral-qualification-20261003-01'
OUT = ROOT/'reports/s2uc/multi-counterprobe-20261003-01'
NEW = ['tools/_s2uc_multi_error.py', 'tools/_s2uc_multi_observer.py',
       'tools/s2uc_multi_qualification.py', 'tests/test_s2uc_multi_error.py', 'tests/test_s2uc_multi_runner.py']
SUITES = ['tests.test_s2uc_multi_error', 'tests.test_s2uc_multi_runner',
          'tests.test_s2uc_paired_error_ema', 'tests.test_s2uc_promotion_ema',
          'tests.test_s2uc_promotion_runner', 'tests.test_s2uc_ema_stock',
          'tests.test_s2uc_pair_context_adapter', 'tests.test_s2uc_continuation_adapter',
          'tests.test_s2uc_factor_recency', 'tests.test_s2uc_signal_approx']


def plan():
    g = list(range(3, 48, 2)); h = list(range(7, 48, 4))
    return dict(status='BOUND_NOT_AUTHORIZED', frames=48, arms=['U', 'M', 'E', 'K', 'P'],
        recipes=dict(X=['3/16', '5/16', '13/16', '15/16'], Y=['3/16', '5/16', '5/16', '15/16']),
        blocks=['X']*4+['Y']*4+['X']*4,
        masks=dict(G=g, H=h, N=[t for t in g if t not in h], F=[19,35], A_W=[23,27,31], A_R=[39,43,47]),
        policy='multi_error_exact_v1', alpha='1/2', metric='mae48',
        experimental_admissions=240, internal_reference_advances=240,
        limits=dict(packed=416, frames=18, outputs=2, combined=20, additional_python=16384,
                    receipt=16384, utf8=32768, export=4194304, reserve=262144),
        output=str(OUT.relative_to(ROOT)).replace('\\', '/'), independent_evaluation='NOT_TESTED')


def hashes():
    found = set(); pending = list(verify_previous()['code'])+NEW+[n.replace('.', '/')+'.py' for n in SUITES]
    while pending:
        name = pending.pop()
        if name in found: continue
        found.add(name)
        for node in ast.walk(ast.parse((ROOT/name).read_text(encoding='utf-8'))):
            modules = []
            if isinstance(node, ast.Import): modules = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]+[node.module+'.'+a.name for a in node.names]
            for module in modules:
                path = module.replace('.', '/')+'.py'
                if module.startswith(('tools.', 'tests.', 'mcm_field_organism.')) and (ROOT/path).is_file(): pending.append(path)
    return {p: sha(ROOT/p) for p in sorted(found)}


def save(path, value):
    with path.open('x', encoding='utf-8') as f: json.dump(value, f, indent=2, allow_nan=False)


def write_text(ledger, name, content):
    raw = content.encode('utf-8')
    if ledger.used+len(raw) > ledger.LIMIT-ledger.RESERVE: raise RuntimeError('OUTPUT_LIMIT')
    ledger.used += len(raw)
    with (ledger.folder/name).open('xb') as f:
        if f.write(raw) != len(raw): raise RuntimeError('SHORT_WRITE')


def authorization(status):
    return dict(status=status, action='RUN_MULTI_48_ONCE', plan_sha256=sha(PLAN), binding_sha256=sha(BINDING),
                output=plan()['output'], arms=plan()['arms'], frames=48)


def prepare():
    if OUT.exists() or AUTH.exists(): raise RuntimeError('ALREADY_AUTHORIZED_OR_CLAIMED')
    save(PLAN, plan())
    save(BINDING, dict(code=hashes(), plan_sha256=sha(PLAN), contract_sha256=sha(CONTRACT),
        python=sys.version, python_executable_sha256=sha(sys.executable), previous_binding_sha256=sha(ROOT/'docs/S2UC_PROMOTION_BINDUNG_20261003.json')))
    save(TEMPLATE, authorization('PENDING_SEPARATE_AUTHORIZATION'))


def verify():
    if sys.flags.optimize: raise RuntimeError('OPTIMIZATION_FORBIDDEN')
    b = read(BINDING)
    if b['code'] != hashes() or read(PLAN) != plan() or b['plan_sha256'] != sha(PLAN): raise RuntimeError('MULTI_BINDING')
    if b['contract_sha256'] != sha(CONTRACT): raise RuntimeError('MULTI_CONTRACT')
    if b['python'] != sys.version or b['python_executable_sha256'] != sha(sys.executable): raise RuntimeError('MULTI_RUNTIME')
    return b


def qualify():
    binding = verify()
    if AUTH.exists() or OUT.exists(): raise RuntimeError('COMPARISON_ALREADY_OPEN')
    ledger = OutputLedger(QUAL)
    stream = io.StringIO(); error = None; success = False
    try:
        ledger.write('binding.json', binding)
        suite = unittest.defaultTestLoader.loadTestsFromNames(SUITES)
        def ids(s):
            for t in s:
                if isinstance(t, unittest.TestSuite): yield from ids(t)
                else: yield t.id()
        names = list(ids(suite))
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        success = result.wasSuccessful() and not result.skipped
        from tests.test_s2uc_multi_error import FACTS
        from tests.test_s2uc_multi_runner import FACTS as RUNNER_FACTS
        FACTS['R2']['additional_python_peak'] = max(x['total'] for x in FACTS['heap'])
        FACTS['R2']['receipt_bytes'] = FACTS['receipt_max']
        FACTS['R2']['transient_utf8_upper'] = 2*FACTS['receipt_max']
        if FACTS['R2']['additional_python_peak'] > 16384: raise RuntimeError('RESOURCE_QUALIFICATION_FAILED')
        ledger.write('tests.json', dict(ids=names, count=result.testsRun, failures=len(result.failures),
                     errors=len(result.errors), skipped=len(result.skipped), success=success, output=stream.getvalue()))
        ledger.write('facts.json', FACTS)
        ledger.write('runner-facts.json', RUNNER_FACTS)
        ledger.write('bound-source.json', {name: (ROOT/name).read_text(encoding='utf-8') for name in binding['code']})
        verify()
        if not success: raise RuntimeError('QUALIFICATION_FAILED')
        frame_peak = max(x['frames'] for x in FACTS['R2_frames'])
        slots = max(x['slots'] for x in FACTS['R2_frames'])
        combined = max(x['combined'] for x in FACTS['R2_frames'])
        overall_heap = max(FACTS['R2']['additional_python_peak'], RUNNER_FACTS['Q1']['resources']['additional_python_peak'])
        report = '\n'.join([
            '# MCM-KI: multi_error_exact_v1 neutral qualifiziert', '',
            f'{result.testsRun}/{result.testsRun} PASS; keine Fehler, Fehlschlaege oder Skips.',
            'T1-T11, R1-R2 und Q1-Q6 sowie betroffene bestehende Regressionen; genaue IDs in tests.json.',
            '44 Unterbrechungspunkte der Fehlerpublikation und drei Promotionsunterbrechungen geprueft.',
            'Alle berechtigten Alternativen bewertet; Herkunft und Prognoseentscheidung getrennt.',
            'Kalte, gleiche, fehlende und erfahrungsbedingt schlechtere Alternativen in facts.json getrennt.', '',
            f'Gepackter Speicher:416/416 Byte inklusive Staging. Python-Zusatzpeak:{overall_heap}/16384 Byte.',
            f'Originalframe-Peak:{frame_peak}/18; Ausgabeplaetze:{slots}/2; gemeinsam:{combined}/20.',
            f'Receipt:{FACTS["R2"]["receipt_bytes"]}/16384 Byte; UTF8-Obergrenze:{FACTS["R2"]["transient_utf8_upper"]}/32768 Byte.',
            'Heapmessung umfasst komplette Systemaufrufe inklusive Scan, Serialisierung, Promotion und Fehlerbereinigung.',
            'Originalpayloads haben getrennte Framebilanz; alle neuen Halter/Metadaten und Systemtransienten sind mitgemessen.',
            'Frame-Tracing erfolgte in getrennten technischen Messungen, ohne dessen Beobachterallokationen dem System zuzurechnen.',
            'Kein Prozess-RAM-Beleg.', '',
            f'Gebunden:{len(binding["code"])} Dateien, Plan, Vertrag und Python-Laufzeit.',
            f'Bindungs-SHA256:{sha(BINDING)}', f'Plan-SHA256:{sha(PLAN)}',
            'Alle51 vorher gebundenen Dateien unveraendert. Neuer Code ausschliesslich in fuenf neuen Dateien.',
            'Gebundene Quellen als bound-source.json erhalten; Hashpruefung vor und nach Qualifikation.', '',
            'Unabhaengige neutrale12er-Folge in U/M/E/K/P:60 Arm-Aufnahmen+60 Referenzfortschreibungen.',
            'Weitere begrenzte technische Fixtures/Regressionen sind Testaufnahmen,kein fachlicher48er-Kontrast.',
            'Der48er-Kontrast wurde weder erzeugt noch ausgefuehrt. Kein Lernnutzenbeleg aus technischen Fixtures.',
            'Autorisierungsvorlage bleibt PENDING_SEPARATE_AUTHORIZATION; keine operative Autorisierung.',
            'Defaults deaktiviert; alte Standardpfade unveraendert.', '',
            'Naechster Vorschlag: technische Abnahme,dann separate Entscheidung ueber einmaligen gebundenen48er-Vergleich.',
            'Vorbereiteter Aufruf: C:/Python314/python.exe -m tools.s2uc_multi_qualification compare --authorization docs/S2UC_MULTI_AUTORISIERUNG_20261003.json',
            'Exportbilanz einschliesslich dieses Berichts in closure.json;4MiB-Grenze und256KiB-Reserve gelten gemeinsam mit spaeterem Vergleich.', ''
        ])
        write_text(ledger,'REPORT.md',report)
    except BaseException as exc:
        error = type(exc).__name__+':'+str(exc)
        raise
    finally:
        files = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in QUAL.iterdir() if p.is_file()}
        ledger.write('closure.json', dict(status='PASS' if success and error is None else 'FAILED',
            error=error, files=files, charged_before_closure=ledger.used, no_48_source_generated=True,
            comparison_executed=False, independent_evaluation='NOT_TESTED'), final=True)


def check_qualification():
    c = read(QUAL/'closure.json')
    if c['status'] != 'PASS': raise RuntimeError('QUALIFICATION_NOT_PASS')
    for name, item in c['files'].items():
        if sha(QUAL/name) != item['sha256'] or (QUAL/name).stat().st_size != item['bytes']: raise RuntimeError('QUALIFICATION_HASH')
    if read(QUAL/'binding.json') != verify(): raise RuntimeError('QUALIFICATION_BINDING')
    return sum(p.stat().st_size for p in QUAL.iterdir() if p.is_file())


def assess(results, masks):
    rows = {a: {r['target']: r for r in result['rows']} for a, result in results.items()}
    technical = []
    for a, r in results.items():
        if sorted(rows[a]) != masks['G'] or not r['slots_released'] or r['censored_target'] != max(masks['G'])+2:
            technical.append(a+':TARGET_OR_RELEASE')
    states = {digest(r['states'] if a == 'U' else r['state_hashes']) for a, r in results.items()}
    if len(states) != 1: technical.append('MEMORY_STATES')
    metrics = {}
    for m, targets in masks.items():
        metrics[m] = {}
        for a in rows:
            missing = [t for t in targets if t not in rows[a]]
            total = None if missing else sum(rows[a][t]['selected_mae'] for t in targets)
            metrics[m][a] = dict(missing=missing, count=len(targets)-len(missing),
                                 error_sum=total, mae=None if total is None else total/len(targets))
    return dict(technical_errors=technical, metrics=metrics,
        comparisons=[dict(target=t, errors={a: rows[a][t]['selected_mae'] for a in rows},
                         U_minus={a: rows['U'][t]['selected_mae']-rows[a][t]['selected_mae'] for a in rows if a != 'U'})
                     for t in masks['G'] if all(t in rows[a] for a in rows)],
        adaptation='REQUIRES_TICKET_AND_PHASE_FEEDBACK_ASSESSMENT' if not technical else 'NOT_EVALUABLE',
        independent_evaluation='NOT_TESTED')


def export(folder, spec, source_factory, *, prior_bytes=0, check=None):
    ledger = OutputLedger(folder)  # Exclusive claim BEFORE calling any source factory.
    ledger.LIMIT -= prior_bytes
    results = {}; partial = {}; error = None
    try:
        ledger.write('claim.json', dict(spec=spec, prior_bytes=prior_bytes))
        values = source_factory()
        ledger.write('source.json', values)
        profile = digest(values)
        for arm in spec['arms']:
            partial = {}
            if arm == 'U': result = multi_replay(values, profile, count=spec['frames'], evidence=partial)
            else: result = old_replay(values, profile, count=spec['frames'], arm=arm, evidence=partial)
            ledger.write(arm+'.json', result); results[arm] = result; partial = {}
        ledger.write('assessment.json', assess(results, spec['masks']))
        if check: check()
        return results
    except BaseException as exc:
        error = type(exc).__name__+':'+str(exc)
        if partial: ledger.write('partial.json', partial)
        raise
    finally:
        ledger.write('closure.json', dict(status='COMPLETE' if error is None else 'FAILED', error=error,
            completed_arms=list(results), charged_before_closure=ledger.used,
            files={p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in Path(folder).iterdir() if p.is_file()}), final=True)


def compare(path):
    verify()
    if read(Path(path)) != authorization('AUTHORIZED_ONCE'): raise RuntimeError('EXPLICIT_AUTHORIZATION_REQUIRED')
    prior = check_qualification()
    spec = plan()
    def material():
        return [(float(Fraction(x)),)*48 for block in spec['blocks'] for x in spec['recipes'][block]]
    export(OUT, spec, material, prior_bytes=prior, check=verify)
    verify()


def main():
    p = argparse.ArgumentParser(); p.add_argument('action', choices=('prepare', 'qualify', 'compare'))
    p.add_argument('--authorization'); args = p.parse_args()
    if args.action == 'prepare': prepare()
    elif args.action == 'qualify': qualify()
    else:
        if not args.authorization: p.error('--authorization required')
        compare(args.authorization)


if __name__ == '__main__': main()
