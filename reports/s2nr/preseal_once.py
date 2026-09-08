"""One NR preseal, followed only on completion by one offline verification."""
import json

from tools import _s2nr_private_source_binding as b
from tools import _s2nr_private_preseal_verification as v

RUN_ID="s2nr-source-preseal-20260908-01"


def main():
    out=b.preseal_once(RUN_ID)
    if (out/"failure.json").exists():
        print((out/"failure.json").read_text(encoding="ascii"))
        return 1
    try:
        result=v.verify_once(out)
    except Exception as exc:
        result=b.sealed(dict(run_id=RUN_ID,status="NOT_EVALUABLE",phase="READ_ONLY_BINDING_VERIFICATION",
            verification_calls=1,error_class=type(exc).__name__,
            code=str(exc) if isinstance(exc,b.S2NRBindingError) else "TECHNICAL_VERIFICATION_ERROR",
            main_gate_after=b.MAIN_GATE,retry=False),"failure_digest")
        b.publish(out/"verification-failure.json",result,b.MAX_METADATA_BYTES)
        print(json.dumps(result))
        return 1
    print(json.dumps({k:result[k] for k in ("run_id","status","source_count","event_count",
        "execution_digest","evaluation_digest","seal_digest","verification_digest")}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
