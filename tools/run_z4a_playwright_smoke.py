from __future__ import annotations

import json
import os
from pathlib import Path
import sys


WORKSPACE = Path(__file__).parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from mcm_field_organism.z4a_playwright_runtime_binding import (
    bind_installed_z4a_playwright_runtime,
)
from mcm_field_organism.z4a_playwright_smoke import (
    run_z4a_playwright_smoke,
    z4a_playwright_smoke_json_value,
)


BROWSER_CACHE = WORKSPACE / ".playwright-browsers"
ASSETS = WORKSPACE / "tools" / "z4a_browser_world_v2"


def main() -> int:
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(BROWSER_CACHE)
    root = BROWSER_CACHE / "chromium_headless_shell-1234"
    executables = tuple(root.rglob("chrome-headless-shell.exe"))
    if len(executables) != 1:
        raise RuntimeError("bound Chromium headless shell is not unique")
    binding = bind_installed_z4a_playwright_runtime(
        manifest_entry_name="chromium-headless-shell",
        executable_path=executables[0],
        installation_root=root,
    )
    receipt = run_z4a_playwright_smoke(binding, asset_directory=ASSETS)
    print(
        json.dumps(
            z4a_playwright_smoke_json_value(receipt),
            allow_nan=False,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
