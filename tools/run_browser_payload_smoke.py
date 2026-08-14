"""Run the single bound generic browser payload smoke and print scalar JSON."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys


WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from mcm_field_organism.browser_payload_runtime import (
    bind_installed_browser_payload_runtime,
)
from mcm_field_organism.browser_payload_smoke import (
    browser_payload_smoke_json_value,
    run_browser_payload_smoke,
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
    receipt = run_browser_payload_smoke(binding, asset_directory=ASSETS)
    print(
        json.dumps(
            browser_payload_smoke_json_value(receipt),
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
