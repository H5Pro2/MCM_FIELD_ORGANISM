"""Run the single W6-I controlled browser execution and print its receipt."""

from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import sys


WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from mcm_field_organism.current_api import (  # noqa: E402
    bind_installed_browser_payload_runtime,
    execute_s1b_causal_browser_one_shot,
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
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(BROWSER_CACHE)
    binding = bind_installed_browser_payload_runtime(
        requirements_path=WORKSPACE / "requirements-browser.txt",
        executable_path=EXECUTABLE,
        installation_root=BROWSER_CACHE,
    )
    contract = prepare_s1b_causal_browser_execution_contract(
        binding,
        asset_directory=ASSETS,
        report_directory=WORKSPACE / "reports",
    )
    receipt = execute_s1b_causal_browser_one_shot(
        contract,
        binding,
        asset_directory=ASSETS,
    )
    print(json.dumps(asdict(receipt), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
