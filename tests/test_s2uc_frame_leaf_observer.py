"""Neutral visitor qualification; no evaluation raster generation."""
import ast
import dataclasses
import inspect
import sys
import textwrap
import tracemalloc
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from tools.s2uc_context_prediction_check import BudgetObserver
from tools._s2uc_frame_leaf_observer_v1 import FrameLeafBudgetObserver,scalar_frame_leaf
from tools._s2tu_retained_trace import Frame
from tools._s2uc_continuation_adapter import ContinuationAdapter,PredictionReceipt
from tools._s2uc_promotion_replay import PromotionMeter
from tests.test_s2uc_promotion_ema import fixture as promotion_fixture,payloads
from tests.test_s2uc_multi_error import fixture as six_fixture,freeze
from tools.s2uc_continuous_comparison import state

OLD=BudgetObserver.trace
NEW=FrameLeafBudgetObserver.trace
FACTS={}


def frame(i=1):return Frame((.25,)*48,'a'*64,'owner','neutral',i)


def snapshot(roots,name='_s2uc_pair_context_adapter.py',function='neutral'):
    return SimpleNamespace(f_code=SimpleNamespace(co_filename=name,co_name=function),f_locals=roots,f_back=None)


def observe(method,roots):
    meter=BudgetObserver();captured={}
    def profile(f,event,arg):
        if f.f_code is method.__code__ and event=='return':
            captured['ids']=set(f.f_locals.get('frames',()))
    previous=sys.getprofile();sys.setprofile(profile)
    error=None
    try:method(meter,snapshot(roots),'line',None)
    except AssertionError as exc:error=(type(exc).__name__,str(exc))
    finally:sys.setprofile(previous)
    return captured['ids'],vars(meter),error


class VisitorTests(unittest.TestCase):
    def compare(self,roots):
        old=observe(OLD,roots);new=observe(NEW,roots)
        self.assertEqual(old,new)
        return old

    def test_V01_only_leaf_branch_changed(self):
        old=ast.parse(textwrap.dedent(inspect.getsource(OLD)))
        new=ast.parse(textwrap.dedent(inspect.getsource(NEW)))
        count=0
        class Remove(ast.NodeTransformer):
            def visit_If(self,node):
                nonlocal count
                if isinstance(node.test,ast.Call) and isinstance(node.test.func,ast.Name) and node.test.func.id=='scalar_frame_leaf':
                    count+=1;return None
                return self.generic_visit(node)
        new=Remove().visit(new)
        self.assertEqual(count,1);self.assertEqual(ast.dump(old),ast.dump(new))
        self.assertTrue(scalar_frame_leaf(frame()))

    def test_V02_identity_alias_cycles_and_frame_limit(self):
        for n in (0,1,18,19):
            fs=[frame(i) for i in range(n)];root={'frames':fs,'aliases':fs*3};root['cycle']=root
            ids,meter,error=self.compare(root)
            self.assertEqual(ids,{id(f) for f in fs});self.assertEqual(meter['frame_peak'],n)
            self.assertEqual(error is not None,n>18)
        FACTS['V02']=dict(boundary=18,overflow=19,aliases_and_cycles=True)

    def test_V03_output_slots_combined_and_bytes(self):
        records=[]
        for n,context in ((18,False),(18,True),(19,True)):
            a=ContinuationAdapter.__new__(ContinuationAdapter)
            a.pending_prediction=PredictionReceipt(1,0,'NEUTRAL',(.3,)*48 if context else None,(.2,)*48,'{}')
            a.frames=[frame(i) for i in range(n)]
            ids,meter,error=self.compare({'adapter':a})
            self.assertEqual(meter['output_slots_peak'],2 if context else 1)
            self.assertEqual(meter['combined_peak'],n+(2 if context else 1))
            self.assertEqual(error is not None,n>18);records.append(meter)
        FACTS['V03']=records

    def test_V04_mutable_custom_subclass_fallback(self):
        @dataclasses.dataclass(frozen=True)
        class Box: child:object
        @dataclasses.dataclass(frozen=True)
        class SubFrame(Frame): extra:object=None
        child=frame(99)
        subclass=SubFrame((.25,)*48,'a'*64,'owner','neutral',1,child)
        cases=[subclass]
        for field,value in (('values',[child]),('values',(Box(child),)),('profile',Box(child)),
                            ('owner',Box(child)),('segment',Box(child)),('ordinal',Box(child))):
            x=frame();object.__setattr__(x,field,value);cases.append(x)
        for x in cases:
            self.assertFalse(scalar_frame_leaf(x))
            ids,_,_=self.compare({'root':x});self.assertEqual(ids,{id(x),id(child)})
        x=frame();object.__setattr__(x,'values',[.25]*48)
        self.assertFalse(scalar_frame_leaf(x));self.compare({'root':x})
        x.values[0]=child
        self.assertIn(id(child),self.compare({'root':x})[0])
        FACTS['V04']=dict(fallback_cases=len(cases)+2,subclass_extra_frame_detected=True,mutable_rechecked=True)

    def test_V05_six_hypotheses_identity_and_release(self):
        a=six_fixture(six=True)
        try:
            receipt=freeze(a)
            self.assertEqual(len(receipt['matches']),6)
            ids,meter,error=self.compare({'adapter':a})
            self.assertIsNone(error);self.assertEqual(len(ids),14)
            FACTS['V05']=dict(hypotheses=6,resources=meter)
        finally:a._terminate()
        self.assertFalse(self.compare({'adapter':a})[0]);self.assertIsNone(a.pending_prediction)
        self.assertFalse(any(a.bank))

    def test_V06_promotion_eviction_and_interrupted_cleanup(self):
        results={}
        points=[None,('validated',-1),('evicted',-1),('generation_written',0),('published',-1)]
        for label,method in (('OLD',OLD),('NEW',NEW)):
            records=[]
            for point in points:
                a,f=promotion_fixture();meter=PromotionMeter(a)
                before=payloads(a,1,7);oldest=a.arm._retained_many[0].generation
                def checkpoint(stage,index):
                    if (stage,index)==point:raise KeyboardInterrupt('NEUTRAL_LEAF_INTERRUPT')
                error=None
                with patch.object(BudgetObserver,'trace',method),patch.object(a,'_promotion_checkpoint',checkpoint):
                    meter.admission_bound(f);sys.settrace(meter.trace)
                    try:a._admit(f)
                    except KeyboardInterrupt as exc:error=str(exc)
                    finally:sys.settrace(None)
                if point is None:
                    self.assertEqual(payloads(a,0,5),before)
                    self.assertNotIn(oldest,[x.generation for x in a.arm._retained_many])
                else:
                    self.assertEqual(error,'NEUTRAL_LEAF_INTERRUPT');self.assertTrue(a.closed)
                    self.assertFalse(any(a._errors.cells+a._errors.ticket));self.assertIsNone(a.pending_prediction)
                records.append(dict(point=point,error=error,resources={k:v for k,v in vars(meter).items() if k!='adapter'},
                    state=state(a.arm),cells=list(a._errors.cells),ticket=list(a._errors.ticket)))
                a._terminate();self.assertFalse(self.compare({'adapter':a})[0])
                meter.adapter=None
            results[label]=records
        self.assertEqual(results['OLD'],results['NEW']);FACTS['V06']=results['NEW']

    def test_V07_derived_guards_unchanged(self):
        results={}
        for label,method in (('OLD',OLD),('NEW',NEW)):
            records=[]
            for kind in ('frame_overflow','vector','metadata'):
                a,f=promotion_fixture();meter=PromotionMeter(a);error=None
                with patch.object(BudgetObserver,'trace',method):
                    try:
                        if kind=='frame_overflow':
                            a.pair=[frame(100+i) for i in range(8)];meter.admission_bound(f)
                        else:
                            local={'self':a,'matches':[{}]*10} if kind=='metadata' else {'self':a,'alien':tuple(float(i) for i in range(48))}
                            meter.trace(snapshot(local,'_s2uc_signal_approx_adapter.py','_select'),'line',None)
                    except (AssertionError,ValueError) as exc:error=(type(exc).__name__,str(exc))
                self.assertIsNotNone(error);records.append(dict(kind=kind,error=error))
                a._terminate();meter.adapter=None
            results[label]=records
        self.assertEqual(results['OLD'],results['NEW']);FACTS['V07']=results['NEW']

    def test_V08_observer_allocations_no_persistent_cache(self):
        root={'frames':[frame(i) for i in range(18)]};records={}
        for label,method in (('OLD',OLD),('NEW',NEW)):
            meter=BudgetObserver();snap=snapshot(root)
            tracemalloc.start();base=tracemalloc.get_traced_memory()[0]
            try:method(meter,snap,'line',None)
            finally:
                _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
            self.assertEqual(set(vars(meter)),{'frame_peak','output_slots_peak','combined_peak','output_python_bytes_peak','samples'})
            self.assertTrue(all(type(v) is int for v in vars(meter).values()))
            records[label]=dict(isolated_observer_peak=peak-base,resources=vars(meter))
        self.assertEqual(records['OLD']['resources'],records['NEW']['resources'])
        FACTS['V08']=records


if __name__=='__main__':unittest.main()
