"""Last valid error pair only; inherited U lifecycle/selection, no added state."""
import math
from tools._s2uc_multi_error import (MultiErrorAdapter, require, HEAD, ENTRY, PAIR,
    U64, F64, UPDATING, mae48)

class LastErrorAdapter(MultiErrorAdapter):
    def consume_feedback(self, sample):
        self._guard()
        try:
            require(self.bank is not None, 'MULTI_NOT_ENABLED')
            self._validate_feedback_input(sample)
            target, active, count, choice, reason = HEAD.unpack_from(self.bank, 192)
            require(active == 1 and self.pending_prediction is not None and target == sample.index and
                    self.pending_prediction.target_index == target and 0 <= count <= 6, 'FEEDBACK_TARGET')
            self.bank[408] = UPDATING
            self._validate_cells()
            require(self._pframe is not None, 'PERSISTENCE_MISSING')
            ep = mae48(self._pframe.values, sample.values)
            for i in range(count):
                g, role, off, q, _ = ENTRY.unpack_from(self.bank, 208+16*i)
                require(g > 0 and role in (0, 1) and off in (0, 1) and q == 0 and self._frozen[i] is not None, 'TICKET_KEY')
                for j in range(i):
                    old = ENTRY.unpack_from(self.bank, 208+16*j)
                    require((old[0], old[1], old[2]) != (g, role, off), 'DUPLICATE_TICKET')
                ec = mae48(self._frozen[i].values, sample.values)
                new_ep = ep
                slot = None
                if self._generation_live(role, g):
                    slot = self._find(role, g, off)
                    if slot is None:
                        for s in range(6):
                            if self.bank[s*32+27]:
                                continue
                            if any(self.bank[208+16*j+11] == s for j in range(i)):
                                continue
                            slot = s
                            break
                        require(slot is not None, 'CELL_LIMIT')
                    self.bank[409] |= 1 << i
                require(math.isfinite(ec) and math.isfinite(new_ep), 'EMA_NONFINITE')
                PAIR.pack_into(self.bank, 304+16*i, ec, new_ep)
                self.bank[208+16*i+11] = 255 if slot is None else slot
            self._checkpoint('validated', -1)
            for i in range(count):
                if not (self.bank[409] & (1 << i)):
                    continue
                g, role, off, q, slot = ENTRY.unpack_from(self.bank, 208+16*i)
                ec, ep = PAIR.unpack_from(self.bank, 304+16*i)
                base = slot*32
                U64.pack_into(self.bank, base, g); self._checkpoint('generation', i)
                F64.pack_into(self.bank, base+8, ec); self._checkpoint('ec', i)
                F64.pack_into(self.bank, base+16, ep); self._checkpoint('ep', i)
                self.bank[base+24] = role; self._checkpoint('role', i)
                self.bank[base+25] = off; self._checkpoint('offset', i)
                self.bank[base+26] = q; self._checkpoint('quality', i)
                self.bank[base+27] = 1; self._checkpoint('valid', i)
            self._checkpoint('published', -1)
            self._release()
        except BaseException:
            self._terminate()
            raise

