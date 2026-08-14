"""Run the private controlled AV previous-state probe once."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mcm_field_organism._controlled_av_previous_state_probe import (
    run_controlled_av_previous_state_probe,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_controlled_av_previous_state_probe()
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )


if __name__ == "__main__":
    main()
