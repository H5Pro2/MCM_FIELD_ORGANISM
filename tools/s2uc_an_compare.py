"""PCM/NJ export observer. No implicit calibration or parameter search."""
import math
import sys
from tools.s2uc_an_material import read_verified, need
from tools.s2uc_ar_compare import GRID, named, select_parameters, selection_rows
from tools._s2uc_origin_judge import Truth
from tools._s2uc_signal_approx_compare import compare, report


def calibration_epsilon(folder,spec,part):
    need(spec['kind']=='DEV' and spec['calibration'] is not None,'EVAL_CALIBRATION_FORBIDDEN')
    _,frames=read_verified(folder,spec,part)
    return _epsilon(frames)


def _epsilon(frames):
    need(len(frames)==8,'EIGHT_CALIBRATION_PROJECTIONS_REQUIRED')
    value=max(math.fsum(abs(x) for x in v)/48 for v in frames)
    need(math.isfinite(value) and value>=sys.float_info.min,'CALIBRATION_NOT_NORMAL_POSITIVE')
    return value


def evaluate_export(folder,spec,part,*,epsilon,tau,measure=False):
    rows,calibration=read_verified(folder,spec,part);cases={}
    if spec['kind']=='DEV':need(epsilon==_epsilon(calibration),'DEV_EPSILON_MUST_MATCH_NJ_CALIBRATION')
    for cid,row in rows.items():
        roots={tuple(range(4*i+1,4*i+5)):spec['episodes'][k]['root'] for i,k in enumerate(spec['cases'][cid]['learn'])}
        cases[cid]=compare(row['values'],row['profile_digest'],Truth(row['truth'],row['positive'],roots,cid),
            epsilon=epsilon,tau=tau,measure=measure)
    return dict(cases=named(cases),summary=named(report(cases)),epsilon=epsilon,tau=tau,
        partition=part,continuation_policy_for_both='legacy_v1',factor_scaled_v1_used=False,
        semantics='Concrete context MAE is null on abstention; full observer schema uses context else persistence.')
