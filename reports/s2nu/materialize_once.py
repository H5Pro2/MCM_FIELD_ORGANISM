"""Authorized NU materialization and one offline verification; no evaluation."""
import json
from tools import _s2nu_private_receptor_materialization as m
from tools import _s2nu_private_materialization_verification as v


def main():
    m.require(not (m.ROOT/"reports/s2nu"/m.RUN_ID).exists(),"RUN_DIRECTORY_ALREADY_EXISTS")
    m.require(m.MAIN_GATE is False and m.b.MAIN_GATE is False and m.io.MAIN_GATE is False,"GATE_NOT_CLOSED")
    try:
        m.MAIN_GATE = True
        out,result = m.run_once()
    finally:
        m.close_gate()
    proof = v.verify_once(out)
    print(json.dumps(dict(run_id=m.RUN_ID,status=result["status"],counts=result["counts"],failure=result["failure"],
        record_digest=result["record_digest"],verification=proof,main_gate_after=m.MAIN_GATE,source_gate_after=m.b.MAIN_GATE)))
    return 0 if proof["status"] == "S2NU_MATERIALIZATION_VALID" else 1


if __name__ == "__main__":
    raise SystemExit(main())
