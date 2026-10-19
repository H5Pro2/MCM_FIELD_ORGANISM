"""Optional direct-promotion rekeying. No changes to the legacy EMA or memory.

Serial synchronous use only. No callbacks/readers may observe publication;
BaseException during publication closes and clears the adapter.
"""
import math
import struct
from tools._s2uc_paired_error_ema import PairedErrorAdapter,CELL,require
from tools._s2uc_signal_approx_adapter import SignalApproxAdapter

POLICY='direct_promotion_v1'
GENERATION=struct.Struct('<Q')


class PromotionAdapter(PairedErrorAdapter):
    def __setattr__(self,name,value):
        if name in ('promotion_policy','_promotion_policy') and hasattr(self,'_promotion_policy'):
            require(False,'PROMOTION_POLICY_IMMUTABLE')
        super().__setattr__(name,value)

    def __delattr__(self,name):
        require(name not in ('promotion_policy','_promotion_policy'),'PROMOTION_POLICY_IMMUTABLE')
        super().__delattr__(name)

    @property
    def promotion_policy(self):return self._promotion_policy

    def __init__(self,*args,promotion_policy='disabled',**kwargs):
        require(promotion_policy in ('disabled',POLICY),'PROMOTION_POLICY')
        if promotion_policy==POLICY:
            require(kwargs.get('selection_policy')=='paired_error_ema_v1','PROMOTION_REQUIRES_EMA')
            require(kwargs.get('retrieval_policy','exact_v1')=='exact_v1','PROMOTION_EXACT_ONLY')
        self._promotion_policy=promotion_policy
        self._promotion_busy=False
        self._last_promoted=0
        super().__init__(*args,**kwargs)

    def _idle(self):require(not self._promotion_busy,'PROMOTION_PUBLICATION_BUSY')

    @property
    def selected_values(self):
        self._idle()
        return super().selected_values

    def accept_perception(self,sample):
        self._idle()
        return super().accept_perception(sample)

    def consume_feedback(self,sample):
        self._idle()
        return super().consume_feedback(sample)

    def _receipt(self,*args):
        self._idle()
        return super()._receipt(*args)

    def finish_story(self):
        self._idle()
        return super().finish_story()

    def release_prediction(self):
        self._idle()
        return super().release_prediction()

    def _promotion_checkpoint(self,stage,index):
        """No-op publication boundary; overridden only by fault-injection fixtures."""

    def _validate_promotion(self,candidate,previous,result,scope):
        require(self._promotion_busy and not self.closed,'PROMOTION_NOT_ACTIVE')
        require(scope==self._feedback_scope==(self.arm.owner,self.arm.profile,self.stream,
            self.hop,self.window,self.start_sample,self.first_ordinal),'PROMOTION_SCOPE')
        require(candidate is not None and result['action']=='TRACE_PROMOTED','PROMOTION_EVENT')
        old=candidate.candidate_generation;new=result['generation']
        require(type(old) is int and 0<old<2**64 and type(new) is int and
            self._last_promoted<new<2**64,'PROMOTION_GENERATION_OR_REPLAY')
        require(result['candidate_generation']==old and self.arm._candidate is None,'PROMOTION_CANDIDATE')
        require(all(t.generation!=new for t in previous),'PROMOTION_REUSED_GENERATION')
        retained=self.arm._retained_many
        require(len(retained)==min(2,len(previous)+1),'PROMOTION_STOCK')
        expected_evicted=previous[0].generation if len(previous)==2 else None
        require(result['evicted']==expected_evicted,'PROMOTION_EVICTION')
        survivors=previous[1:] if len(previous)==2 else previous
        require(all(retained[i] is t for i,t in enumerate(survivors)),'PROMOTION_SURVIVORS')
        target=retained[-1]
        require(target.generation==new and target.frames is candidate.frames,'PROMOTION_FRAME_IDENTITY')
        require(len(candidate.frames)==4 and all(f.owner==self.arm.owner and f.profile==self.arm.profile
            for f in candidate.frames),'PROMOTION_FRAME_SCOPE')
        require(all(candidate.frames[i].ordinal<candidate.frames[i+1].ordinal for i in range(3)),
            'PROMOTION_ORDINALS')
        # No shadow bank or saved error pairs: validate by bounded pairwise scan.
        for i in range(12):
            g,ec,ep,role,offset,quality,valid=CELL.unpack_from(self._errors.cells,i*32)
            require(valid in (0,1),'PROMOTION_CELL_VALID')
            if not valid:continue
            require(0<g<2**64 and role in (0,1) and offset in (0,1) and quality in (0,1)
                and math.isfinite(ec) and math.isfinite(ep) and ec>=0 and ep>=0,'PROMOTION_CELL')
            require(not (role==0 and g==new),'PROMOTION_TARGET_CONFLICT')
            require((role==1 and g==old) or (role==0 and any(t.generation==g for t in previous)),
                'PROMOTION_STALE_CELL')
            for j in range(i):
                other=CELL.unpack_from(self._errors.cells,j*32)
                require(not other[-1] or (other[3],other[0],other[4],other[5])!=(role,g,offset,quality),
                    'PROMOTION_DUPLICATE_CELL')
        return old,new,expected_evicted

    def _publish_promotion(self,candidate,previous,result,scope):
        old,new,evicted=self._validate_promotion(candidate,previous,result,scope)
        self._promotion_checkpoint('validated',-1)
        for i in range(12):
            row=CELL.unpack_from(self._errors.cells,i*32)
            if row[-1] and row[3]==0 and row[0]==evicted:
                self._errors.cells[i*32:(i+1)*32]=bytes(32)
        self._promotion_checkpoint('evicted',-1)
        for i in range(12):
            row=CELL.unpack_from(self._errors.cells,i*32)
            if row[-1] and row[3]==1 and row[0]==old:
                self._promotion_checkpoint('before_key',i)
                GENERATION.pack_into(self._errors.cells,i*32,new)
                self._promotion_checkpoint('generation_written',i)
                self._errors.cells[i*32+24]=0
                self._promotion_checkpoint('after_key',i)
        self._errors.prune(self)
        self._last_promoted=new
        self._promotion_checkpoint('published',-1)

    def _admit(self,frame):
        self._idle()
        if self.promotion_policy=='disabled' or (frame.ordinal-self.first_ordinal+1)%4:
            return super()._admit(frame)
        candidate=self.arm._candidate
        previous=tuple(self.arm._retained_many)
        scope=(self.arm.owner,self.arm.profile,self.stream,self.hop,self.window,self.start_sample,self.first_ordinal)
        original=self.arm.close_segment
        had_override='close_segment' in vars(self.arm)
        prior_override=vars(self.arm).get('close_segment')
        event=None
        def capture(segment):
            nonlocal event
            require(event is None,'PROMOTION_MULTIPLE_CLOSE')
            event=original(segment)
            return event
        self._promotion_busy=True
        try:
            self.arm.close_segment=capture
            try:
                # Same inherited admission, but do not prune candidate cells yet.
                SignalApproxAdapter._admit(self,frame)
            finally:
                if had_override:self.arm.close_segment=prior_override
                else:del self.arm.close_segment
            require(event is not None,'PROMOTION_CLOSE_MISSING')
            if event['action']=='TRACE_PROMOTED':
                self._publish_promotion(candidate,previous,event,scope)
            else:self._errors.prune(self)
        except BaseException:
            self._terminate()
            raise
        finally:
            self._promotion_busy=False
