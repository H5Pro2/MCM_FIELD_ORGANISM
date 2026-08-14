import argparse, json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order import build_callable_factory_call_execution_order
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order_acceptance import *
def build_callable_factory_call_execution_order_acceptance(i): return accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order(build_callable_factory_call_execution_order(i))
def main():
 p=argparse.ArgumentParser(); p.add_argument("--repeat-index",type=int,choices=(1,2,3),default=1); a=build_callable_factory_call_execution_order_acceptance(p.parse_args().repeat_index); print(json.dumps(public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order_acceptance_to_jsonable(a),indent=2)); return 0 if a.acceptance_complete else 1
if __name__=="__main__": raise SystemExit(main())
