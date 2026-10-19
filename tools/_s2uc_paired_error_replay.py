"""Finite connection; standard cap stays64, explicit EMA contract permits200."""
from tools._s2uc_paired_error_ema import PairedErrorAdapter, mae48, require
from tools._s2uc_signal_approx_adapter import SignalApproxAdapter
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_continuation_adapter import consume_prediction
from tools._s2uc_origin_judge import GatedReplay
from tools.s2uc_continuous_comparison import state

EXTENSION='paired_error_ema_200_v1'


def replay(values,profile,*,count,arm='E',bounded_contract=None):
    require(type(count) is int and ((bounded_contract is None and 3<=count<=64) or
        (bounded_contract==EXTENSION and count==200)),'REPLAY_BOUND')
    require(arm in ('E','K','P'),'REPLAY_ARM')
    a=PairedErrorAdapter(FactorRecencyArm(profile,'owner'),'stream',
        selection_policy='paired_error_ema_v1' if arm=='E' else 'disabled')
    ref=SignalApproxAdapter(FactorRecencyArm(profile,'owner'),'stream')
    source=GatedReplay(iter(values),profile)
    rows=[];admitted=[];original=a._admit
    def admit(frame):
        admitted.append(frame.ordinal)
        original(frame)
    a._admit=admit
    try:
        for _ in range(count):
            sample=source.take(a)
            if a.pending_prediction is not None:
                p=a.pending_prediction
                chosen=p.persistence_values if arm=='P' else a.selected_values
                require(chosen is p.context_values or chosen is p.persistence_values,'OUTPUT_ALIAS')
                score=mae48(chosen,sample.values)
                rows.append(dict(target=sample.index,choice='CONTEXT' if chosen is p.context_values else 'PERSISTENCE',
                    selected_mae=score,persistence_mae=mae48(p.persistence_values,sample.values),
                    context_mae=None if p.context_values is None else mae48(p.context_values,sample.values)))
                if arm=='E':a.consume_feedback(sample)
                else:consume_prediction(a,sample)
                consume_prediction(ref,sample)
            a.accept_perception(sample);ref.accept_perception(sample)
            require(state(a.arm)==state(ref.arm),'MEMORY_STATE_CHANGED')
        require(admitted==list(range(1,count+1)),'ADMISSION_COUNT')
        censored=a.pending_prediction.target_index if a.pending_prediction is not None else None
        a.release_prediction();ref.release_prediction()
        a.finish_story();ref.finish_story()
        require(state(a.arm)==state(ref.arm),'FINAL_MEMORY_CHANGED')
        return dict(arm=arm,frames=count,rows=rows,censored_target=censored,states_identical=True,
            admitted=admitted,slots_released=a.pending_prediction is None,
            ema_cleared=a._errors is None or not any(a._errors.cells+a._errors.ticket),pull_log=source.log)
    finally:
        source.close()
        if not a.closed:a._terminate()
        if not ref.closed:ref._terminate()
