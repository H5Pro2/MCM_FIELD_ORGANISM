"""Run the controlled history comparison for the passive memory candidate."""

from __future__ import annotations

from dataclasses import asdict
import json

from mcm_field_organism import (
    LocalSynapticMemoryConfig,
    run_passive_synaptic_memory_comparison,
)


def main() -> None:
    result = run_passive_synaptic_memory_comparison(
        LocalSynapticMemoryConfig(
            flexible_rate=0.5,
            stabilization_rate=0.25,
            release_rate=0.2,
            local_budget=0.8,
        )
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
