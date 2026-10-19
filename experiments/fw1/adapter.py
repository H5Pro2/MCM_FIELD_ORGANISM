"""FW1: only confirmed retained cells are invalidated; no extra policy state."""
from tools._s2uc_multi_error import MultiErrorAdapter, CELL, ADMITTING, require

class ResetAdapter(MultiErrorAdapter):
    def _invalidate_confirmed(self, generation):
        require(self.bank[408]==ADMITTING, 'RESET_PHASE')
        require(type(generation) is int and sum(t.generation==generation for t in self.arm._retained_many)==1, 'RESET_GENERATION')
        require(self.arm._observation_end.get(generation)==self.admitted+self.first_ordinal-1, 'RESET_ENDMARK')
        self._validate_cells()
        self._checkpoint('reset_validated',generation)
        for slot in range(6):
            g,ec,ep,role,off,q,valid=CELL.unpack_from(self.bank,slot*32)
            if valid and role==0 and g==generation:
                self._zero(slot*32,(slot+1)*32)
                self._checkpoint('reset_cell',slot)
        self._checkpoint('reset_complete',generation)

    def _admit(self, frame):
        if self.bank is None:return super()._admit(frame)
        self._guard();before_state=self.bank[408];self.bank[408]=ADMITTING
        try:
            candidate=self.arm._candidate;previous=tuple(self.arm._retained_many)
            old_ends=tuple(self.arm._observation_end.items())
            self.arm.form(frame);self.admitted+=1;self.revision+=1
            result=None
            if (frame.ordinal-self.first_ordinal+1)%4==0:
                result=self.arm.close_segment(frame.segment);self.revision+=1
                if result['action']=='TRACE_PROMOTED':self._promote(candidate,previous,result)
            self._prune()
            if result is not None and result['action']=='TRACE_CONFIRMED_RECENT':
                g=result['generation']
                require(sum(end!=self.arm._observation_end.get(key) for key,end in old_ends)==1 and
                        any(key==g and end!=self.arm._observation_end.get(g) for key,end in old_ends), 'RESET_TRANSITION')
                require(any(t.generation==g and any(t is p for p in previous) for t in self.arm._retained_many), 'RESET_IDENTITY')
                self._invalidate_confirmed(result['generation'])
            self.bank[408]=before_state
        except BaseException:
            self._terminate();raise
