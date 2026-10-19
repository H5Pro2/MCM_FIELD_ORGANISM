"""Read-only verification of the K1 implementation package; never runs a replay."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINDING = ROOT / 'docs/S2UC_K1_IMPLEMENTIERUNGSBINDUNG_20261003.json'


def main():
    binding = json.loads(BINDING.read_text(encoding='utf-8'))
    for name, digest in binding['files'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('K1_PACKAGE_CHANGED:' + name)
    if sys.version != binding['python'] or sys.flags.optimize:
        raise RuntimeError('K1_RUNTIME_CHANGED')
    if hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest() != binding['executable_sha256']:
        raise RuntimeError('K1_EXECUTABLE_CHANGED')
    from tools.s2uc_t1_start_v3 import verify
    verify()
    print(json.dumps(dict(status='PASS_PACKAGE_INTEGRITY', files=len(binding['files']),
        comparison_executed=False, comparison_ready=False,
        blocker='24-case executor, source/mask sealing, neutral start qualification and new authorization pending')))


if __name__ == '__main__':
    main()
