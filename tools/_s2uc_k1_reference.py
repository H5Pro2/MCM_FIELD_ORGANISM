"""Independent observer-only state machine; no production arm/close imports."""


class Reference:
    def __init__(self, enabled):
        self.enabled = enabled
        self.pending = []
        self.retained = []
        self.candidate = None
        self.candidate_serial = self.retained_serial = 0
        self.observation_end = {}

    @staticmethod
    def payload(trace):
        return tuple(v for _, v in trace['frames'])

    def feed(self, ordinal, values):
        self.pending.append((ordinal, tuple(values)))
        if len(self.pending) != 4:
            return
        frames, self.pending = self.pending, []
        incoming = tuple(v for _, v in frames)
        old = self.candidate
        expires = self.enabled and old is not None and frames[-1][0] >= old['frames'][-1][0] + 8
        known = next((t for t in self.retained if self.payload(t) == incoming), None)
        if known is not None:
            if frames[0][0] > self.observation_end[known['generation']]:
                self.retained.remove(known)
                self.retained.append(known)
                self.observation_end[known['generation']] = frames[-1][0]
            if expires:
                self.candidate = None
        elif old is not None and self.payload(old) == incoming:
            if set(o for o, _ in old['frames']).isdisjoint(o for o, _ in frames):
                self.retained_serial += 1
                if len(self.retained) == 2:
                    evicted = self.retained.pop(0)
                    del self.observation_end[evicted['generation']]
                self.retained.append(dict(generation=self.retained_serial, frames=old['frames']))
                self.observation_end[self.retained_serial] = frames[-1][0]
                self.candidate = None
            elif expires:
                self.candidate = None
        elif old is None or not self.enabled or expires:
            self.candidate_serial += 1
            self.candidate = dict(generation=self.candidate_serial, frames=frames)
        # Otherwise intentionally discard incoming; no backlog.

    def snapshot(self):
        def trace(t):
            return None if t is None else dict(generation=t['generation'], ordinals=[o for o, _ in t['frames']], values=[v for _, v in t['frames']])
        return dict(candidate=trace(self.candidate), retained=[trace(t) for t in self.retained],
            forming=[o for o, _ in self.pending], candidate_serial=self.candidate_serial,
            retained_serial=self.retained_serial, observation_end=dict(self.observation_end))

    def matches(self, pair):
        result = []
        traces = [(0,t) for t in self.retained] + ([] if self.candidate is None else [(1,self.candidate)])
        for role,t in traces:
            for offset in range(3):
                if self.payload(t)[offset:offset+2] == tuple(pair):
                    result.append((role,t['generation'],offset))
        return sorted(result)
