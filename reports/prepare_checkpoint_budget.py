"""Pure format/ledger arithmetic. No project imports, payloads or test execution."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def size(value):
    return len(json.dumps(value, ensure_ascii=True, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("ascii"))


def field_upper():
    # String placeholders include quotes: conservative for <=24-byte float text.
    number = "9" * 24
    positions = [(0, i) for i in range(48)] + [(1 + i // 36, i % 36) for i in range(288)]
    ids = [f"organism.mcm_field.auditory.n{i}" for i in range(48)]
    ids += [f"organism.mcm_field.visual.n{i}" for i in range(288)]
    at = dict(zip(positions, ids))
    offsets = ((-1, 0), (0, -1), (0, 1), (1, 0))
    neurons = []
    samples = 0
    for position, identity in zip(positions, ids):
        local = []
        for dr, dc in offsets:
            other = at.get((position[0] + dr, position[1] + dc))
            if other is not None:
                local.append(dict(sample_id="sample." + other, source_field_id="organism.mcm_field",
                    source_tick=28, relative_position=[dr, dc], activation=number, afterimage=number))
        samples += len(local)
        neurons.append(dict(neuron_id=identity, field_id="organism.mcm_field", modality_id="organism",
            geometry_id="organism.shared.v1", position=list(position), activation=number,
            afterimage=number, perception=dict(tick=28, receptor_contact=number, local_samples=local)))
    docks = []
    for modality, values in (("auditory", ids[:48]), ("visual", ids[48:])):
        docks.append(dict(dock_id="dock." + modality, modality_id=modality,
            receptor_geometry_id="x" * 80, pairs=[["x" * 80, identity] for identity in values]))
    value = dict(schema_version=1, layer=dict(layer_id="organism.mcm_layer",
        sample_offsets=list(offsets), periodic_axes=[], receptor_dock_ids=ids, neurons=neurons),
        docks=docks, last_distribution=dict(field_time=dict(clock_id="s2ob-caller-field-clock",
            window_start_tick=9999999999, window_end_tick=9999999999), contacts=[]))
    return dict(bytes=size(value), neuron_bytes=size(neurons), dock_bytes=size(docks),
        remaining_fields_bytes=size(value)-size(neurons)-size(docks), neurons=336, samples=samples,
        float_token_cap=24, identifier_cap_for_carriers_and_geometry=80,
        schema=1, max_events=28, field_limit=524288,
        scope="Fixed OB geometry and neutral transient field only; not every SharedMCMField schema.")


def record_upper(events, formations, scans, audio):
    parts = dict(memory_states=(formations+1)*98304, inputs=events*16384,
        steps=events*16384, scans=scans*32767, nj=audio*1024,
        formations=formations*1536, generations=formations*1536, record_metadata=32768)
    return dict(parts=parts, total=sum(parts.values()))


def prepare():
    field = field_upper()
    arm = record_upper(7, 5, 4, 6)
    prefix = record_upper(4, 4, 0, 4)
    checkpoint = prefix["total"] + field["bytes"] + 8192
    common = dict(uninterrupted_arm=arm["total"], resumed_arm=arm["total"],
        checkpoint=checkpoint, sources=174080, verification=262144,
        qualification_log=16384, administrative_binding_and_closure=16384)
    alternatives = {}
    for phase, extra in (("published", 0), ("publish_link_before_unlink", checkpoint),
                         ("failure_with_pending_file", checkpoint)):
        parts = dict(common, temporary_checkpoint=extra, failure_diagnostics=16384 if "failure" in phase else 0)
        total = sum(parts.values())
        alternatives[phase] = dict(parts=parts, total=total, limit=4194304,
            excess=max(0, total-4194304))
    paths = ["tools/_memory_checkpoint.py", "reports/prepare_checkpoint_budget.py",
             "docs/MEMORY_SPEICHERN_WIEDERLADEN_PLAN.md"]
    files = {p:dict(bytes=(ROOT/p).stat().st_size,
        sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths}
    return dict(status="PRECONDITION_NOT_ESTABLISHED", field=field, arm=arm, prefix=prefix,
        alternatives=alternatives, files=files, test_calls=0, project_imports=0,
        caveats=["Protective maxima, not actual file sizes or a lower bound on required space.",
                 "Sources use the unchanged class cap; complete active inventory and test files are not yet bound.",
                 "Shared-subclass and metadata budgets are not proved by this total calculation.",
                 "Files with two names are counted twice, conservatively, even when hard-linked."])


if __name__ == "__main__":
    print(json.dumps(prepare(), ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False))
