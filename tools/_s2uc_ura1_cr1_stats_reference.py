"""Independent CR1 frame-window, rational aggregation and quantile oracle. No production stats import."""
import hashlib
from fractions import Fraction
from collections import Counter
from math import lcm,isfinite


def verify_matrix(data):
    if len(data)!=320000:raise ValueError('MATRIX_LENGTH')
    for offset,actual in enumerate(data):
        z,pos=divmod(offset,32);o,k=divmod(pos,16)
        text='MCM-URA1/bootstrap/v1/z='+str(z)+'/orientation='+str(o)+'/k='+str(k)
        expected=2*(int(hashlib.sha256(text.encode('ascii')).hexdigest()[:16],16)%16)+o
        if actual!=expected:raise ValueError('MATRIX_REFERENCE')
    return True


def interval(values,data):
    den=lcm(*(v.denominator for v in values));totals=[]
    for j in range(10000):
        hist=Counter(data[j*32:(j+1)*32]);total=0
        for index,n in hist.items():total+=n*values[index].numerator*(den//values[index].denominator)
        totals.append(total)
    totals.sort();answer=[]
    for numerator in (1,39):
        lower,weight=divmod(9999*numerator,40)
        answer.append(str(Fraction(totals[lower]*(40-weight)+totals[lower+1]*weight,40*32*den)))
    return answer


def verify(reports,data,actual,check=lambda:None):
    verify_matrix(data)
    # Validate independently before converting any outcome to a rational number.
    if len(reports)!=32 or {r['replicate'] for r in reports}!=set(range(1,33)):raise ValueError('REF_CASES')
    masks=('Q_early_post','Q_pre','Q_late_post','Q_all_post','Q','G_all','S','Q_X','Q_Y');store={};cumulative=[]
    categories={'eligible':(0,1,2),'warm':('none','cold','mixed','warm'),'same_output':(False,True),
                'choice':('both_persistence','mixed','same_context','different_context')}
    for r in sorted(reports,key=lambda x:x['replicate']):
        check();number=r['replicate'];rows=r['rows']
        if r['orientation']!=(number+1)%2 or not r['complete'] or len(rows)!=511:raise ValueError('REF_COMPLETE')
        groups={m:[] for m in masks};curve=[];running=Fraction(0)
        for index,row in enumerate(rows):
            if row['target']!=2*index+3:raise ValueError('REF_TARGETS')
            if any(type(row[a]) is not float or not isfinite(row[a]) or row[a]<0 for a in ('C','U')):raise ValueError('REF_ERROR')
            if any(row[k] not in choices for k,choices in categories.items()):raise ValueError('REF_DIAGNOSIS')
            entry=(number,row['target'],Fraction.from_float(row['C']),Fraction.from_float(row['U']),row)
            groups['G_all'].append(entry)
            if index%2==0:
                if row['cue'] not in ('X','Y'):raise ValueError('REF_CUE')
                groups['Q'].append(entry);groups['Q_'+row['cue']].append(entry)
                frame=row['target']
                if 515<=frame<=639:groups['Q_early_post'].append(entry)
                if 387<=frame<=511:groups['Q_pre'].append(entry)
                if 643<=frame<=1023:groups['Q_late_post'].append(entry)
                if 515<=frame<=1023:groups['Q_all_post'].append(entry)
            else:
                if row['cue'] is not None:raise ValueError('REF_CUE')
                groups['S'].append(entry)
            running+=entry[2]-entry[3];curve.append(str(running))
        if tuple(map(len,(groups[m] for m in masks)))!=(32,32,96,128,256,511,255,128,128):raise ValueError('REF_MASKS')
        store[number]=groups;cumulative.append(dict(replicate=number,targets=[2*i+3 for i in range(511)],delta=curve))
    def summary(entries):
        better=worse=equal=0;gain=Fraction(0);harm=Fraction(0);maximum=Fraction(0)
        for _,_,u,r,_ in reversed(entries):
            delta=u-r
            if delta<0:better+=1;gain-=delta
            elif delta>0:worse+=1;harm+=delta;maximum=max(maximum,delta)
            else:equal+=1
        count=better+worse+equal
        return dict(count=count,better=better,worse=worse,equal=equal,gain=str(gain),harm=str(harm),net=str(gain-harm),max_harm=str(maximum),mean_delta=str((harm-gain)/count) if count else None)
    secondary=[]
    for mask in masks:
        for orientation in (None,0,1):
            check();ids=list(range(1,33)) if orientation is None else list(range(orientation+1,33,2))
            entries=[];pair=[];umeans=[];rmeans=[]
            for number in ids:
                seq=store[number][mask];entries+=seq
                u=sum((x[2] for x in reversed(seq)),Fraction(0))/len(seq)
                r=sum((x[3] for x in reversed(seq)),Fraction(0))/len(seq)
                umeans.append(u);rmeans.append(r);pair.append(u-r)
            bal=summary(entries);worst=max(pair);mh=Fraction(bal['max_harm'])
            secondary.append(dict(mask=mask,orientation=orientation,means={'C':str(sum(umeans)/len(ids)),'U':str(sum(rmeans)/len(ids))},
                pairs=[str(v) for v in pair],mean=str(sum(pair)/len(ids)),worst_mean=str(worst),
                worst_stories=[ids[i] for i in range(len(ids)) if pair[i]==worst],
                maximum_harm_targets=[[n,t] for n,t,u,r,_ in entries if mh>0 and u-r==mh],**bal))
    values=[Fraction(x) for x in secondary[0]['pairs']];ci=interval(values,data)
    if Fraction(ci[1])<0:verdict='C_EARLY_POST_BETTER'
    elif Fraction(ci[0])>0:verdict='U_EARLY_POST_BETTER'
    else:verdict='INCONCLUSIVE'
    diagnosis=[]
    for key,labels in categories.items():
        for label in labels:diagnosis.append(dict(partition=key,label=label,**summary([x for n in range(1,33) for x in store[n]['Q_early_post'] if x[4][key]==label])))
    expected=dict(primary=dict(name='CR1:Q129-160:C-U',mean=secondary[0]['mean'],pairs=secondary[0]['pairs'],ci=ci,verdict=verdict),
                  secondary=secondary,diagnosis=diagnosis,cumulative=cumulative,bootstrap_sha256=hashlib.sha256(data).hexdigest())
    if actual!=expected:raise ValueError('STATISTICS_REFERENCE')
    return True
