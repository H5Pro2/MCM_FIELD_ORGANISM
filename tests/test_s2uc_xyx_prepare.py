"""Only preparation tests. No source generation or adapter/replay execution."""
import copy
import json
import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

from tools import s2uc_xyx_prepare as q
from tools._s2uc_xyx_assessment import assess,criteria,metrics,ARMS

FACTS={}


def saved():
    # Read the consumed OLD Y=P run solely as a parser regression.
    c=q.prior.read(q.prior.OUT/'closure.json')
    for name,item in c['files'].items():
        assert q.prior.sha(q.prior.OUT/name)==item['sha256']
    return ({a:q.prior.read(q.prior.OUT/(a+'.json')) for a in ARMS},q.prior.read(q.prior.OUT/'source.json'))


def abstract_decisions():
    # Declared boolean/label test records; no source, no simulated policy history.
    out={t:dict(selected_label='X' if t in (11,15,43,47) else 'Y',reason='SELECTED_BY_ERROR',
        strict_warm_winner=True,original_frozen_verified=True,prior_feedback=[1],phase_feedback=[1],
        available_labels=['X','Y']) for t in (11,15,23,27,31,35,39,43,47)}
    return out


class PreparationTests(unittest.TestCase):
    def test_B01_fixed_recipe_masks_and_limits(self):
        p=q.plan()
        self.assertEqual(p['recipes']['Y'],['3/16','5/16','9/16','15/16'])
        self.assertEqual(p['blocks'],['X']*4+['Y']*4+['X']*4)
        self.assertEqual(set(p['masks']),{'G','H','N','S','F','A_W','A_R'})
        self.assertEqual(sorted(p['masks']['H']+p['masks']['N']),p['masks']['G'])
        self.assertEqual(p['criteria']['deadlines'],dict(change=27,return_phase=43))
        self.assertEqual(p['limits'],q.prior.plan()['limits'])
        self.assertNotEqual(p['output'],q.prior.plan()['output'])
        _,oldsource=saved()
        with self.assertRaisesRegex(RuntimeError,'SOURCE_RECIPE'): q.validate_source(oldsource)
        FACTS['B1']=dict(new_recipe_is_static=True,old_source_rejected=True,materialized=False)

    def test_B02_all_masks_and_missing_target(self):
        r,_=saved(); v,c,n=metrics(r,q.plan()['masks'])
        for mask,targets in q.plan()['masks'].items():
            for a in ARMS: self.assertEqual(v[mask][a]['count'],len(targets))
        self.assertEqual(len(c),23)
        r['U']['rows']=[x for x in r['U']['rows'] if x['target']!=23]
        v,_,n=metrics(r,q.plan()['masks'])
        self.assertEqual(v['A_W']['U']['missing'],[23]); self.assertIsNone(v['H']['U']['mae'])
        self.assertEqual(n['H'],'NOT_EVALUABLE')

    def test_B03_selection_positive_and_all_negatives(self):
        good=abstract_decisions(); self.assertEqual(criteria(good)['verdict'],'BELEGT')
        cases=[]
        for target in (11,15,27,31,43,47):
            for field,value in (('selected_label','P'),('strict_warm_winner',False),
                    ('original_frozen_verified',False),('prior_feedback',[]),('phase_feedback',[]),
                    ('reason','COLD_ONLY'),('reason','TIED_IMPROVEMENT')):
                d=copy.deepcopy(good); d[target][field]=value
                self.assertEqual(criteria(d)['verdict'],'NICHT_NACHGEWIESEN')
                cases.append([target,field,value])
        d=copy.deepcopy(good); d[23]['available_labels']=['X']
        self.assertEqual(criteria(d)['verdict'],'NICHT_NACHGEWIESEN')
        d=copy.deepcopy(good); del d[43]
        self.assertEqual(criteria(d)['verdict'],'NICHT_NACHGEWIESEN')
        FACTS['B3']=dict(negative_cases=cases,availability_and_missing_also_fail=True,
                         abstract_fixture_not_learning_evidence=True)

    def test_B04_strict_net_H_and_G_separate(self):
        r,_=saved(); h=q.plan()['masks']['H']
        for a in ARMS:
            for row in r[a]['rows']:
                row['selected_mae']=0. if a=='U' or (a=='K' and row['target'] in h) else 1.
        v,_,n=metrics(r,q.plan()['masks'])
        self.assertEqual(n,{'H':'NICHT_NACHGEWIESEN','G':'BELEGT'})
        self.assertEqual(criteria({})['verdict'],'NICHT_NACHGEWIESEN')
        FACTS['B4']=dict(H_tie_rejected=True,G_separate=True,net_does_not_replace_selection=True)

    def test_B05_saved_evidence_chain_and_ticket_permutation(self):
        r,source=saved(); original=assess(r,source,q.plan())
        self.assertEqual(original['technical_errors'],[])
        self.assertEqual(original['selection']['verdict'],'NICHT_NACHGEWIESEN')  # OLD source Y=P.
        for f in r['U']['forecasts']:
            selected=next((m for m,h in zip(f['matches'],f['hypotheses']) if h['eligible'] and h['ticket']+1==f['choice']),None)
            zipped=list(zip(f['matches'],f['hypotheses']))[::-1]
            f['matches']=[m for m,h in zipped]; f['hypotheses']=[h for m,h in zipped]
            count=0; f['choice']=0
            for m,h in zipped:
                if h['eligible']:
                    h['ticket']=count
                    if m is selected: f['choice']=count+1
                    count+=1
            t=f['input_indices'][-1]+1
            for row in r['U']['rows']:
                if row['target']==t: row['choice']=f['choice']
        altered=assess(r,source,q.plan())
        self.assertEqual(altered['technical_errors'],[])
        self.assertEqual([(d['target'],d['selected_key']) for d in original['decisions']],
                         [(d['target'],d['selected_key']) for d in altered['decisions']])
        FACTS['B5']=dict(old_saved_evidence_only=True,ticket_order_not_identity=True,old_Y_equals_P_not_pass=True)

    def test_B06_bad_provenance_feedback_and_missing_evidence(self):
        for kind in ('ordinal','raw_error','before','after','missing'):
            r,source=saved()
            up=next(x for x in r['U']['updates'] if x['target']==39)
            if kind=='ordinal': up['hypotheses'][0]['original_ordinal']=1
            elif kind=='raw_error': up['hypotheses'][0]['ec']+=.125
            elif kind=='before': up['before'][0]['ec']+=.125
            elif kind=='after': up['after'][0]['ec']+=.125
            else: r['U']['updates'].remove(up)
            out=assess(r,source,q.plan())
            self.assertTrue(out['technical_errors']); self.assertEqual(out['selection']['verdict'],'NOT_EVALUABLE')

    def test_B07_authorization_before_materialization(self):
        for value in ({'status':'PENDING_SEPARATE_AUTHORIZATION'}, q.prior.read(q.prior.AUTH)):
            with patch.object(q,'verify'),patch.object(q.prior,'read',return_value=value), \
                 patch.object(q,'auth',return_value={'status':'AUTHORIZED_ONCE','action':'NEW'}), \
                 patch.object(q,'_materialize') as material,patch.object(q,'_export') as export:
                with self.assertRaisesRegex(RuntimeError,'AUTHORIZATION'): q.run('unused')
                material.assert_not_called(); export.assert_not_called()

    def test_B08_exclusive_before_supplier(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(q,'_materialize') as supplier:
                with self.assertRaises(FileExistsError): q._export(Path(tmp),supplier,549025,lambda:None)
                supplier.assert_not_called()

    def test_B09_partial_failure_and_no_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'failed'
            def fail(*args,**kwargs):
                kwargs['evidence']['failure_stage']='neutral_injected'
                raise KeyboardInterrupt('neutral')
            with patch.object(q,'validate_source'),patch.object(q.prior,'multi_replay',fail),self.assertRaises(KeyboardInterrupt):
                q._export(out,lambda:[],549025,lambda:None)
            c=q.prior.read(out/'closure.json')
            self.assertEqual(c['status'],'FAILED'); self.assertTrue((out/'partial.json').exists())
            with self.assertRaises(FileExistsError): q._export(out,lambda:[],549025,lambda:None)
            FACTS['B9']=dict(failure_preserved=True,no_retry=True,real_replay_calls=0)

    def test_B10_resources_not_zero_peaks_and_budget(self):
        r,_=saved(); report=q.resource_report(r)
        self.assertIsNone(report['U']['measured_original_frame_peak'])
        self.assertEqual(report['U']['controlled_original_frame_upper_bound'],12)
        with tempfile.TemporaryDirectory() as tmp:
            ledger=q.OutputLedger(Path(tmp)/'budget'); ledger.LIMIT-=549025
            ledger.used=ledger.LIMIT-ledger.RESERVE
            with self.assertRaises(Exception): ledger.write('overflow.json',{'x':1})
            ledger.write('closure.json',{'status':'test'},final=True)
        FACTS['B10']=dict(reused_bytes=549025,limit=4194304,reserve=262144,unpopulated_is_null=True)

    def test_B11_binding_rejects_changes(self):
        base=dict(code={'a':'h'},plan_sha256='x',contract_sha256='x',python=sys.version,
                  python_executable_sha256='x',reused_qualification_bytes=549025,reused_closure_sha256='x')
        for change in ('plan','code','contract','runtime'):
            b=copy.deepcopy(base); p=q.plan()
            if change=='plan': p['recipes']['Y'][2]='5/16'
            elif change=='code': b['code']={'a':'changed'}
            elif change=='contract': b['contract_sha256']='changed'
            else: b['python']='wrong'
            with patch.object(q,'hashes',return_value={'a':'h'}),patch.object(q.prior,'sha',return_value='x'), \
                 patch.object(q.prior,'check_qualification',return_value=549025), \
                 patch.object(q.prior,'read',side_effect=lambda path: b if path==q.BINDING else p):
                with self.assertRaises(RuntimeError): q.verify()

    def test_B12_frozen_forecast_boundary(self):
        for change in ('indices','revision','interval','matches'):
            r,source=saved(); f=next(f for f in r['U']['forecasts'] if f['input_indices'][-1]+1==39)
            if change=='indices': f['input_indices'][0]=1
            elif change=='revision': f['read_revision']+=1
            elif change=='interval': f['source_intervals'][0][0]+=1
            else: f['matches'].pop(); f['hypotheses'].pop()
            result=assess(r,source,q.plan())
            self.assertTrue(result['technical_errors'])
            self.assertEqual(result['selection']['verdict'],'NOT_EVALUABLE')


if __name__=='__main__': unittest.main()
