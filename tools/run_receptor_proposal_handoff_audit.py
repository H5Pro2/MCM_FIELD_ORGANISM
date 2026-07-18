from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.receptor_proposal_handoff_audit import (
    run_receptor_proposal_handoff_audit,
)


def main() -> int:
    print(
        json.dumps(
            {
                "audit": asdict(run_receptor_proposal_handoff_audit()),
                "field_advance_performed": False,
                "event_selection_or_reduction_applied": False,
                "contact_persistence_added": False,
                "organism_memory_added": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
