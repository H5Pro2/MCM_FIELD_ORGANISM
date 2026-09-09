"""One source-only seal, then one independent read-only inspection."""
import json
from tools import _s2oa_private_source_binding as b
from tools import _s2oa_private_preseal_verification as v

RUN_ID="s2oa-source-preseal-20260909-01"


def main():
    try:
        b.MAIN_GATE=True
        out=b.preseal_once(RUN_ID)
    finally:
        b.MAIN_GATE=False
    if (out/"failure.json").exists():
        print((out/"failure.json").read_text(encoding="ascii"))
        return 1
    try:
        result=v.verify_once(out)
    except Exception as exc:
        result=b.sealed(dict(run_id=RUN_ID,status="NOT_EVALUABLE",phase="READ_ONLY_BINDING_VERIFICATION",
            verification_calls=1,error_class=type(exc).__name__,code=getattr(exc,"code","TECHNICAL_VERIFICATION_ERROR"),
            main_gate_after=False,retry=False),"failure_digest")
        b.publish(out/"verification-failure.json",result,b.MAX_METADATA_BYTES)
        print(json.dumps(result)); return 1
    print(json.dumps(result)); return 0


if __name__=="__main__":
    raise SystemExit(main())
