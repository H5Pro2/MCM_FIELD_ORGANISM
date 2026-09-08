"""Authorized single NT comparison, one verification, then conditional evaluation."""
import json
from tools import _s2nt_private_comparison_run as run

RUN_ID = "s2nt-diagnostic-comparison-20260908-01"


def main():
    run.c.require(run.MAIN_GATE is False and run.b.MAIN_GATE is False,"GATE_INVALID")
    run.c.require(not (run.b.ROOT/"reports/s2nt"/RUN_ID).exists(),"RUN_ALREADY_EXISTS")
    run.MAIN_GATE = True
    try:
        out = run.run_main_once(RUN_ID)
    finally:
        run.MAIN_GATE = False
    verification = run.verify_file_once(out)
    assessment = None
    if verification["status"] == "S2NT_COMPARISON_VERIFIED" and verification["evaluation_allowed"] is True:
        assessment = run.evaluate_file_once(out)
    print(json.dumps(dict(run_id=RUN_ID,verification=verification,assessment=assessment,
        main_gate_after=run.MAIN_GATE,source_gate_after=run.b.MAIN_GATE)))
    return 0 if assessment is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
