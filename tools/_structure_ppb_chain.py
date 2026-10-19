"""Nine bound presentations to three empty visual PPB banks, not a runtime."""
from dataclasses import asdict
import json
from mcm_field_organism import _ppb1_reference as ppb
from mcm_field_organism.receptor_contract import ReceptorContactFrame
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools import _ppb_visual_transition_table as diagnostic
from tools import _structure_source_binding as s

VERSION='structure-location.ppb-chain.v1'
SEQUENCES=((3,4,5),(0,1,2),(0,2,3))
MAIN_GATE=False


class ChainError(ValueError):
    pass


def need(value,code):
    if not value:raise ChainError(code)


def plain(value):
    return json.loads(s.raw(value))


def config():
    return build_s2jw_default_live_profile().profile.visual_config


def contact(cfg,source,values,chain):
    i=source['frame_index']
    need(type(i) is int and i>=0 and source['time']==[i,30],'SOURCE_TIME')
    need(len(values)==288,'VECTOR_SIZE')
    return ReceptorContactFrame('visual',cfg.geometry_id,f'structure.ppb.k{chain+1}.f{i}',
        f'structure.ppb.k{chain+1}',i,i+1,cfg.carrier_ids,tuple(values))


def generate(inputs,sources,binding,progress=None):
    cfg=config();chains=[];work=0
    if progress is not None:progress.update(chains=chains,completed=0,phase='INITIALIZE')
    for k,seq in enumerate(SEQUENCES):
        state=ppb.initial_ppb1_bank_state(cfg);states=[state.canonical_payload()];steps=[];births=[None]*4
        chains.append(dict(chain=k,states=states,steps=steps))
        for ordinal,index in enumerate(seq):
            frame=contact(cfg,sources[index],inputs[index],k)
            if progress is not None:progress['phase']='ADVANCE'
            pre=state.canonical_payload();result=ppb.advance_ppb1_bank(cfg,state,frame)
            state=result.poststate;post=state.canonical_payload()
            states.append(post)
            if progress is not None:
                progress['completed']+=1;progress['phase']='TABLE'
            data=dict(config=plain(asdict(cfg)),values=list(frame.values),pre=pre,post=post,
                frame=plain(asdict(frame)),observed=result.readout.canonical_payload(),births=plain(births))
            table=diagnostic.table(data);work+=table['primary_differences']
            next_births=plain(births)
            for n,slot in enumerate(post['slots']):
                if not slot['occupied']:next_births[n]=None
                elif slot['slot_id']==result.readout.slot_id and result.readout.event!='MATCHED':
                    next_births[n]=dict(chain=k,step=ordinal+1,source_digest=s.digest(sources[index]))
            need(len(s.raw(post))<=40960,'STATE_LIMIT')
            steps.append(dict(source_index=index,source_digest=s.digest(sources[index]),
                frame=data['frame'],pre_index=ordinal,post_index=ordinal+1,
                readout=data['observed'],table=table,births_before=plain(births),births_after=next_births))
            births=next_births
    record=dict(version=VERSION,status='RECORDING_COMPLETE',binding_digest=s.digest(binding),
        config=plain(asdict(cfg)),chains=chains,counts=dict(initializations=3,transitions=9,
        diagnostic_differences=work,productive_differences=work//2))
    need(work<=5184 and len(s.raw(record))<=1048576,'RECORD_LIMIT')
    return record


def verify(record,inputs,sources,binding):
    need(record['version']==VERSION and record['status']=='RECORDING_COMPLETE'
         and record['binding_digest']==s.digest(binding),'ROOT')
    cfg=config();need(record['config']==plain(asdict(cfg)) and len(record['chains'])==3,'CONFIG')
    total=0
    for k,(chain,seq) in enumerate(zip(record['chains'],SEQUENCES,strict=True)):
        need(chain['chain']==k and len(chain['states'])==4 and len(chain['steps'])==3,'CHAIN')
        initial=chain['states'][0]
        need(initial['accepted_step_count']==0 and initial['source_clock_id'] is None
             and initial['last_source_window_end_tick'] is None and initial['config_digest']==cfg.digest(),'INITIAL')
        need(initial['bank_id']==cfg.bank_id and len(initial['slots'])==4
             and all(not x['occupied'] and x['prototype_values']==[] and x['support_count'] is None
                     and x['last_selected_step'] is None for x in initial['slots']),'INITIAL_SLOTS')
        births=[None]*4
        for ordinal,index in enumerate(seq):
            step=chain['steps'][ordinal];pre=chain['states'][ordinal];post=chain['states'][ordinal+1]
            need(step['source_index']==index and step['source_digest']==s.digest(sources[index])
                 and step['pre_index']==ordinal and step['post_index']==ordinal+1,'ORDER')
            expected_frame=plain(asdict(contact(cfg,sources[index],inputs[index],k)))
            need(step['frame']==expected_frame and step['births_before']==births,'CONTACT_OR_GENERATION')
            readout=step['readout']
            need(readout['prestate_digest']==s.digest(pre) and readout['poststate_digest']==s.digest(post)
                 and readout['config_digest']==cfg.digest(),'STATE_DIGEST')
            native_input={key:expected_frame[key] for key in ('modality_id','geometry_id','clock_id',
                'window_start_tick','window_end_tick','carrier_ids','values')}
            need(readout['input_digest']==s.digest(native_input),'INPUT_DIGEST')
            data=dict(config=record['config'],values=list(inputs[index]),frame=step['frame'],
                pre=pre,post=post,observed=readout,births=births)
            proof=diagnostic.verify(data,step['table']);total+=proof['comparisons']
            selected=next(i for i,x in enumerate(post['slots']) if x['slot_id']==readout['slot_id'])
            slot=post['slots'][selected]
            need(readout['support_count']==slot['support_count'] and readout['prototype_values']==slot['prototype_values']
                 and readout['stabilized']==(slot['support_count']>=cfg.stable_after),'READOUT')
            matching=[r for r in step['table']['rows'] if r.get('matched')]
            distance=min((r['distance'],r['slot_id']) for r in matching)[0] if matching else None
            need(readout['match_distance']==distance,'MATCH_DISTANCE')
            expected_births=json.loads(s.raw(births))
            for i,x in enumerate(post['slots']):
                if not x['occupied']:expected_births[i]=None
                elif i==selected and readout['event']!='MATCHED':
                    expected_births[i]=dict(chain=k,step=ordinal+1,source_digest=s.digest(sources[index]))
            need(step['births_after']==expected_births,'POST_GENERATION');births=expected_births
            need(all(x['generation']==step['births_before'][i] for i,x in enumerate(step['table']['rows'])),'TABLE_GENERATION')
    need(total<=2592 and record['counts']==dict(initializations=3,transitions=9,
        diagnostic_differences=2*total,productive_differences=total),'WORK')
    return dict(status='EVIDENCE_VALID',record_digest=s.digest(record),evaluation_allowed=True,
        independent_differences=total,productive_replay=False)


def evaluate(record,proof,pair_rows):
    need(proof.get('evaluation_allowed') is True and proof.get('record_digest')==s.digest(record),'EVALUATION_GATE')
    summaries=[]
    for k,chain in enumerate(record['chains']):
        first,last=SEQUENCES[k][0],SEQUENCES[k][2]
        baseline=next(r for r in pair_rows if r['indices']==[first,last])
        step=chain['steps'][2]
        anchor=next(r for r in step['table']['rows'] if r['generation'] is not None and r['generation']['step']==1)
        summaries.append(dict(chain=k,original_pair_matched=baseline['matched'],
            original_pair_distance=baseline['distance'],anchor_slot=anchor['slot_id'],
            current_anchor_matched=anchor['matched'],current_anchor_distance=anchor['distance_hex'],
            anchor_decision_changed=baseline['matched']!=anchor['matched'],
            selected_slot=step['readout']['slot_id'],event=step['readout']['event'],
            selected_anchor=step['readout']['slot_id']==anchor['slot_id']))
    return dict(status='DESCRIPTIVE_ONLY',third_inputs=summaries,
        steps=[[dict(source_index=x['source_index'],event=x['readout']['event'],
            slot=x['readout']['slot_id'],support=x['readout']['support_count'],stable=x['readout']['stabilized'])
            for x in chain['steps']] for chain in record['chains']],
        full_memory_test=False,post_saturation_update_tested=False,replacement_tested=False)
