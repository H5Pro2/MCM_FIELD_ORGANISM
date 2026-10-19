"""Post-terminal delivery: existing verified records only, no policy or statistics replay."""
import hashlib,json,sys,time
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.fw1_prepare import entry
from tools._s2uc_ura1_delta_fast_decode import Reader
from tools._s2uc_ura1_fs_accounting_v4 import inventory,treebytes
from tools import _s2uc_hx1_windows as win

def read(path):return json.loads(path.read_bytes())
def save(name,value):entry.write_exclusive(entry.TARGET/name,value)
def require(ok,why):
    if not ok:raise ValueError(why)

def main():
    started=time.monotonic();entry.install_job();folder=entry.TARGET;t=read(folder/'terminal.json')
    require(t['worker_ended'] and t['status'] in ('TERMINAL_COMPLETE','TECHNICAL_ABORT'),'NOT_TERMINAL')
    c,digest=entry.validate_binding(entry.CONFIGS['research'])
    require(digest=='e61664694a43c40adc1b74f8c680383e61c8e04b33ba98ecf61cbe056035bc99','BINDING')
    if (folder/'closure.json').exists():
        for name,v in read(folder/'closure.json').get('files',{}).items():require(entry.sha(folder/name)==v['sha256'],'CLOSURE:'+name)
    else:require(t['status']=='TECHNICAL_ABORT','MISSING_CLOSURE')
    if t['status']!='TERMINAL_COMPLETE':
        save('delivery-abort.json',dict(first_failure=t['first_failure'],completed_pairs=t['completed_cases'],active_pair=t['active_case'],executions=t.get('executions'),scientific_verdict=None,job=t.get('job'),cleanup=t.get('cleanup')))
        return
    require(t['completed_cases']==list(range(1,17)) and t['cleanup']=='CONFIRMED' and t['file_cleanup_confirmed'],'COMPLETENESS')
    require(all(t['executions'][k]==64 for k in ('policy_started','policy_completed','live_started','live_completed','archive_started','archive_completed')),'COUNTS')
    require(t['executions']['statistics_reference_completed']==1,'STATISTICS_COUNT')
    stat=read(folder/'statistics.json');ref=read(folder/'statistics-reference.json')
    require(all(stat[k]==ref[k] for k in ('mean','pairs','ci','informative','verdict')),'STATISTICS_AGREEMENT')
    manifest=read(folder/'sources-manifest.json');require(entry.sha(folder/'sources-manifest.json')==t['source_manifest_sha256'] and len(manifest['entries'])==32 and t['sources_sealed_before_policy'],'SOURCE_MANIFEST')
    for item in manifest['entries']:require(entry.sha(folder/item['path'])==item['sha256'],'SOURCE_HASH')
    groups={label:dict(gains=0,harms=0,ties=0,error_sum=F(),gain_sum=F(),harm_sum=F(),same_outputs=0,different_outputs=0,resets=0,effective_resets=0,effective_with_later_selection=0,cells_invalidated=0,offset0=0,offset1=0,cells_relearned_before_next_reset=0,cells_without_later_update=0) for label in ('A','B')}
    peaks={};conditions=[]
    save('delivery-analysis-start.json',dict(policy=0,statistics_replays=0,descriptive_archive_decodes_planned=32))
    for number in range(1,33):
        pair=(number+1)//2;label='A' if number%2 else 'B';g=groups[label]
        s=read(folder/f'case-{number:02d}-summary.json')
        require(s['complete'] and s['cleanup'] and s['stock_equal'] and s['targets']==list(range(3,1024,2)) and s['integrity']=='PASS_DELTA_INTEGRITY','CONDITION')
        for a,b in zip(s['KEEP'],s['RESET'],strict=True):
            d=F(a)-F(b);g['error_sum']+=d
            if d<0:g['gains']+=1;g['gain_sum']-=d
            elif d>0:g['harms']+=1;g['harm_sum']+=d
            else:g['ties']+=1
        r=s['resources']
        for k in ('dictionary','nodes','edges','indices','collections','record_peak','temp_peak','encoded_bytes','gzip_bytes'):peaks[k]=max(peaks.get(k,0),r[k])
        for mode in ('KEEP','RESET'):
            for k in ('additional_python_peak','receipt_bytes_peak','utf8_upper','packed','whole_conservative_peak'):peaks[k]=max(peaks.get(k,0),r[mode][k])
            peaks['originals']=max(peaks.get('originals',0),r[mode]['boundary_peaks']['originals']);peaks['output_slots']=max(peaks.get('output_slots',0),r[mode]['boundary_peaks']['output_slots'])
        reader=Reader((folder/f'case-{number:02d}.gz').read_bytes());root=reader.value(reader.doc['root'])
        def records(mode,name):return (json.loads(v) for v in reader.records(root[mode][name]['$sequence']))
        for a,b in zip(records('KEEP','forecasts'),records('RESET','forecasts'),strict=True):
            require(a['index']==b['index'],'FORECAST_ALIGNMENT')
            if a['index']<1024:g['same_outputs' if a['output']==b['output'] else 'different_outputs']+=1
        updates={}
        for row in records('RESET','rows'):
            for u in row['updates']:
                if u['live']:updates.setdefault(tuple(u['key']),[]).append(row['target'])
        for idx,e in enumerate(s['resets']):
            g['resets']+=1;g['effective_resets']+=int(e['deleted']>0);g['effective_with_later_selection']+=int(e['deleted']>0 and e['end']+3<=1023);g['cells_invalidated']+=e['deleted']
            following=next((x['end'] for x in s['resets'][idx+1:] if x['generation']==e['generation']),1025)
            for off in e['offsets']:
                g[f'offset{off}']+=1
                relearned=any(e['end']<target<following for target in updates.get((0,e['generation'],off),[]))
                g['cells_relearned_before_next_reset' if relearned else 'cells_without_later_update']+=1
        conditions.append(dict(case=number,pair=pair,condition=label,stock_equal=True,integrity=s['integrity'],cleanup=True,targets=511))
        del reader,root,s,updates
    for label,g in groups.items():
        require(g['gains']+g['harms']+g['ties']==8176 and g['same_outputs']+g['different_outputs']==8176,'DESCRIPTIVE_DENOMINATOR')
        g['mean_difference']=str(g['error_sum']/8176)
        for key in ('error_sum','gain_sum','harm_sum'):g[key]=str(g[key])
    save('descriptive.json',dict(groups=groups,scope='All prescribed targets; descriptive only; no additional significance tests',archive_decodes=32,policy=0,reference_replays=0,statistics_replays=0))
    save('verification.json',dict(status='PASS',prestart_sha256=digest,source_manifest_sha256=t['source_manifest_sha256'],source_count=32,conditions=conditions,statistics_equal=True,executions=t['executions'],code_bindings=len(c['files']),qualification_bindings=len(c['qualification'])))
    limits=dict(dictionary=4194304,nodes=65536,edges=262144,indices=65536,collections=16,record_peak=262144,temp_peak=67108864,encoded_bytes=4194304,gzip_bytes=524288,additional_python_peak=16384,receipt_bytes_peak=16384,utf8_upper=32768,packed=416,originals=18,output_slots=2)
    require(all(peaks[k]<=v for k,v in limits.items()),'RESOURCE_BOUND')
    save('delivery-resources.json',dict(run_seconds=t['seconds'],run_job=t['job'],peaks=peaks,limits=limits,postprocessing_seconds=time.monotonic()-started,postprocessing_job=win.snapshot(),filesystem_before_report=inventory(folder)['groups'],extra_policy=0))
    print(json.dumps(dict(statistics=stat,descriptive=groups,resources=peaks,postprocessing_seconds=time.monotonic()-started)))

if __name__=='__main__':main()
