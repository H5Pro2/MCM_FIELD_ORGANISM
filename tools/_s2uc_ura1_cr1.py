"""CR1: one freeze/receipt; only all-cold nonempty eligibility uses original recency.
The validated U receipt is kept explicit to preserve all error paths. Feedback,
admission, promotion and pruning are inherited unchanged. No extra instance state.
"""
import json
from tools._s2uc_multi_error import (MultiErrorAdapter, require, CELL, HEAD, ENTRY,
                                    FREEZING, PENDING, REASONS)
from tools._s2uc_continuation_adapter import PredictionReceipt
from tools._s2uc_pair_context_adapter import ContextReceipt
C_REASONS = REASONS + ('SELECTED_COLD_ORIGINAL_RECENCY',)

class ColdRecencyAdapter(MultiErrorAdapter):
    def _receipt(self, status, indices, intervals, matches):
        if self.bank is None or len(indices) != 2:
            return super()._receipt(status, indices, intervals, matches)
        self._guard()
        try:
            require(self.pending_prediction is None, 'PREDICTION_PENDING')
            require(len(matches) <= 9, 'MATCH_LIMIT')
            self.bank[408] = FREEZING
            self._validate_cells()
            count = warm = 0
            best = 0.0
            choice = ties = 0
            newest, winning_key, cold_choice = -1, None, 0
            self._pframe = self.pair[1]
            # Serialize each row separately to avoid an additional metadata table.
            rows = []
            for match_index, m in enumerate(matches):
                role = {'retained': 0, 'candidate': 1}[m['role']]
                g, off = m['generation'], m['offset']
                require(type(g) is int and 0 < g < 2**64 and off in (0, 1, 2), 'MATCH_KEY')
                for prior_index in range(match_index):
                    n = matches[prior_index]
                    require((n['role'], n['generation'], n['offset']) != (m['role'], g, off), 'DUPLICATE_MATCH')
                if m['factors'] != [1.0] or off == 2:
                    rows.append(json.dumps(dict(eligible=False, reason='NO_SUCCESSOR' if off == 2 else 'FACTOR_UNSPECIFIED'), separators=(',', ':')))
                    continue
                require(count < 6, 'HYPOTHESIS_LIMIT')
                found = None
                for sr, sg, fs in self._sources():
                    if (sr, sg) == (m['role'], g):
                        require(fs[0].segment == m['formation'] and
                                all(fs[k].ordinal == m['ordinals'][k] for k in range(4)), 'SOURCE_IDENTITY')
                        found = fs[off+2]
                require(found is not None, 'SOURCE_MISSING')
                self._frozen[count] = found
                ENTRY.pack_into(self.bank, 208+16*count, g, role, off, 0, 255)
                slot = self._find(role, g, off)
                ec = ep = d = None
                if slot is not None:
                    r = CELL.unpack_from(self.bank, slot*32)
                    ec, ep = r[1], r[2]
                    d = ec-ep
                    warm += 1
                    if d < best:
                        best, choice, ties = d, count+1, 1
                    elif d == best and d < 0:
                        ties += 1
                selection_key = (role, g, off)
                if found.ordinal > newest or (found.ordinal == newest and
                        (winning_key is None or selection_key < winning_key)):
                    newest, winning_key, cold_choice = found.ordinal, selection_key, count+1
                rows.append(json.dumps(dict(eligible=True, ticket=count, ec=ec, ep=ep, delta=d,
                    evaluation='COLD' if slot is None else 'TIE_P' if d == 0 else 'WORSE_THAN_P' if d > 0 else 'BETTER_THAN_P'), separators=(',', ':'), allow_nan=False))
                count += 1
            reason = 1 if not count else 2 if not warm else 3 if best == 0 else 4 if ties > 1 else 5
            if reason != 5:
                choice = 0
            if count and not warm:
                choice, reason = cold_choice, 6
            HEAD.pack_into(self.bank, 192, indices[-1]+1, 1, count, choice, reason)
            header = dict(status=status, stream=self.stream, owner=self.arm.owner,
                          profile=self.arm.profile, input_indices=indices, source_intervals=intervals,
                          read_revision=self.revision, decision=C_REASONS[reason], choice=choice)
            raw = json.dumps(header, separators=(',', ':'))[:-1] + ',"matches":['
            raw += ','.join(json.dumps(m, separators=(',', ':'), allow_nan=False) for m in matches)
            raw += '],"hypotheses":[' + ','.join(rows) + ']}'
            require(len(raw.encode('utf-8')) <= 16384, 'RECEIPT_LIMIT')
            context = self._frozen[choice-1].values if choice else None
            self.pending_prediction = PredictionReceipt(indices[-1]+1, self.revision,
                C_REASONS[reason], context, self._pframe.values, raw)
            self._checkpoint('frozen', -1)
            self.bank[408] = PENDING
            return ContextReceipt(raw)
        except BaseException:
            self._terminate()
            raise

