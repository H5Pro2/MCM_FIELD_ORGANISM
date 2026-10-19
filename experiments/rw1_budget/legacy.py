"""Instrument the unchanged RW1 Budget using only remapped artificial roots."""
import time
from unittest.mock import patch
from .workload import *
from experiments.rw1 import common as original
from experiments.as480 import common as io

class MeasuredLegacy:
    def __init__(self,target):
        self.target=target;self.metrics=dict(scan_calls=0,scan_seconds=0.,serialization_calls=0,serialization_seconds=0.,write_calls=0,write_seconds=0.)
        self.context=[];self.origsize=original.size;self.origraw=io.raw;self.origexclusive=io.exclusive;self.origappend=io.append
    def __enter__(self):
        def scan(p):
            t=time.perf_counter()
            try:return self.origsize(p)
            finally:self.metrics['scan_calls']+=1;self.metrics['scan_seconds']+=time.perf_counter()-t
        def serialize(x):
            t=time.perf_counter()
            try:return self.origraw(x)
            finally:self.metrics['serialization_calls']+=1;self.metrics['serialization_seconds']+=time.perf_counter()-t
        def write(fn,p,x):
            t=time.perf_counter();s=self.metrics['serialization_seconds']
            try:return fn(p,x)
            finally:self.metrics['write_calls']+=1;self.metrics['write_seconds']+=time.perf_counter()-t-(self.metrics['serialization_seconds']-s)
        changes={'ROOT':BASE,'OLD':BASE/'old','DOC':BASE/'doc','PREP':BASE/'prep','CONTRACT':BASE/'contract.fixture','TARGET':self.target,
                 'size':scan,'raw':serialize,'exclusive':lambda p,x:write(self.origexclusive,p,x),'append':lambda p,x:write(self.origappend,p,x)}
        for k,v in changes.items():
            ctx=patch.object(original,k,v);ctx.start();self.context.append(ctx)
        ctx=patch.object(io,'raw',serialize);ctx.start();self.context.append(ctx)
        self.budget=original.Budget(self.target);return self
    def apply(self,action):
        value=materialize_action(action)
        if action['kind']=='append':self.budget.event(action['name'],value)
        else:self.budget.save(action['name'],value)
    def __exit__(self,*args):
        for ctx in reversed(self.context):ctx.stop()
