"""Separate bounded counter for temporal banks; no modification of old 100-call path."""
import math,tracemalloc
from .core import need,vector

class Projector:
    def __init__(self,limit=390):
        need(limit==390,'FIXED_PROJECTION_LIMIT');self.limit=limit;self.calls=0;self.nj_calls=0;self.peak_workspace=0
    def __call__(self,payload,start):
        need(self.calls<self.limit and len(payload)==19200 and start>=0 and start%480==0,'PROJECTION_SCOPE')
        # Runtime imports precede measurement; fixed geometry prevents unbounded arrays.
        import numpy as np
        from dataclasses import asdict
        from mcm_field_organism.log_spectral_receptor import LogSpectralReceptor,LogSpectralConfig
        from mcm_field_organism.broadband_hearing_path import AuditoryReceptorState,AuditoryReceptorContact
        from tools import _s2nj_private_auditory_output_projection as nj
        need(not tracemalloc.is_tracing(),'EXCLUSIVE_WORKSPACE_METER')
        tracemalloc.start();tracemalloc.reset_peak()
        try:
            config=LogSpectralConfig();receptor=LogSpectralReceptor(config)
            self.calls+=1;values=receptor.analyze(np.frombuffer(payload,dtype='<f4'))
            state=AuditoryReceptorState('auditory',nj.RAW_GEOMETRY,start//480,start,start+4800,receptor.channel_ids,values,
                AuditoryReceptorContact.ACTIVE_ENERGY if any(values) else AuditoryReceptorContact.ACTIVE_ZERO)
            self.nj_calls+=1;projected=nj.project_auditory_half_v1(state,config=config,source_profile_digest=nj.RAW_PROFILE_DIGEST)
            peak=tracemalloc.get_traced_memory()[1];self.peak_workspace=max(self.peak_workspace,peak)
            need(peak<=16*1048576,'RECEPTOR_WORKSPACE_LIMIT')
            self.last=asdict(projected)
            return vector(projected.values)
        finally:tracemalloc.stop()
