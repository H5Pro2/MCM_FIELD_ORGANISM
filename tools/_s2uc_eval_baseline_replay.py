"""New evaluation-only replay, at most80 positions. Historical entry unchanged."""
from tools._s2uc_promotion_replay import *

def replay(values,profile,*,count,arm,evidence=None, check=lambda: None):
    require(type(count) is int and 4<=count<=80 and count%2==0,'PROMOTION_REPLAY_BOUND')
    require(arm in ('M','E','K','P'),'PROMOTION_ARM')
    if evidence is None:evidence={}
    events=[];forecasts=[];updates=[];rows=[];states=[];peaks=[]
    evidence.update(admissions=events,forecasts=forecasts,error_updates=updates,rows=rows,state_hashes=states)

    class Observed(PromotionAdapter):
        def _admit(self,frame):
            before=cells(self);stock=inventory(self)
            ticket=None if self._errors is None else bytes(self._errors.ticket)
            frozen=self.pending_prediction
            record=dict(frame=frame.ordinal,phase='admission',before=stock,cells_before=before,status='STARTED')
            events.append(record)
            meter.admission_bound(frame)
            # Whole system operation, including metadata/capture closures;
            # tracing is excluded, not production temporaries. The complete
            # retained/candidate/incoming reference union is measured above.
            tracing=sys.gettrace();sys.settrace(None)
            retained=owned(self);tracemalloc.start();base=tracemalloc.get_traced_memory()[0]
            failure=None
            try:super()._admit(frame)
            except BaseException as exc:
                failure=exc
                raise
            finally:
                _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
                peaks.append(retained+max(0,peak-base));sys.settrace(tracing)
                if failure is not None:
                    record.update(status='FAILED',error=type(failure).__name__+':'+str(failure),
                        terminal_closed=self.closed,cells_after=cells(self),after=inventory(self))
                    tb=failure.__traceback__
                    while tb:
                        local=tb.tb_frame.f_locals
                        if tb.tb_frame.f_code.co_name=='_admit' and tb.tb_frame.f_code.co_filename.endswith('_s2uc_promotion_ema.py'):
                            record['promotion_result']=local.get('event')
                        if 'stage' in local and 'index' in local:
                            record['failure_stage']=local['stage'];record['failure_index']=local['index']
                        tb=tb.tb_next
            after=inventory(self);expected=[]
            new=[t for t in after['retained'] if t['generation'] not in [x['generation'] for x in stock['retained']]]
            promoted=stock['candidate'] if new and after['candidate'] is None else None
            if promoted:
                require(len(new)==1 and new[0]['ordinals']==promoted['ordinals'] and
                    new[0]['values_sha256']==promoted['values_sha256'],'OBSERVER_PROMOTION_IDENTITY')
            for c in before:
                row=dict(c)
                if arm=='M' and promoted and c['role']==1 and c['generation']==promoted['generation']:
                    row.update(role=0,generation=new[0]['generation'])
                if self._generation_live(row['role'],row['generation']):expected.append(row)
            require(cells(self)==expected,'OBSERVER_PROMOTION_CELLS')
            require(self.pending_prediction is frozen and (self._errors is None or bytes(self._errors.ticket)==ticket),
                'OBSERVER_TICKET_OR_DECISION_CHANGED')
            record.update(status='COMPLETE',after=after,cells_after=cells(self))
        def _receipt(self,*args):
            receipt=super()._receipt(*args)
            raw=receipt.json_text;size=len(raw.encode())
            meter.receipt_bytes_peak=max(meter.receipt_bytes_peak,size)
            meter.receipt_transient_utf8_bytes_peak=max(meter.receipt_transient_utf8_bytes_peak,2*size)
            require(size<=16384 and 2*size<=32768,'PROMOTION_RECEIPT_BUDGET')
            if self.pending_prediction:
                p=self.pending_prediction;choice=p.persistence_values if arm=='P' else self.selected_values
                import json
                forecasts.append(dict(target=p.target_index,choice='CONTEXT' if choice is p.context_values else 'PERSISTENCE',
                    context_available=p.context_values is not None,receipt=json.loads(raw),cells_before=cells(self),
                    ticket=None if self._errors is None else list(TICKET.unpack(self._errors.ticket))))
            return receipt

    a=Observed(FactorRecencyArm(profile,'owner'),'stream',selection_policy='paired_error_ema_v1' if arm in ('M','E') else 'disabled',
        promotion_policy=POLICY if arm=='M' else 'disabled')
    ref=SignalApproxAdapter(FactorRecencyArm(profile,'owner'),'stream');source=GatedReplay(iter(values),profile)
    meter=PromotionMeter(a)
    try:
        for _ in range(count):
            check()
            sample=source.take(a)
            if a.pending_prediction:
                p=a.pending_prediction;choice=p.persistence_values if arm=='P' else a.selected_values
                require(choice is p.context_values or choice is p.persistence_values,'OUTPUT_ALIAS')
                rows.append(dict(target=sample.index,choice='CONTEXT' if choice is p.context_values else 'PERSISTENCE',
                    selected_mae=mae48(choice,sample.values),context_mae=None if p.context_values is None else mae48(p.context_values,sample.values),
                    persistence_mae=mae48(p.persistence_values,sample.values)))
                before=cells(a);ticket=None if a._errors is None else list(TICKET.unpack(a._errors.ticket))
                expected=[dict(c) for c in before]
                if ticket and ticket[-1] and a._generation_live(ticket[2],ticket[0]):
                    g,_,role,offset,quality,_,_=ticket
                    existing=next((c for c in expected if (c['role'],c['generation'],c['offset'],c['quality'])==(role,g,offset,quality)),None)
                    ec=rows[-1]['context_mae'];ep=rows[-1]['persistence_mae']
                    if existing is None:expected.append(dict(role=role,generation=g,offset=offset,quality=quality,ec=ec,ep=ep))
                    else:existing.update(ec=.5*existing['ec']+.5*ec,ep=.5*existing['ep']+.5*ep)
                if arm in ('M','E'):a.consume_feedback(sample)
                else:consume_prediction(a,sample)
                key=lambda c:(c['role'],c['generation'],c['offset'],c['quality'])
                require(sorted(cells(a),key=key)==sorted(expected,key=key),'OBSERVER_WRONG_ERROR_UPDATE')
                updates.append(dict(target=sample.index,phase='target_consumption',ticket=ticket,before=before,after=cells(a)))
                consume_prediction(ref,sample)
            sys.settrace(meter.trace)
            try:a.accept_perception(sample)
            finally:sys.settrace(None)
            ref.accept_perception(sample)
            require(state(a.arm)==state(ref.arm),'PROMOTION_MEMORY_CHANGED')
            states.append(digest(state(a.arm)))
        censored=a.pending_prediction.target_index
        a.finish_story();ref.release_prediction();ref.finish_story()
        require([e['frame'] for e in events]==list(range(1,count+1)),'PROMOTION_ADMISSIONS')
        require([r['target'] for r in rows]==list(range(3,count,2)) and censored==count+1,'PROMOTION_TARGETS')
        require(max(peaks,default=0)<=16384,'PROMOTION_PYTHON_BUDGET')
        resources={k:v for k,v in vars(meter).items() if k!='adapter'}
        evidence.update(arm=arm,frames=count,rows=rows,forecasts=forecasts,error_updates=updates,admissions=events,
            state_hashes=states,censored_target=censored,slots_released=a.pending_prediction is None,
            ema_cleared=a._errors is None or not any(a._errors.cells+a._errors.ticket),states_identical=True,
            resources=dict(meter=resources,additional_python_peak=max(peaks,default=0),
                heap_method='isolated whole admission incl promotion metadata/capture closure; observer trace excluded; complete pre-admission original-frame union bounds transient references',packed_bytes=416))
        return evidence
    finally:
        source.close()
        out_cleanup = out if "out" in locals() else evidence
        if not a.closed:a._terminate()
        if not ref.closed:ref._terminate()

        out_cleanup["terminal_cleanup"] = bool(a.closed and ref.closed and source.closed and
            all(not x.pair and not x.arm._forming and not x.arm._hints and not x.arm._retained_many
                and x.arm._candidate is None and x.pending_prediction is None for x in (a,ref)))
        meter.adapter = None  # Break observer/class closure retention after terminal release.
