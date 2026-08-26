"""Print the static W6-G browser execution preflight without launching a browser."""

from __future__ import annotations

import json
from pathlib import Path
import sys

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from mcm_field_organism.current_api import (  # noqa: E402
    bind_installed_browser_payload_runtime,
    prepare_s1b_causal_browser_execution_contract,
)


BROWSER_CACHE = WORKSPACE / ".playwright-browsers"
EXECUTABLE = (
    BROWSER_CACHE
    / "chromium_headless_shell-1234"
    / "chrome-headless-shell-win64"
    / "chrome-headless-shell.exe"
)
ASSETS = WORKSPACE / "tools" / "controlled_browser_payload_world"


def main() -> int:
    runtime_binding = bind_installed_browser_payload_runtime(
        requirements_path=WORKSPACE / "requirements-browser.txt",
        executable_path=EXECUTABLE,
        installation_root=BROWSER_CACHE,
    )
    preflight = prepare_s1b_causal_browser_execution_contract(
        runtime_binding,
        asset_directory=ASSETS,
        report_directory=WORKSPACE / "reports",
    )
    payload = preflight.canonical_payload()
    payload["contract_digest"] = preflight.digest()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if preflight.execution_permitted else 2


if __name__ == "__main__":
    raise SystemExit(main())
