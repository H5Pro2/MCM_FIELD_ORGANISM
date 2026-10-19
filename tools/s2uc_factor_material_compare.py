"""Read completed material into the unchanged three-arm observer."""
from tools.s2uc_factor_material import read_verified
from tools._s2uc_origin_judge import Truth
from tools._s2uc_factor_continuation_compare import compare,summarize

def evaluate_export(folder,spec,partition,profile_definition):
    rows=read_verified(folder,spec,partition,profile_definition);results={}
    for cid,row in rows.items():
        roots={tuple(range(4*i+1,4*i+5)):spec['episodes'][k]['root'] for i,k in enumerate(spec['cases'][cid]['learn'])}
        results[cid]=compare(row['values'],row['profile']['digest'],Truth(row['truth'],row['positive'],roots,cid))
    return dict(cases=results,summary=summarize(results),semantics=dict(
        concrete='rows[policy].context_mae; null means no concrete prediction',
        fallback='observer_hybrid_mae and full_rows legacy/scaled use persistence only on abstention',
        persistence='persistence_mae is independently reported',
        learning='learning_rows/learning_targets separate, not included in primary summary'))
