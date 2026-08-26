from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.z4a_audio_receptor_source import (
    audit_z4a_audio_binding,
    z4a_audio_binding_json_value,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    audit = audit_z4a_audio_binding()
    payload = z4a_audio_binding_json_value(audit)
    payload["implementation_digests"] = {
        "controlled_audio_phase_source.py": _sha256(
            ROOT / "mcm_field_organism" / "controlled_audio_phase_source.py"
        ),
        "z4a_audio_receptor_source.py": _sha256(
            ROOT / "mcm_field_organism" / "z4a_audio_receptor_source.py"
        ),
    }
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
