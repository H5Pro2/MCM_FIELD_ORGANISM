"""Codec-only qualification of two existing archives, never runs policies."""
import hashlib
import io
import json
import unittest
from pathlib import Path
from tests import test_s2uc_ura1_archive_codec as tests


def main():
    root = Path(__file__).resolve().parents[1]
    out = root/'reports/s2uc/ura1-codec-development-20261014-01'
    if out.exists():
        raise FileExistsError(out)
    stream = io.StringIO()
    class Result(unittest.TextTestResult):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs); self.ids = []
        def addSuccess(self, test):
            self.ids.append(dict(id=test.id(), status='PASS')); super().addSuccess(test)
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Result).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(tests.CodecTests))
    print(stream.getvalue())
    if not result.wasSuccessful():
        raise SystemExit(1)
    out.mkdir()
    def save(name, value):
        (out/name).write_text(json.dumps(value, sort_keys=True, indent=2)+'\n', encoding='utf-8')
    for name, (_, _, blob) in tests.CodecTests.cases.items():
        (out/(name+'.dag.json.gz')).write_bytes(blob)
    (out/'tests.txt').write_text(stream.getvalue(), encoding='utf-8')
    save('tests.json', dict(tests=result.testsRun, ids=result.ids, status='PASS_CODEC_ONLY'))
    save('evidence.json', tests.FACTS)
    files = ['tools/_s2uc_ura1_archive_encode.py', 'tools/_s2uc_ura1_archive_decode.py',
             'tests/test_s2uc_ura1_archive_codec.py', 'tools/s2uc_ura1_archive_codec_qualify.py']
    save('binding.json', dict(files={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in files},
         source_closure_sha256=hashlib.sha256((tests.SOURCE/'closure.json').read_bytes()).hexdigest(),
         research_ready=False, policy_runs=0))
    print(json.dumps(tests.FACTS, indent=2))


if __name__ == '__main__':
    main()
