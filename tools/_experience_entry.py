"""Bound one-shot entry. Authorization is separate; default gate stays closed."""
from pathlib import Path
from tools import _experience_comparison as c
from tools import _experience_verification as v

MAIN_GATE = False


def run_once(binding, directory, *, qualification, current_inventory):
    global MAIN_GATE
    decoder = None
    path = None
    phase = "BINDINGS"
    try:
        c.need(MAIN_GATE is True,"MAIN_GATE_CLOSED")
        MAIN_GATE = False
        c.b.check_root(binding,"binding_digest")
        from reports.run_experience_comparison_once import inventory
        c.need(current_inventory==inventory(),"ACTIVE_SOURCES_CHANGED")
        c.need(binding["profile"]==c.PROFILE and binding["code_digest"]==c.b.digest(current_inventory)
               and qualification["status"]=="QUALIFIED" and qualification["test_calls"]==1
               and qualification["hashes_unchanged"] is True
               and binding["qualification_digest"]==c.b.digest(qualification),"ENTRY_BINDING_INVALID")
        c.budget(binding["reservations"])
        for name,receipt in qualification["files"].items():
            file=c.b.ROOT/binding["qualification_directory"]/name
            data=file.read_bytes()
            c.need(len(data)==receipt["bytes"] and c.b.hashlib.sha256(data).hexdigest()==receipt["sha256"],"QUALIFICATION_FILE_CHANGED")
        manifest = c.p.decode(binding["manifest"])
        c.need(manifest.code_digest==binding["code_digest"],"CODE_BINDING_INVALID")
        path = Path(directory)
        c.need(str(path.resolve())==binding["output"] and not path.exists() and path.parent.is_dir(),"OUTPUT_INVALID")
        path.mkdir()
        c.r.ng.ne.atomic_write(path/"binding.json",binding,65536)
        phase = "DECODER_INIT"
        decoder = c.media.uhd.open_decoder(manifest,binding["decoder_binding"])
        supplier = c.media.Materializer(manifest,decoder)
        phase = "COMPARISON"
        record = c.run_materialized(manifest,supplier,mode="MEDIA")
        c.r.ng.ne.atomic_write(path/"record.json",record,6291456)
        if record["status"]!="RECORDING_COMPLETE":
            return record
        c.need(supplier.counts==dict(payloads=44,audio=22,nj=22,visual=22,materialized_events=24),"MATERIALIZATION_COUNTS_INVALID")
        with (path/"verification.claim").open("xb") as f:
            f.write(b"once")
        phase = "VERIFICATION"
        proof = v.verify(record)
        c.r.ng.ne.atomic_write(path/"verification.json",proof,131072)
        phase = "EVALUATION"
        evaluation = c.evaluate(record,proof)
        c.r.ng.ne.atomic_write(path/"evaluation.json",evaluation,262144)
        return record
    except Exception as exc:
        if path is not None and path.exists():
            failure=dict(status="NOT_EVALUABLE",phase=phase,code=getattr(exc,"code",type(exc).__name__),
                detail=getattr(exc,"detail",None),message=str(exc),main_gate=False)
            c.r.ng.ne.atomic_write(path/"failure.json",failure,65536)
        raise
    finally:
        MAIN_GATE = False
        if decoder is not None:
            decoder.close()
