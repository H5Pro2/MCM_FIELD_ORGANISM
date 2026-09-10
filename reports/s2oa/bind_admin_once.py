"""Create one new administrative binding, then one independent read-only check."""
import json
from tools import _s2oa_private_administrative_binding as b
from tools import _s2oa_private_administrative_verification as v


def main():
    try:
        out = b.bind_once()
        proof = v.verify_once(out)
        print(json.dumps(dict(run_id=b.RUN_ID,status=proof["status"],balance=proof["balance"],
                             verification_digest=proof["verification_digest"])))
        return 0
    except Exception as exc:
        print(json.dumps(dict(status="NOT_EVALUABLE",error_class=type(exc).__name__,
                             code=getattr(exc,"code","ADMINISTRATIVE_IO_ERROR"))))
        return 1
    finally:
        b.MAIN_GATE = False


if __name__ == "__main__":
    raise SystemExit(main())
