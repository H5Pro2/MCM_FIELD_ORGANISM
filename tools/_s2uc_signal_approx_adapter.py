"""Explicit signal gate plus unit-factor approximate retrieval; no memory edits."""
import dataclasses,json,math,sys
from tools._s2uc_continuation_adapter import ContinuationAdapter
from tools._s2uc_pair_context_adapter import AdapterError,ContextReceipt

def amplitude(values):
    if any(type(x) is not float or not math.isfinite(x) for x in values):
        raise AdapterError('DISTANCE_VALUES_INVALID')
    a=math.fsum(abs(x) for x in values)/48
    if not math.isfinite(a):raise ArithmeticError('AMPLITUDE_NONFINITE')
    return a

def relative_l1(h0,h1,s0,s1,ha0,ha1,sa0,sa1):
    denominator=max((ha0+ha1)/2,(sa0+sa1)/2)
    if not math.isfinite(denominator) or denominator<sys.float_info.min:
        raise ArithmeticError('DISTANCE_DENOMINATOR')
    distance=math.fsum(abs(h[k]-s[k]) for h,s in ((h0,s0),(h1,s1)) for k in range(48))/96/denominator
    if not math.isfinite(distance):raise ArithmeticError('DISTANCE_NONFINITE')
    return distance

class SignalApproxAdapter(ContinuationAdapter):
    _locked=frozenset(('retrieval_policy','epsilon','tau','_retrieval_policy','_epsilon','_tau'))
    def __setattr__(self,name,value):
        if name in self._locked and hasattr(self,'_retrieval_policy'):
            raise AdapterError('RETRIEVAL_CONFIG_IMMUTABLE')
        super().__setattr__(name,value)
    def __delattr__(self,name):
        if name in self._locked:raise AdapterError('RETRIEVAL_CONFIG_IMMUTABLE')
        super().__delattr__(name)
    @property
    def retrieval_policy(self):return self._retrieval_policy
    @property
    def epsilon(self):return self._epsilon
    @property
    def tau(self):return self._tau
    def __init__(self,*args,retrieval_policy='exact_v1',epsilon=None,tau=None,**kwargs):
        if retrieval_policy not in ('exact_v1','signal_approx_v1'):
            raise AdapterError('RETRIEVAL_POLICY_INVALID')
        if retrieval_policy=='exact_v1':
            if epsilon is not None or tau is not None:raise AdapterError('EXACT_PARAMETERS_UNUSED')
        elif type(epsilon) is not float or not math.isfinite(epsilon) or epsilon<sys.float_info.min or type(tau) is not float or not math.isfinite(tau) or not 0.<=tau<=.125:
            raise AdapterError('RETRIEVAL_PARAMETERS_INVALID')
        self._epsilon=epsilon;self._tau=tau;self._retrieval_policy=retrieval_policy
        super().__init__(*args,**kwargs)

    def _sources(self):
        for t in self.arm._retained_many:yield 'retained',t.generation,t.frames
        if self.arm._candidate is not None:
            c=self.arm._candidate;yield 'candidate',c.candidate_generation,c.frames

    def _select(self,status,exact):
        h0,h1=self.pair[0].values,self.pair[1].values
        try:ha0,ha1=amplitude(h0),amplitude(h1)
        except ArithmeticError:return 'ABSTAIN_SIGNAL_NUMERIC',[]
        if min(ha0,ha1)<=self.epsilon:return 'ABSTAIN_LOW_SIGNAL',[]
        if len(exact)>1:return status,[dict(m,match_quality='EXACT') for m in exact]
        if exact:
            m=exact[0];found=None
            for role,g,frames in self._sources():
                if role==m['role'] and g==m['generation'] and frames[0].segment==m['formation'] and [f.ordinal for f in frames]==m['ordinals']:found=frames
            if found is None:raise AdapterError('PRESTATE_SOURCE_MISSING')
            o=m['offset']
            try:sa0,sa1=amplitude(found[o].values),amplitude(found[o+1].values)
            except ArithmeticError:return 'ABSTAIN_SIGNAL_NUMERIC',[]
            if min(sa0,sa1)<=self.epsilon:return 'ABSTAIN_STORED_LOW_SIGNAL',[]
            return status,[dict(m,match_quality='EXACT')]
        matches=[]
        for role,g,frames in self._sources():
            for o in range(3):
                try:
                    s0,s1=frames[o].values,frames[o+1].values
                    sa0,sa1=amplitude(s0),amplitude(s1)
                    if min(sa0,sa1)<=self.epsilon:continue
                    d=relative_l1(h0,h1,s0,s1,ha0,ha1,sa0,sa1)
                except ArithmeticError:
                    # No candidate is safe if another admissible comparison is unknown.
                    return 'ABSTAIN_APPROX_NUMERIC',[]
                if d<=self.tau:
                    matches.append(dict(role=role,generation=g,formation=frames[0].segment,
                        ordinals=[f.ordinal for f in frames],offset=o,factors=[1.],
                        match_quality='APPROXIMATE',distance=d))
        return ('ABSTAIN_NO_APPROX_CONTEXT' if not matches else 'ABSTAIN_APPROX_AMBIGUOUS' if len(matches)>1 else 'APPROXIMATE_SINGLE_MATCH'),matches

    def _receipt(self,status,indices,intervals,matches):
        if self.retrieval_policy=='exact_v1' or len(indices)!=2:
            return super()._receipt(status,indices,intervals,matches)
        exact_count=len(matches);status,selected=self._select(status,matches)
        receipt=super()._receipt(status,indices,intervals,selected)
        data=json.loads(receipt.json_text)
        data['retrieval']=dict(policy=self.retrieval_policy,epsilon=self.epsilon,tau=self.tau,
            exact_match_count=exact_count,signal_lost_exact_single=exact_count==1 and status in ('ABSTAIN_LOW_SIGNAL','ABSTAIN_STORED_LOW_SIGNAL','ABSTAIN_SIGNAL_NUMERIC'))
        raw=json.dumps(data,separators=(',',':'),allow_nan=False)
        if len(raw.encode())>16384:raise AdapterError('RECEIPT_LIMIT')
        # Same immutable vector references; provenance updated before _admit.
        self.pending_prediction=dataclasses.replace(self.pending_prediction,provenance_json=raw)
        return ContextReceipt(raw)
