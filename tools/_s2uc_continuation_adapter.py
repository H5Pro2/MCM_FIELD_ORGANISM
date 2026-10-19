"""Local causal continuation output. Memory and perception rules are inherited."""
from dataclasses import dataclass
import json,math,sys
from tools._s2uc_pair_context_adapter import PairContextAdapter,PerceptionSample,AdapterError

@dataclass(frozen=True,slots=True)
class PredictionReceipt:
    target_index:int
    read_revision:int
    status:str
    context_values:tuple|None
    persistence_values:tuple
    provenance_json:str

def _scaled_continuation(values,exponent):
    """Scalar preflight; publish one tuple only after all channels pass."""
    overflow=underflow=inexact=False
    for x in values:
        if type(x) is not float or not math.isfinite(x):
            raise AdapterError('STORED_VALUES_INVALID')
        try:y=math.ldexp(x,exponent)
        except OverflowError:
            overflow=True;continue
        if not math.isfinite(y):overflow=True;continue
        if (x!=0. and y==0.) or (y!=0. and abs(y)<sys.float_info.min):
            underflow=True;continue
        if math.ldexp(y,-exponent)!=x:inexact=True
    if overflow:return None,'ABSTAIN_SCALE_OVERFLOW'
    if underflow:return None,'ABSTAIN_SCALE_UNDERFLOW'
    if inexact:return None,'ABSTAIN_SCALE_INEXACT'
    return tuple(math.ldexp(x,exponent) for x in values),None

class ContinuationAdapter(PairContextAdapter):
    def __setattr__(self,name,value):
        if name in ('policy','_policy') and hasattr(self,'_policy'):
            raise AdapterError('POLICY_IMMUTABLE')
        super().__setattr__(name,value)
    def __delattr__(self,name):
        if name in ('policy','_policy'):raise AdapterError('POLICY_IMMUTABLE')
        super().__delattr__(name)
    @property
    def policy(self):return self._policy
    def __init__(self,*args,policy='legacy_v1',**kwargs):
        if type(policy) is not str or policy not in ('legacy_v1','factor_scaled_v1'):
            raise AdapterError('POLICY_INVALID')
        self._policy=policy
        super().__init__(*args,**kwargs)
        self.pending_prediction=None
    def _receipt(self,status,indices,intervals,matches):
        receipt=super()._receipt(status,indices,intervals,matches)
        if len(indices)!=2:return receipt
        if self.pending_prediction is not None:raise AdapterError('PREDICTION_PENDING')
        prediction_status='ABSTAIN_NO_CONTEXT';values=None
        if len(matches)>1:prediction_status='AMBIGUOUS_CONTEXT'
        elif matches:
            match=matches[0]
            factors=match['factors']
            if self.policy=='factor_scaled_v1' and (type(factors) is not list or not factors or any(type(f) is not float or f not in (.5,1.,2.) for f in factors)):
                raise AdapterError('FACTOR_INVALID')
            if self.policy=='legacy_v1' and factors!=[1.]:prediction_status='FACTOR_CONTINUATION_NOT_SPECIFIED'
            elif len(factors)!=1:prediction_status='ABSTAIN_AMBIGUOUS_FACTOR'
            elif match['offset']+2>=4:prediction_status='ABSTAIN_NO_SUCCESSOR'
            else:
                sources=[('retained',t.generation,t.frames) for t in self.arm._retained_many]
                if self.arm._candidate is not None:
                    sources.append(('candidate',self.arm._candidate.candidate_generation,self.arm._candidate.frames))
                found=[frames for role,g,frames in sources if role==match['role'] and g==match['generation'] and frames[0].segment==match['formation'] and [f.ordinal for f in frames]==match['ordinals']]
                if len(found)!=1:raise AdapterError('PRESTATE_SOURCE_MISSING')
                values=found[0][match['offset']+2].values
                prediction_status='PREDICTED_'+match['role'].upper()
                if self.policy=='factor_scaled_v1' and factors[0]!=1.:
                    values,error=_scaled_continuation(values,-1 if factors[0]==.5 else 1)
                    prediction_status=error or 'PREDICTED_SCALED_'+match['role'].upper()
        # Only tuples of immutable numeric values, never Frame/Trace references.
        self.pending_prediction=PredictionReceipt(indices[-1]+1,self.revision,prediction_status,values,self.pair[1].values,receipt.json_text)
        return receipt
    def accept_perception(self,sample):
        if self.pending_prediction is not None:
            self._terminate();raise AdapterError('RELEASE_PREDICTION_BEFORE_NEXT_ADMISSION')
        return super().accept_perception(sample)
    def release_prediction(self):
        self.pending_prediction=None
    def _terminate(self):
        self.pending_prediction=None
        super()._terminate()

def evaluate_prediction(prediction,actual):
    """Separate observer only; does not receive an adapter or memory object."""
    if type(prediction) is not PredictionReceipt or type(actual) is not tuple or len(actual)!=48 or any(type(x) is not float or not math.isfinite(x) for x in actual):
        raise AdapterError('EVALUATION_INPUT_INVALID')
    return dict(context='AMBIGUOUS' if prediction.status=='AMBIGUOUS_CONTEXT' else 'ABSTAIN' if prediction.context_values is None else 'HIT' if prediction.context_values==actual else 'MISS',persistence='HIT' if prediction.persistence_values==actual else 'MISS',context_covered=prediction.context_values is not None)


def consume_prediction(adapter,sample):
    """Synchronous observer handoff; free output slots even on evaluation errors."""
    try:
        p=adapter.pending_prediction
        if type(sample) is not PerceptionSample or p is None or sample.index!=p.target_index or (sample.owner,sample.profile,sample.stream)!=(adapter.arm.owner,adapter.arm.profile,adapter.stream):
            raise AdapterError('PREDICTION_TARGET_INVALID')
        return evaluate_prediction(p,sample.values)
    except Exception:
        adapter._terminate()
        raise
    finally:
        adapter.release_prediction()
