"""Run one canonical A0/C0 source diagnostic and print scalar JSON."""

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
from mcm_field_organism.controlled_av_source_pair_diagnostic import (
    controlled_av_source_pair_diagnostic_json_value,
    run_controlled_av_canonical_source_pair_diagnostic,
)


BROWSER_CACHE = WORKSPACE / ".playwright-browsers"
EXECUTABLE = (
    BROWSER_CACHE
    / "chromium_headless_shell-1234"
    / "chrome-headless-shell-win64"
    / "chrome-headless-shell.exe"
)
ASSETS = WORKSPACE / "tools" / "controlled_av_canonical_audio_world"


def main() -> int:
    from playwright.sync_api import sync_playwright

    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(BROWSER_CACHE)
    binding = bind_installed_browser_payload_runtime(
        requirements_path=WORKSPACE / "requirements-browser.txt",
        executable_path=EXECUTABLE,
        installation_root=BROWSER_CACHE,
    )
    receipt = run_controlled_av_canonical_source_pair_diagnostic(
        binding,
        asset_directory=ASSETS,
        playwright_factory=sync_playwright,
    )
    print(
        json.dumps(
            controlled_av_source_pair_diagnostic_json_value(receipt),
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
