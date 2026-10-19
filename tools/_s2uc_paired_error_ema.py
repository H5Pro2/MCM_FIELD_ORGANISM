"""Optional causal error memory; unchanged perception/retrieval/confirmation."""
import json
import math
import struct

from tools._s2uc_signal_approx_adapter import SignalApproxAdapter
from tools._s2uc_pair_context_adapter import AdapterError, PerceptionSample

CELL = struct.Struct('<QddBBBB4x')  # generation, errors, role, offset, quality, valid
TICKET = struct.Struct('<QQBBBBB11x')  # generation, target, role, offset, quality, choice, valid
CELLS = 12


def require(ok, code):
    if not ok:
        raise AdapterError(code)


def mae48(x, y):
    """Shared internal/baseline arithmetic: ordered scalar binary64 additions."""
    require(type(x) is tuple and type(y) is tuple and len(x)==len(y)==48, 'MAE_SHAPE')
    total = 0.0
    for i in range(48):
        require(type(x[i]) is float and type(y[i]) is float and math.isfinite(x[i]) and math.isfinite(y[i]), 'MAE_VALUES')
        difference = abs(x[i]-y[i])
        total = total+difference
        require(math.isfinite(difference) and math.isfinite(total), 'MAE_NONFINITE')
    return total/48.0


class ErrorMemory:
    __slots__ = ('cells','ticket')

    def __init__(self):
        self.cells = bytearray(CELLS*CELL.size)
        self.ticket = bytearray(TICKET.size)

    def clear(self):
        self.cells[:] = bytes(CELLS*CELL.size)
        self.release()

    def release(self):
        self.ticket[:] = bytes(TICKET.size)

    def find(self, role, generation, offset, quality):
        for i in range(CELLS):
            g, ec, ep, r, o, q, valid = CELL.unpack_from(self.cells, i*CELL.size)
            if valid and (r,g,o,q)==(role,generation,offset,quality):
                return i
        return None

    def errors(self, role, generation, offset, quality):
        i = self.find(role,generation,offset,quality)
        if i is None:
            return None
        row = CELL.unpack_from(self.cells,i*CELL.size)
        return row[1],row[2]

    def prepare(self, role, generation, offset, quality, target):
        require(role in (0,1) and offset in (0,1) and quality in (0,1), 'EMA_KEY')
        require(type(generation) is int and 0<generation<2**64 and type(target) is int and 0<target<2**63, 'EMA_GENERATION')
        require(not TICKET.unpack(self.ticket)[-1], 'EMA_TICKET_PENDING')
        errors = self.errors(role,generation,offset,quality)
        choice = int(errors is not None and errors[0]<errors[1])
        TICKET.pack_into(self.ticket,0,generation,target,role,offset,quality,choice,1)

    def update(self, role, generation, offset, quality, ec, ep):
        require(all(type(x) is float and math.isfinite(x) and x>=0 for x in (ec,ep)), 'EMA_ERROR_VALUES')
        i = self.find(role,generation,offset,quality)
        if i is None:
            for j in range(CELLS):
                if not CELL.unpack_from(self.cells,j*CELL.size)[-1]:
                    i=j
                    break
            require(i is not None,'EMA_CELL_LIMIT')
        else:
            old=CELL.unpack_from(self.cells,i*CELL.size)
            ec=(0.5*old[1])+(0.5*ec)
            ep=(0.5*old[2])+(0.5*ep)
        require(math.isfinite(ec) and math.isfinite(ep),'EMA_NONFINITE')
        # Build all bytes before publication: conversion/packing cannot partially commit.
        packed=CELL.pack(generation,ec,ep,role,offset,quality,1)
        self.cells[i*CELL.size:(i+1)*CELL.size]=packed

    def prune(self, adapter):
        for i in range(CELLS):
            generation,_,_,role,_,_,valid=CELL.unpack_from(self.cells,i*CELL.size)
            if valid and not adapter._generation_live(role,generation):
                self.cells[i*CELL.size:(i+1)*CELL.size]=bytes(CELL.size)


class PairedErrorAdapter(SignalApproxAdapter):
    """Disabled unless selection_policy is explicitly paired_error_ema_v1.

    Active callers consume_feedback(valid next sample) before normal admission.
    Output selection is an alias; original context and persistence stay frozen.
    """
    def __setattr__(self,name,value):
        if name in ('selection_policy','_selection_policy') and hasattr(self,'_selection_policy'):
            raise AdapterError('SELECTION_POLICY_IMMUTABLE')
        super().__setattr__(name,value)

    def __delattr__(self,name):
        if name in ('selection_policy','_selection_policy'):
            raise AdapterError('SELECTION_POLICY_IMMUTABLE')
        super().__delattr__(name)

    @property
    def selection_policy(self):
        return self._selection_policy

    def __init__(self,*args,selection_policy='disabled',**kwargs):
        require(selection_policy in ('disabled','paired_error_ema_v1'),'SELECTION_POLICY')
        require(kwargs.get('policy','legacy_v1')=='legacy_v1','EMA_LEGACY_ONLY')
        self._selection_policy=selection_policy
        self._errors=None
        self._feedback_scope=None
        super().__init__(*args,**kwargs)
        if selection_policy=='paired_error_ema_v1':
            require(all(0<=x<2**63 for x in (self.hop,self.window,self.start_sample,self.first_ordinal)), 'EMA_TIME_RANGE')
            self._errors=ErrorMemory()
            self._feedback_scope=(self.arm.owner,self.arm.profile,self.stream,self.hop,self.window,self.start_sample,self.first_ordinal)

    def _generation_live(self,role,generation):
        if role==0:
            return any(t.generation==generation for t in self.arm._retained_many)
        return self.arm._candidate is not None and self.arm._candidate.candidate_generation==generation

    def _validate_feedback_input(self,sample):
        require(not self.closed,'CLOSED')
        require(type(sample) is PerceptionSample,'PERCEPTION_TYPE_REQUIRED')
        require(self._feedback_scope==(self.arm.owner,self.arm.profile,self.stream,self.hop,self.window,self.start_sample,self.first_ordinal),'SCOPE_CHANGED')
        i=sample.index
        require(type(i) is int and i==self.next_index and 1<=i<2**63,'INDEX_GAP_OR_REORDER')
        require((sample.profile,sample.owner,sample.stream)==(self.arm.profile,self.arm.owner,self.stream),'SCOPE_CHANGED')
        start=self.start_sample+(i-1)*self.hop
        require(type(sample.start_sample) is int and type(sample.end_sample) is int and
                (sample.start_sample,sample.end_sample)==(start,start+self.window),'TIME_DISCONTINUITY')
        require(0<=sample.start_sample<sample.end_sample<2**63,'EMA_TIME_RANGE')
        require(type(sample.values) is tuple and len(sample.values)==48 and
                all(type(x) is float and math.isfinite(x) for x in sample.values),'VALUES_INVALID')
        require(self.first_ordinal+i-1<2**63,'ORDINAL_LIMIT')

    def _freeze_choice(self):
        p=self.pending_prediction
        if p is None or p.context_values is None:
            return
        data=json.loads(p.provenance_json)
        require(len(data['matches'])==1,'EMA_SINGLE_REQUIRED')
        match=data['matches'][0]
        role={'retained':0,'candidate':1}[match['role']]
        quality={'EXACT':0,'APPROXIMATE':1}[match.get('match_quality','EXACT')]
        self._errors.prepare(role,match['generation'],match['offset'],quality,p.target_index)

    def _receipt(self,status,indices,intervals,matches):
        receipt=super()._receipt(status,indices,intervals,matches)
        if self._errors is not None and len(indices)==2:
            self._errors.prune(self)
            self._freeze_choice()
        return receipt

    @property
    def selected_values(self):
        p=self.pending_prediction
        if p is None:
            return None
        if self._errors is None:
            return p.context_values if p.context_values is not None else p.persistence_values
        row=TICKET.unpack(self._errors.ticket)
        return p.context_values if row[-1] and row[-2] else p.persistence_values

    def consume_feedback(self,sample):
        try:
            require(self._errors is not None,'EMA_NOT_ENABLED')
            self._validate_feedback_input(sample)
            p=self.pending_prediction
            require(p is not None and p.target_index==sample.index,'PREDICTION_TARGET_INVALID')
            generation,target,role,offset,quality,choice,valid=TICKET.unpack(self._errors.ticket)
            if valid:
                require(target==sample.index and p.context_values is not None,'EMA_TICKET_TARGET')
                ec=mae48(p.context_values,sample.values)
                ep=mae48(p.persistence_values,sample.values)
                if self._generation_live(role,generation):
                    self._errors.update(role,generation,offset,quality,ec,ep)
        except Exception:
            self._terminate()
            raise
        finally:
            self.release_prediction()

    def accept_perception(self,sample):
        if self._errors is not None:
            try:
                self._validate_feedback_input(sample)
            except Exception:
                self._terminate()
                raise
        return super().accept_perception(sample)

    def _admit(self,frame):
        super()._admit(frame)
        if self._errors is not None:
            self._errors.prune(self)

    def release_prediction(self):
        super().release_prediction()
        if self._errors is not None:
            self._errors.release()

    def _terminate(self):
        if self._errors is not None:
            self._errors.clear()
        super()._terminate()

    def finish_story(self):
        # An even-length bounded story can leave one unobserved next target.
        if self._errors is not None:
            self.release_prediction()
        return super().finish_story()
