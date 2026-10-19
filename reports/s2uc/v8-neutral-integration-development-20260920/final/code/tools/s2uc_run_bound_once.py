"""Explicit, separately authorized S2-UC starter. It does not open its own gate."""
from pathlib import Path
from tools import _s2uc_run_binding as binding
from tools import _s2uc_source_binding as manifest_binding
from tools import _s2uc_run_entry as entry
from tools import _s2uc_source_adapter as adapter

def nu_payload_supplier(endpoint):
    """Deferred NU payload lookup; called only by SourceAdapter after prestart checks."""
    from tools import _s2nu_private_source_binding as nu
    rows, _ = binding.source.source_rows()
    row = rows[endpoint["source_id"]]
    return nu.pcm_window(nu.WindowSpec(int(row["stream_id"][1:]), int(row["window_ordinal"])))

DEFAULT_BINDING = Path("reports/s2uc/closure-preparation/S2UC_RUN_BINDING_20260920_FINAL_V14.json")

def start(output_directory, payload_supplier=nu_payload_supplier, *, authorize=False, binding_file=DEFAULT_BINDING):
    entry.MAIN_GATE = False
    if not authorize:
        raise ValueError("RUN_NOT_AUTHORIZED")
    binding.load_for_start(binding_file)
    raise ValueError("REAL_EXECUTION_DISABLED")
