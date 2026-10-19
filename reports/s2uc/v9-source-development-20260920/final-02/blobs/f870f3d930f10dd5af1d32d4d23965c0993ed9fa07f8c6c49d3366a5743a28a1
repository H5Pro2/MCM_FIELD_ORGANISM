"""V9 admission boundaries over the single V8 lifecycle and V7 publisher."""
from tools import _s2uc_source_execution_binding as binding
from tools import _s2uc_source_context_v9 as context
from tools import _s2uc_resources_v9 as resources
from tools import _s2uc_execution_v8 as core
from tools import _s2uc_run_entry as legacy_entry


class _Publication(core._Publication):
    limits, reserves = resources.LIMITS, resources.RESERVES
    account = staticmethod(resources.account)
    version, proof_version = "s2uc.neutral-integration.v9", "s2uc.verification-evaluation.v9"

    def __init__(self, path, initial):
        super().__init__(path, initial)
        self.execution.update(contract_id=resources.CONTRACT_ID, scope="NEUTRAL_NONZERO_V9",
                              candidate_gain_loss_status="NOT_MEASURED")


def run_neutral(binding_path, supplier, *, run_id, output_directory):
    result = core._run(binding_path, supplier, run_id=run_id, output_directory=output_directory,
                       validate=binding.validate, publisher=_Publication)
    return {**result, "scope": "NEUTRAL_NONZERO_V9", "candidate_gain_loss_status": "NOT_MEASURED",
            "real_execution_authorized": False}


def start_real(source_context):
    """Structural success cannot authorize a real run, even with forged OK claims."""
    legacy_entry.MAIN_GATE = False
    context.validate_source_context(source_context)
    raise ValueError("V9_REAL_EXECUTION_DISABLED")
