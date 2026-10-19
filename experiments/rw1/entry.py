"""Prepared RW1 CLI. Research requires a future externally supplied permission."""
import os,sys,argparse
from pathlib import Path
for n in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[n]='1'
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from experiments.rw1 import gateway

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--fixtures',metavar='EXCLUSIVE_ATTEMPT');g.add_argument('--research',action='store_true')
    g.add_argument('--worker');g.add_argument('--seal',metavar='COMPLETED_FIXTURE_FOLDER')
    p.add_argument('--authorization');a=p.parse_args()
    if a.worker:return gateway.worker(a.worker)
    if a.seal:gateway.seal(a.seal);return 0
    return gateway.supervise('research' if a.research else 'fixtures',a.fixtures,a.authorization)
if __name__=='__main__':raise SystemExit(main())
