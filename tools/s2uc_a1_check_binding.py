"""Read-only A1 implementation binding verification. No qualification/replay."""
import hashlib
import json
from pathlib import Path
import sys


def main():
    root=Path(__file__).resolve().parents[1]
    p=root/'docs/S2UC_A1_IMPLEMENTIERUNGSBINDUNG_20261004.json'
    b=json.loads(p.read_text(encoding='utf-8'))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    if sys.flags.optimize or sys.version!=b['python'] or sha(Path(sys.executable))!=b['executable_sha256']:
        raise ValueError('RUNTIME_BINDING')
    for n,h in b['files'].items():
        if sha(root/n)!=h:raise ValueError('A1_BINDING_CHANGED:'+n)
    print(json.dumps(dict(status='PASS_A1_BINDING',files=len(b['files']),replay=False)))


if __name__=='__main__':main()
