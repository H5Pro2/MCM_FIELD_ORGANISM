"""One authorized first-window decoder probe; no receptor/system imports."""
from dataclasses import make_dataclass
import hashlib
import io
import json
from pathlib import Path
import sys
import traceback
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "reports/s2oe/decoder-first-window-diagnostic-20260911-02"
COMMON = ROOT / "reports/s2oe/media-player-run-binding-20260911-02/common.json"
COMMON_SHA = "7d306c851a74eeccb00c6aca3b5397372c6d8e450f217cb12a457f08bae5e6d3"
FILES = ("tools/_s2oe_decoder_worker.py", "tools/_s2oe_media_decoder.py",
    "tests/s2oe_diagnostic_worker.py", "tests/test_s2oe_diagnostic.py",
    "reports/diagnose_media_first_window.py", "reports/verify_media_first_window.py")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(name, value):
    raw = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    with (OUT / name).open("xb") as stream:
        stream.write(raw)


def inventory():
    return {p: dict(bytes=(ROOT/p).stat().st_size,
        sha256=digest((ROOT/p).read_bytes())) for p in FILES}


def checked():
    bound = json.loads((OUT/"binding.json").read_text())
    assert bound["code"] == inventory(), "CODE_BINDING_CHANGED"
    assert digest(COMMON.read_bytes()) == COMMON_SHA, "SOURCE_BINDING_CHANGED"
    return bound


def prepare():
    OUT.mkdir(exist_ok=False)
    raw = COMMON.read_bytes()
    assert digest(raw) == COMMON_SHA
    common = json.loads(raw)
    code = inventory()
    # Complete files plus bounded diagnostic/qualification closure, not media stock.
    ledger = dict(code_bytes=sum(v["bytes"] for v in code.values()),
        historical_common_bytes=len(raw), binding_reserve=16384,
        qualification_reserve=16384, diagnostic_reserve=16384,
        verification_reserve=8192, report_reserve=8192)
    assert sum(ledger.values()) < 262144
    save("binding.json", dict(version="s2oe.first-window-diagnostic.v1", code=code,
        source=common["manifest"]["source"], common_sha256=COMMON_SHA,
        selection=dict(repeat=1, window=0), commit_bytes=536870912,
        qualification_id="decoder-phase-neutral-20260911-02",
        tests=["original_exception", "allocation_exception", "limit_does_not_erase_original",
            "abrupt_end_retains_phase_not_exception", "bounded_diagnostics_and_unchanged_limits"],
        ledger=ledger, total_reserved_bytes=sum(ledger.values()),
        no_receptors=True, no_optimization=True))


def qualify():
    checked()
    with (OUT/"qualification.claim").open("xb") as stream:
        stream.write(b"once\n")
    suite = unittest.defaultTestLoader.discover(str(ROOT/"tests"), pattern="test_s2oe_diagnostic.py")
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    with (OUT/"qualification.log").open("x", encoding="utf-8") as stream:
        stream.write(log.getvalue())
    save("qualification.json", dict(status="QUALIFIED" if result.wasSuccessful()
        and result.testsRun == 5 else "NOT_QUALIFIED", tests=result.testsRun,
        errors=len(result.errors), failures=len(result.failures),
        log_sha256=digest((OUT/"qualification.log").read_bytes())))
    assert result.wasSuccessful() and result.testsRun == 5
    assert sum((OUT/p).stat().st_size for p in ("qualification.claim",
        "qualification.log", "qualification.json")) <= 16384


def diagnose():
    bound = checked()
    assert json.loads((OUT/"qualification.json").read_text())["status"] == "QUALIFIED"
    with (OUT/"diagnostic.claim").open("xb") as stream:
        stream.write(b"one select(1, 0)\n")
    from tools import _s2oe_decoder_worker as w
    source = dict(bound["source"])
    for key in ("video_time_base", "audio_time_base", "frame_rate", "video_size"):
        source[key] = tuple(source[key])
    source = make_dataclass("BoundSource", [(k, object) for k in source], frozen=True)(**source)
    worker = None
    record = dict(status="NOT_EVALUABLE", selection=bound["selection"],
        source_binding_sha256=COMMON_SHA, binding_sha256=digest((OUT/"binding.json").read_bytes()),
        decoder_calls=0, receptors=0, nj=0, field=0, memory=0, runtime=0)
    try:
        worker = w.WorkerDecoder(source)
        record["decoder_calls"] = 1
        pcm, rgb, pts, next_pts = worker.select(1, 0)
        record.update(status="DECODER_WINDOW_COMPLETE", pts=pts, next_pts=next_pts,
            output_shapes=[list(pcm.shape), list(rgb.shape)],
            output_bytes=[pcm.nbytes, rgb.nbytes])
        del pcm, rgb
    except BaseException as exc:
        record["failure"] = dict(code=getattr(exc, "code", None),
            exception_type=type(exc).__name__, detail=getattr(exc, "balance", None),
            traceback=[dict(file=Path(f.filename).name, line=f.lineno, function=f.name)
                for f in traceback.extract_tb(exc.__traceback__)[-6:]])
    finally:
        if worker:
            try:
                worker.close()
            except BaseException as exc:
                record["close_error"] = type(exc).__name__
            record.update(resources=worker.resources, counters=worker.counters,
                last_confirmed_phase=worker.last_confirmed_phase)
        record["gates_opened"] = False
        save("diagnostic.json", record)
    assert (OUT/"diagnostic.json").stat().st_size <= 16384


if __name__ == "__main__":
    {"prepare": prepare, "qualify": qualify, "diagnose": diagnose}[sys.argv[1]]()
