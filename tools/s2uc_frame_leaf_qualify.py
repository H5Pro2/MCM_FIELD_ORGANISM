"""Bound and supervised neutral qualification of only Frame-leaf visitor v1."""
import argparse
import io
import json
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
from tools import s2uc_runtime_audit as audit
from tools._s2uc_frame_leaf_observer_v1 import FrameLeafBudgetObserver
from tools.s2uc_context_prediction_check import BudgetObserver

ROOT=audit.ROOT
PLAN=ROOT/'docs/S2UC_FRAME_BLATT_V1_PLAN_20261003.txt'
BINDING=ROOT/'docs/S2UC_FRAME_BLATT_V1_BINDUNG_20261003.json'
OUT=ROOT/'reports/s2uc/frame-leaf-qualification-20261003-01'
FILES=('tools/_s2uc_frame_leaf_observer_v1.py','tools/s2uc_frame_leaf_qualify.py','tests/test_s2uc_frame_leaf_observer.py')
LIMIT=16*1048576
OLD=BudgetObserver.trace


def spec():return dict(fixtures=['N1','N2'],arms=list(audit.ARMS),orders={'N1':['OLD','NEW'],'N2':['NEW','OLD']},replays=16,frames=80,admissions=1280,reference_advances=1280,trace=True,seconds=900,bytes=LIMIT)


def history():
    paths=[audit.BINDING,audit.PLAN]
    for folder in (audit.OUT,ROOT/'reports/s2uc/runtime-neutral-audit-assessment-20261003-01'):
        paths.extend(p for p in folder.iterdir() if p.is_file())
    return {p.relative_to(ROOT).as_posix():audit.frozen.sha(p) for p in paths}


def prepare():
    previous=audit.verify()
    audit.frozen.save(BINDING,dict(plan=audit.frozen.sha(PLAN),code={n:audit.frozen.sha(ROOT/n) for n in FILES},
        previous_code=previous['previous_code'],audit_binding=audit.frozen.sha(audit.BINDING),history=history(),spec=spec()))


def verify():
    b=audit.frozen.read(BINDING);previous=audit.verify()
    assert b['plan']==audit.frozen.sha(PLAN) and b['spec']==spec()
    assert b['code']=={n:audit.frozen.sha(ROOT/n) for n in FILES}
    assert b['previous_code']==previous['previous_code'] and b['history']==history()
    assert b['audit_binding']==audit.frozen.sha(audit.BINDING)
    return b


def save(name,value):
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    used=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())
    if used+len(raw)+65536>LIMIT:raise RuntimeError('EXPORT_LIMIT')
    with (OUT/name).open('xb') as f:f.write(raw)


def canonical(r):return json.dumps(audit.semantic(r),sort_keys=True,separators=(',',':'),allow_nan=False)


def matrix(deadline):
    def check():
        if time.monotonic_ns()>=deadline:raise TimeoutError('VISITOR_MATRIX_DEADLINE')
    rows=[];pairs=[]
    try:
        for case in spec()['fixtures']:
            values=audit.fixture(case);save(case+'-source.json',values)
            for arm in audit.ARMS:
                results={}
                for mode in spec()['orders'][case]:
                    check();partial={};method=OLD if mode=='OLD' else FrameLeafBudgetObserver.trace
                    with patch.object(BudgetObserver,'trace',method):
                        start=time.perf_counter_ns();cpu=time.process_time_ns()
                        try:r=audit.baseline.replay(values,audit.frozen.digest(values),count=80,arm=arm,evidence=partial,check=check)
                        except BaseException:
                            save(f'{case}-{arm}-{mode}-partial.json',partial);raise
                        elapsed=time.perf_counter_ns()-start;cpu=time.process_time_ns()-cpu
                    assert sys.gettrace() is None
                    assert r['terminal_cleanup'] and r['slots_released'] and r['ema_cleared']
                    res=r['resources'];meter=res['meter']
                    assert res['additional_python_peak']<=16384 and res['packed_bytes']==416
                    assert meter['frame_peak']<=18 and meter['output_slots_peak']<=2 and meter['combined_peak']<=20
                    assert meter['receipt_bytes_peak']<=16384 and meter['receipt_transient_utf8_bytes_peak']<=32768
                    t=time.perf_counter_ns();save(f'{case}-{arm}-{mode}.json',r);export=time.perf_counter_ns()-t
                    row=dict(case=case,arm=arm,mode=mode,wall_ns=elapsed,cpu_ns=cpu,serialization_file_ns=export,resources=res)
                    save(f'{case}-{arm}-{mode}-timing.json',row);rows.append(row);results[mode]=r
                assert canonical(results['OLD'])==canonical(results['NEW'])
                assert results['OLD']['resources']['meter']==results['NEW']['resources']['meter']
                pair=dict(case=case,arm=arm,semantic_equal=True,meter_equal=True,complete_release=True,
                    semantic_sha256=audit.frozen.digest(audit.semantic(results['NEW'])))
                pairs.append(pair);save(f'{case}-{arm}-equality.json',pair)
        save('measurements.json',rows);save('equality.json',pairs)
    except BaseException as exc:
        save('matrix-error.json',dict(error=type(exc).__name__+':'+str(exc),completed=rows,pairs=pairs));raise


def report():
    rows=audit.frozen.read(OUT/'measurements.json');pairs=audit.frozen.read(OUT/'equality.json')
    assert len(rows)==16 and len(pairs)==8
    comparisons=[]
    for case in ('N1','N2'):
        for arm in audit.ARMS:
            p={r['mode']:r for r in rows if r['case']==case and r['arm']==arm}
            comparisons.append(dict(case=case,arm=arm,old_seconds=p['OLD']['wall_ns']/1e9,new_seconds=p['NEW']['wall_ns']/1e9,
                ratio=p['OLD']['wall_ns']/p['NEW']['wall_ns'],reduction=1-p['NEW']['wall_ns']/p['OLD']['wall_ns']))
    sums={m:sum(r['wall_ns'] for r in rows if r['mode']==m)/1e9 for m in ('OLD','NEW')}
    peak=max(r['resources']['additional_python_peak'] for r in rows)
    maxima={k:max(r['resources']['meter'][k] for r in rows) for k in rows[0]['resources']['meter']}
    summary=dict(pairs=comparisons,total_seconds=sums,reduction=1-sums['NEW']/sums['OLD'],additional_python_peak=peak,meter_maxima=maxima)
    save('summary.json',summary)
    lines=['# Frame-Blattfall V1: neutrale Qualifikation (2026-10-03)','',
        'Separat versionierter Patch: ausschließlich geprüfter Frame-Blattfall. Historischer Beobachter, Policies, Grenzen und Exporte unverändert. Neuer Visitor nur im qualifizierten Vergleich aktiviert; Raster32 bleibt geschlossen.', '',
        'V01–V08 bestanden; konkrete IDs und neutrale Einzelbelege in tests.json und test-facts.json. Acht vollständige kanonische Fachvergleiche und acht Vergleiche sämtlicher meter-Felder gleich. Entscheidungen/Receipts, Fehlerupdates, Bestände, Zustandshashes, Endziel81, EMA-Löschung und terminale Freigabe eingeschlossen.', '',
        '16 Replays ×80 Positionen =1280 Aufnahmen +1280 Referenzfortschreibungen. N1 je Arm OLD/NEW, N2 NEW/OLD; beide mit aktivem Originaltrace, keine Warmups oder Zeitwiederholungen. Keine Diagnose-Timerhooks in Policy oder Visitor.', '',
        '| Quelle/Arm | OLD s | NEW s | OLD/NEW | Entlastung |','|---|---:|---:|---:|---:|']
    for p in comparisons:lines.append(f'| {p["case"]}/{p["arm"]} | {p["old_seconds"]:.6f} | {p["new_seconds"]:.6f} | {p["ratio"]:.3f} | {100*p["reduction"]:.2f}% |')
    lines+=['',f'Summe OLD {sums["OLD"]:.6f} s; NEW {sums["NEW"]:.6f} s; Entlastung {100*summary["reduction"]:.2f}%. Beobachtete Einzelpaare, kein statistischer Populationstest und keine Garantie einer Raster32-Gesamtlaufzeit.', '',
        f'Zusätzlicher Python-Heappeak maximal {peak} Byte (Grenze16384). Metermaxima: `{json.dumps(maxima,sort_keys=True)}`. Originale Trace- und Admission-Bounds bleiben vollständig aktiv. Gepackter EMA-Bound416 Byte ist ein Exportlimit, nicht für jeden Arm tatsächlicher Besitz. Freigegebene Ausgaben und terminales Cleanup in allen16 Replays. Isolierte Visitorallokationen stehen getrennt in V08; sie sind keine Gesamtprozess-RAM-Messung.', '',
        'V01 prüft per AST, dass am alten Tracekörper nur der Blattfall ergänzt wurde. V02/V03 prüfen gleiche erreichbare Frame-ID-Mengen, Aliase/Zyklen,18/19-Grenze, Slots und20er-Kombination. V04 prüft Unterklassen, mutable Payloads und fremde Feldtypen einschließlich darin verborgener Frames. V05 verwendet sechs echte Hypothesen einer neutralen Vorbelegung. V06 vergleicht Promotion, Verdrängung und vier Publikationsunterbrechungen samt Fehlerbereinigung und transienten Peaks. V07 prüft unveränderte Frame-, Fremdvektor- und Metadatenfehler. V08 prüft isolierte Allokation und das Fehlen persistenten Caches.', '',
        'Der kurze Pfad prüft jedes Mal exakten Frame-Typ, exakt tuple mit48 echten floats und ausschließlich skalare Bindungsfelder. Unterklassen und unklare/mutable Werte bleiben im alten Visitor. Frame-ID wird vor dem Rücksprung gezählt. Kein Cache, keine deaktivierten Traceereignisse, keine geänderten Policyentscheidungen oder Budgetgrenzen.', '',
        'Neue Bindung umfasst Patch, Tests, Runner und Plan sowie71 historische Codebindungen und gespeicherte Altartefakte. Prüfung vor/nach Matrix. Zeitwächterereignisse in matrix-lifecycle.json; Bestätigung nach join ist kein genauer Todeszeitpunkt, Abschlussphase dort nur prototypische Serialisierung. Die operative Ausführungsvorbereitung muss später Deadline, Abbruchanforderung, Workerbestätigung und gesamte Abschlussverwaltung getrennt protokollieren.', '',
        'Nächster Schritt zur Entscheidung des Projektleiters: qualifizierten Beobachterstand für eine separate technische Ausführungsvorbereitung übernehmen und deren Zeitbudget sowie vollständige Zeitwächterprotokollierung prüfen. Dieser Abschluss startet keinen Evaluationslauf und vervollständigt Raster32 nicht. Keine weitere Optimierung implementiert.', '']
    raw='\n'.join(lines).encode();used=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())
    assert used+len(raw)+65536<LIMIT
    with (OUT/'REPORT.md').open('xb') as f:f.write(raw)


def run():
    b=verify();OUT.mkdir(exist_ok=False);save('binding.json',b)
    save('sources.json',{n:(ROOT/n).read_text(encoding='utf-8') for n in FILES})
    error=None;success=False
    try:
        suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_frame_leaf_observer')
        def ids(s):
            for x in s:
                if isinstance(x,unittest.TestSuite):yield from ids(x)
                else:yield x.id()
        names=list(ids(suite));stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        save('tests.json',dict(ids=names,count=r.testsRun,success=r.wasSuccessful(),errors=len(r.errors),failures=len(r.failures),skips=len(r.skipped),output=stream.getvalue()))
        from tests.test_s2uc_frame_leaf_observer import FACTS
        save('test-facts.json',FACTS)
        assert r.wasSuccessful() and not r.skipped
        lifecycle=audit.supervise_diagnostic(matrix,(),900);save('matrix-lifecycle.json',lifecycle)
        assert lifecycle['status']=='NORMAL',lifecycle['status']
        verify();report();success=True
    except BaseException as exc:error=type(exc).__name__+':'+str(exc);raise
    finally:
        save('closure.json',dict(status='PASS' if success else 'FAILED',error=error,
            files={p.name:dict(bytes=p.stat().st_size,sha256=audit.frozen.sha(p)) for p in OUT.iterdir() if p.is_file()},
            historical_unchanged=success,raster_replays=0))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('prepare','run'))
    if parser.parse_args().action=='prepare':prepare()
    else:run()
