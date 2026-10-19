"""Optional A1 admission; legacy U and its modules remain unchanged."""
import json
from tools._s2uc_multi_error import MultiErrorAdapter, IDLE, ADMITTING, U64, require
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2tu_retained_trace import RetainedTrace
from tools._s2uc_pair_context_adapter import ContextReceipt
from tools._s2uc_continuation_adapter import PredictionReceipt

POLICY='unique_partial_admission_v1'


class A1Adapter(MultiErrorAdapter):
    def _admission_match(self,matches):
        chosen=None
        for m in matches:
            if m['factors']==[1.0] and m['offset'] in (0,1):
                if chosen is not None:return None
                chosen=m
        c=self.arm._candidate
        if chosen is None or chosen['role']!='candidate' or c is None:return None
        require(chosen['generation']==c.candidate_generation and
            chosen['ordinals']==[f.ordinal for f in c.frames],'A1_ORIGINAL_IDENTITY')
        if any(f.ordinal<=c.frames[-1].ordinal for f in self.pair):return None
        # Only current observed forming frames and the two current hints.
        if len(self.arm._forming)==2:
            for _,_,frames in self._sources():
                if all(frames[j].values==(self.arm._forming[j] if j<2 else self.pair[j-2]).values for j in range(4)):
                    return None
        return chosen

    def _admit_candidate(self,offset):
        a=self.arm;c=a._candidate;previous=tuple(a._retained_many)
        require(self.bank[408]==IDLE and self.pending_prediction is None,'A1_PENDING')
        require(self._scope()==self._feedback_scope,'A1_SCOPE')
        require(c is not None and len(previous)<=2,'A1_STOCK')
        require(a._retained_generation<2**64-1 and U64.unpack_from(self.bank,400)[0]<=a._retained_generation,'A1_GENERATION')
        self._validate_cells()
        generation=a._retained_generation+1
        replacement=RetainedTrace(generation,c.frames)  # Same tuple, no Frame copies.
        victim=previous[0] if len(previous)==2 else None
        event=dict(reason='PARTIAL_RETRIEVAL_ADMISSION',full_repeat=False,
            ordinals=[f.ordinal for f in c.frames],offset=offset,hints=[f.ordinal for f in self.pair],
            old_key=[1,c.candidate_generation],new_key=[0,generation],
            victim=None if victim is None else dict(generation=victim.generation,ordinals=[f.ordinal for f in victim.frames]))
        self._checkpoint('a1_prepared',-1)
        self.bank[408]=ADMITTING
        if victim is not None:
            a._retained_many.pop(0);del a._observation_end[victim.generation]
        self._checkpoint('a1_evicted',-1)
        a._candidate=None;a._retained_many.append(replacement);a._retained_generation=generation
        a._observation_end[generation]=c.frames[-1].ordinal
        self._checkpoint('a1_moved',-1)
        self._promote(c,previous,dict(candidate_generation=c.candidate_generation,generation=generation,
            evicted=None if victim is None else victim.generation))
        self._checkpoint('a1_cells',-1)
        a._check_budget();self.revision+=1
        self._checkpoint('a1_revision',-1)
        self.bank[408]=IDLE
        return event

    def _receipt(self,status,indices,intervals,matches):
        try:
            event=None
            if len(indices)==2:
                self._guard()
                require(self.pending_prediction is None,'A1_PENDING')
                m=self._admission_match(matches)
                if m is not None:
                    event=self._admit_candidate(m['offset'])
                    require(self.arm.hint(self.pair[0]) is None,'A1_HINT_PHASE')
                    result=self.arm.hint(self.pair[1]);status=result['decision'];matches=result['matches']
            if status=='CONFIRMED_RETAINED_MATCH':status='RETAINED_ORIGINAL_MATCH'
            receipt=super()._receipt(status,indices,intervals,matches)
            raw=receipt.json_text[:-1]+',"retained_semantics":"ADMITTED_NOT_FULL_REPEAT_PROOF","a1_admission":'+json.dumps(event,separators=(',',':'))+'}'
            require(len(raw.encode())<=16384,'A1_RECEIPT_LIMIT')
            if len(indices)==2:
                p=self.pending_prediction
                self.pending_prediction=PredictionReceipt(p.target_index,p.read_revision,p.status,p.context_values,p.persistence_values,raw)
            self._checkpoint('a1_receipt',-1)
            return ContextReceipt(raw)
        except BaseException:
            # Fail closed: no partially committed, usable memory is published.
            self._terminate()
            raise


def create(profile,owner,stream,*,admission_policy='disabled',multi_policy='disabled',**kwargs):
    if admission_policy=='disabled':
        return MultiErrorAdapter(FactorRecencyArm(profile,owner),stream,multi_policy=multi_policy,**kwargs)
    require(admission_policy==POLICY and multi_policy!='disabled','A1_POLICY')
    return A1Adapter(FactorRecencyArm(profile,owner),stream,multi_policy=multi_policy,**kwargs)
