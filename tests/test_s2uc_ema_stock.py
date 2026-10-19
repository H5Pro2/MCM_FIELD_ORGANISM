"""Independent neutral fixtures only; never materialize the bound stock recipe."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import s2uc_ema_stock as s
from tools._s2uc_ema_stock_observer import observed_replay,digest
from tools._s2uc_ema_stock_assessment import metrics,assess
from tools._s2uc_paired_error_replay import replay
from tools._s2uc_bounded_audio import OutputLedger,AudioError

FACTS={}
EXPORT_FOLDER=None


def neutral():
    # Independent 64-frame lifecycle fixture, no A/B/Bp/C recipe or block order.
    proto=dict(X=[.11,.23,.67,.89],Y=[.31,.43,.79,.97],
        Q=[.31,.43,.43,.97],Z=[.17,.37,.59,.83],W=[.19,.41,.61,.91])
    order=['X','X','Y','Y','X','Q','Q','Z','Z','X','X','X','W','W','X','X']
    return [(float(x),)*48 for name in order for x in proto[name]]


class StockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=None
        if EXPORT_FOLDER is None:
            cls.temp=tempfile.TemporaryDirectory();folder=Path(cls.temp.name)/'neutral-export'
        else:folder=EXPORT_FOLDER
        with patch.object(s,'material',side_effect=AssertionError('REAL_GENERATOR_FORBIDDEN')):
            cls.export=s.export(folder,neutral,s.plan(),mode='NEUTRAL_QUALIFICATION')
        cls.folder=folder;cls.results=cls.export['results']
        FACTS['neutral_export']=dict(bytes=cls.export['bytes'],limit=OutputLedger.LIMIT,
            closure_reserve=OutputLedger.RESERVE,source_frames=64,experimental_admissions=192,
            internal_reference_advances=192,real_generator_called=False,
            resources={a:r['resources'] for a,r in cls.results.items()})

    @classmethod
    def tearDownClass(cls):
        if cls.temp:cls.temp.cleanup()

    def test_S01_observer_equivalence_and_full_export(self):
        profile=digest(dict(mode='NEUTRAL_QUALIFICATION',geometry='direct48.stock.v1'))
        for a,r in self.results.items():
            baseline=replay(neutral(),profile,count=64,arm=a)
            for k,v in baseline.items():self.assertEqual(r[k],v,k)
            self.assertEqual(len(r['generation_events']),64)
            meter=r['resources']['frame_meter']
            self.assertGreater(meter['receipt_bytes_peak'],0)
            self.assertLessEqual(meter['receipt_bytes_peak'],16384)
            self.assertLessEqual(meter['receipt_transient_utf8_bytes_peak'],32768)
            self.assertGreaterEqual(meter['receipt_transient_utf8_bytes_peak'],2*meter['receipt_bytes_peak'])
        self.assertEqual(self.results['E']['state_hashes'],self.results['K']['state_hashes'])
        self.assertEqual(self.results['E']['state_hashes'],self.results['P']['state_hashes'])
        self.assertEqual(sum(p.stat().st_size for p in self.folder.iterdir()),self.export['bytes'])
        closure=json.loads((self.folder/'closure.json').read_text())
        self.assertEqual(closure['status'],'COMPLETE')
        self.assertLessEqual((self.folder/'closure.json').stat().st_size,OutputLedger.RESERVE)
        for name,info in closure['files'].items():self.assertEqual(s.sha(self.folder/name),info['sha256'])

    def test_S02_ambiguity_then_later_eviction(self):
        r=self.results['E'];u=next(u for u in r['error_updates'] if u['target']==27)
        f=next(f for f in r['forecasts'] if f['target']==27)
        deletion=next(e for e in r['generation_events'] if e['frame']==28)
        self.assertEqual(len(f['receipt']['matches']),2)
        self.assertFalse(f['context_available']);self.assertFalse(u['ticket'][-1])
        self.assertEqual(u['before'],u['after']);self.assertTrue(u['before'])
        self.assertTrue(any(c['role']==0 and c['generation']==2 for c in deletion['deleted']))
        self.assertEqual(u['phase'],'target_consumption');self.assertEqual(deletion['phase'],'admission')
        FACTS['ambiguity_vs_deletion']=dict(no_update_target=27,regular_deletion_frame=28,
            target_cells_before=u['before'],target_cells_after=u['after'],deletion=deletion)

    def test_S03_new_candidate_and_retained_generations_cold(self):
        r=self.results['E'];events={e['frame']:e for e in r['generation_events']}
        self.assertTrue(any(c['role']==0 and c['generation']==1 for c in events[36]['deleted']))
        fs={f['target']:f for f in r['forecasts']}
        for target in (43,47):
            f=fs[target];ticket=f['ticket'];g,_,role,offset,quality,_,valid=ticket
            self.assertTrue(valid);self.assertEqual(f['choice'],'PERSISTENCE')
            self.assertFalse(any((c['role'],c['generation'],c['offset'],c['quality'])==(role,g,offset,quality) for c in f['errors_before']))
        self.assertEqual(fs[43]['ticket'][2],1);self.assertEqual(fs[47]['ticket'][2],0)
        self.assertTrue(any(c['role']==1 for c in events[44]['deleted']))
        self.assertEqual(fs[59]['choice'],'CONTEXT')
        FACTS['fresh_generations']=dict(old_evicted_at=36,candidate_cold_target=43,
            promotion_at=44,retained_cold_target=47,own_experience_context_target=59)

    def test_S04_all_five_masks_and_cold_costs(self):
        p=s.plan();rows={a:dict(rows=[dict(target=t,choice='PERSISTENCE',context_mae=0.,selected_mae=1.)
            for t in p['masks']['Gesamt']]) for a in ('E','K','P')}
        for row in rows['E']['rows']:
            row['selected_mae']=0. if row['target'] in p['masks']['D'] else 4.
        m=metrics(rows,p['masks'])
        self.assertEqual({k:v['arms']['E']['count'] for k,v in m.items()},dict(V=7,D=3,M=9,N=22,Gesamt=31))
        self.assertEqual(m['D']['arms']['E']['mae'],0.)
        self.assertGreater(m['V']['arms']['E']['mae'],m['V']['arms']['K']['mae'])
        self.assertEqual(m['V']['arms']['E']['error_sum'],16.)
        self.assertEqual(m['Gesamt']['arms']['E']['error_sum'],112.)
        self.assertEqual(m['M']['arms']['E']['error_sum']+m['N']['arms']['E']['error_sum'],112.)
        FACTS['fixed_mask_fixture']=m

    def test_S05_missing_target_never_zero(self):
        r=copy.deepcopy(self.results);r['E']['rows']=[x for x in r['E']['rows'] if x['target']!=55]
        m=metrics(r,s.plan()['masks'])
        self.assertEqual(m['V']['arms']['E']['status'],'NOT_EVALUABLE')
        self.assertIsNone(m['V']['arms']['E']['mae']);self.assertEqual(m['V']['arms']['E']['missing'],[55])

    def test_S06_expectation_mismatch_is_not_system_error(self):
        before=copy.deepcopy(self.results);r=assess(self.results,s.plan())
        self.assertTrue(r['expectation_deviations']);self.assertEqual(r['technical_errors'],[])
        self.assertEqual(r['stock_causality'],'NOT_EVALUABLE');self.assertEqual(r['net_benefit'],'NOT_EVALUABLE')
        self.assertEqual(before,self.results)
        FACTS['independent_neutral_expectations']=dict(deviations=len(r['expectation_deviations']),
            technical_errors=r['technical_errors'],dependent_status=r['net_benefit'])

    def test_S07_budget_reserve_overflow_exclusivity(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'budget';ledger=OutputLedger(folder)
            with self.assertRaises(AudioError):ledger.write('too-big.json','x'*(ledger.LIMIT-ledger.RESERVE))
            ledger.write('data.json',dict(ok=True));ledger.write('closure.json',dict(status='STOP'),final=True)
            with self.assertRaises(FileExistsError):OutputLedger(folder)
            with self.assertRaises(AudioError):ledger.write('late.json',{})
            self.assertLessEqual(sum(p.stat().st_size for p in folder.iterdir()),ledger.LIMIT)
        FACTS['budget_guards']=dict(oversize_rejected=True,closure_preserved=True,overwrite_rejected=True)

    def test_S08_authorization_checked_before_material_or_export(self):
        with patch.object(s,'verify_binding'),patch.object(s,'read',return_value={'status':'PENDING'}),\
             patch.object(s,'authorization',return_value={'status':'AUTHORIZED_ONCE'}),\
             patch.object(s,'material') as material,patch.object(s,'export') as export:
            with self.assertRaisesRegex(AssertionError,'SEPARATE_AUTHORIZATION_REQUIRED'):s.run('neutral-pending.json')
            material.assert_not_called();export.assert_not_called()

    def test_S09_failure_preserves_partial_and_closure_no_retry(self):
        calls=[]
        def fail(values,profile,arm,*,count,evidence):
            calls.append(arm);evidence['neutral_marker']='observed-before-failure';raise RuntimeError('NEUTRAL_INJECTED_FAILURE')
        with tempfile.TemporaryDirectory() as tmp,patch.object(s,'observed_replay',side_effect=fail):
            folder=Path(tmp)/'failed'
            with self.assertRaisesRegex(RuntimeError,'NEUTRAL_INJECTED_FAILURE'):s.export(folder,neutral,s.plan(),mode='NEUTRAL_FAILURE')
            self.assertEqual(calls,['E'])
            self.assertEqual(json.loads((folder/'closure.json').read_text())['status'],'NOT_EVALUABLE')
            self.assertEqual(json.loads((folder/'partial-observer.json').read_text())['neutral_marker'],'observed-before-failure')
            with patch.object(s,'material') as material:
                with self.assertRaises(FileExistsError):s.export(folder,material,s.plan(),mode='NEUTRAL_FAILURE')
                material.assert_not_called()

    def test_S10_net_benefit_uses_V_not_D(self):
        p=s.plan();p['expected_stock']=[];p['expected_targets']={}
        r=copy.deepcopy(self.results)
        for f in r['E']['forecasts']:
            if f['target'] in p['masks']['V']:f['context_available']=True
        for arm in r:
            for row in r[arm]['rows']:
                row['selected_mae']=(0. if row['target'] in p['masks']['D'] else 4.) if arm=='E' else 1.
        result=assess(r,p)
        self.assertEqual(result['technical_errors'],[])
        self.assertEqual(result['net_benefit'],'SCHADEN')
        self.assertEqual(result['metrics']['D']['arms']['E']['mae'],0.)
        for f in r['E']['forecasts']:
            if f['target']==55:f['context_available']=False
        self.assertEqual(assess(r,p)['net_benefit'],'NOT_EVALUABLE')
        FACTS['benefit_guard']=dict(D_better_but_V_harm='SCHADEN',V_unavailable='NOT_EVALUABLE')

    def test_S11_corrupt_update_and_illegal_transfer_are_technical(self):
        r=copy.deepcopy(self.results)
        u=next(u for u in r['E']['error_updates'] if u['target']==27)
        u['after'][0]['ec']+=1.
        result=assess(r,s.plan())
        self.assertIn('27:UPDATE_WITHOUT_TICKET',result['technical_errors'])
        self.assertIn('27:WRONG_CELL_UPDATE',result['technical_errors'])
        r=copy.deepcopy(self.results)
        event=next(e for e in r['E']['generation_events'] if e['frame']==44)
        event['cells_after'].append(dict(role=0,generation=5,offset=0,quality=0,ec=0.,ep=1.))
        self.assertIn('44:ILLEGAL_ADMISSION_CELL_CHANGE',assess(r,s.plan())['technical_errors'])
        FACTS['corruption_detection']=dict(illegal_target_update=True,illegal_generation_transfer=True)

    def test_S12_closure_at_full_ordinary_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger=OutputLedger(Path(tmp)/'full')
            # JSON string adds two quotes and one newline.
            ledger.write('payload.json','x'*(ledger.LIMIT-ledger.RESERVE-3))
            self.assertEqual(ledger.used,ledger.LIMIT-ledger.RESERVE)
            with self.assertRaises(AudioError):ledger.write('extra.json',{})
            ledger.write('closure.json',dict(status='BUDGET_STOP'),final=True)
            self.assertLessEqual(ledger.used,ledger.LIMIT)
        FACTS['closure_reserve_at_cap']=True


if __name__=='__main__':unittest.main()
