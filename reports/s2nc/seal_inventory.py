"""Receptor-free source inventory sealing; no matcher or project imports."""

import ast
import hashlib
import json
import math
from pathlib import Path
import struct
import sys


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "s2nc-source-panel-preseal-20260906-01"
CONTRACT = "docs/S2NC_PROSPEKTIVER_AUDITIVER_A_ANWENDBARKEITSVERGLEICH.md"
INVENTORY_DOC = "docs/S2NC_QUELLENINVENTAR_UND_KONKURRENZPANELS.md"
PROFILE = {"sample_rate": 48000, "window_size": 4800, "hop_size": 480,
           "min_frequency": 50.0, "max_frequency": 18000.0, "band_count": 48}
SOURCE_PATHS = (
    "mcm_field_organism/log_spectral_receptor.py",
    "mcm_field_organism/carrier_baselines.py",
    "tools/_s2jw_default_live_profile.py",
    "tools/_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tools/_s2kz_private_direct_auditory_slot_scan_baseline.py",
)


def canonical(value):
    return json.dumps(value, allow_nan=False, ensure_ascii=True,
                      sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def group(seed_number, frequencies_millihz, amplitudes):
    return {"seed": f"s2nc-pcm-{seed_number:03d}",
            "partials": [{"frequency_millihz": f, "amplitude_ratio": list(a)}
                         for f, a in zip(frequencies_millihz, amplitudes, strict=True)]}


def source(source_id, groups):
    return {"source_id": source_id, "algorithm": "SEEDED_PHASE_HARMONIC_SUM_F32LE_V1",
            "sample_rate": 48000, "sample_count": 4800, "groups": groups}


def inventory():
    full = ((8, 20), (2, 20), (1, 20))
    lower = ((6, 20), (3, 40), (3, 80))
    quiet = ((1, 80), (1, 320), (1, 640))
    half = ((4, 20), (1, 20), (1, 40))
    return [
        source("s001", [group(1, (220000, 440000, 660000), full)]),
        source("s002", [group(2, (330000, 660000, 990000), full)]),
        source("s003", [group(3, (550000, 1100000, 1650000), full)]),
        source("s004", [group(4, (165000, 330000, 495000), full)]),
        source("s005", [group(5, (275000, 550000, 825000), full)]),
        source("s006", [group(6, (385000, 770000, 1155000), full)]),
        source("s007", [group(7, (770000, 1540000, 2310000), full)]),
        source("s008", [group(8, (1540000, 3080000, 4620000), full)]),
        source("s009", [group(9, (3080000, 6160000, 9240000), full)]),
        source("s010", [group(1, (220000, 440000, 660000), full)]),
        source("s011", [group(1, (220000, 440000, 660000), lower)]),
        source("s012", [group(1, (226600, 453200, 679800), full)]),
        source("s013", [group(2, (330000, 660000, 990000), full)]),
        source("s014", [group(2, (330000, 660000, 990000), lower)]),
        source("s015", [group(2, (339900, 679800, 1019700), full)]),
        source("s016", [group(3, (550000, 1100000, 1650000), full)]),
        source("s017", [group(3, (550000, 1100000, 1650000), lower)]),
        source("s018", [group(3, (566500, 1133000, 1699500), full)]),
        source("s019", [group(10, (467500, 935000, 1402500), full)]),
        source("s020", [group(11, (1023000, 2046000, 3069000), full)]),
        source("s021", []),
        source("s022", [group(1, (220000, 440000, 660000), quiet)]),
        source("s023", [group(1, (220000, 440000, 660000), half),
                        group(2, (330000, 660000, 990000), half)]),
    ]


def pcm_bytes(recipe):
    # Only oscillator parameters reach this function; no panels, rules, or evaluation data.
    oscillators = []
    for g in recipe["groups"]:
        for index, partial in enumerate(g["partials"]):
            seed = (g["seed"] + ":" + str(index)).encode("ascii")
            phase_word = int.from_bytes(hashlib.sha256(seed).digest()[:4], "little")
            phase = (float(phase_word) / 4294967296.0) * math.tau
            frequency = float(partial["frequency_millihz"]) / 1000.0
            numerator, denominator = partial["amplitude_ratio"]
            amplitude = float(numerator) / float(denominator)
            oscillators.append((frequency, amplitude, phase))
    encoded = bytearray(recipe["sample_count"] * 4)
    for sample_index in range(recipe["sample_count"]):
        time = float(sample_index) / float(recipe["sample_rate"])
        value = 0.0
        for frequency, amplitude, phase in oscillators:
            angle = ((math.tau * frequency) * time) + phase
            value = value + amplitude * math.sin(angle)
        if not math.isfinite(value) or not -1.0 <= value <= 1.0:
            raise ValueError("source sample outside canonical PCM domain")
        struct.pack_into("<f", encoded, sample_index * 4, value)
    return encoded


def panels_and_cases():
    # Literal panel families; removal never substitutes a different competitor.
    definitions = (
        ("p01", ("s001", "s002", "s003", "s004", "s005", "s006", "s007", "s008", "s009"),
         ("s001", "s008", "s009"), ("s010", "s011", "s012", "s019", "s020", "s021", "s022", "s023")),
        ("p02", (None, "s002", "s003", "s004", "s005", "s006", "s007", "s008", "s009"),
         (None, "s008", "s009"), ("s010", "s011", "s012", "s019", "s020", "s021", "s022", "s023")),
        ("p03", ("s001", "s002", "s003", "s004", "s005", "s006", "s007", "s008", "s009"),
         ("s002", "s008", "s009"), ("s013", "s014", "s015", "s019", "s020", "s021", "s022", "s023")),
        ("p04", ("s001", None, "s003", "s004", "s005", "s006", "s007", "s008", "s009"),
         (None, "s008", "s009"), ("s013", "s014", "s015", "s019", "s020", "s021", "s022", "s023")),
        ("p05", ("s001", "s002", "s003", "s004", "s005", "s006", "s007", "s008", "s009"),
         ("s003", "s008", "s009"), ("s016", "s017", "s018", "s019", "s020", "s021", "s022", "s023")),
        ("p06", ("s001", "s002", None, "s004", "s005", "s006", "s007", "s008", "s009"),
         (None, "s008", "s009"), ("s016", "s017", "s018", "s019", "s020", "s021", "s022", "s023")),
    )
    panels, cases = [], []
    for panel_id, b4, fast, cues in definitions:
        panels.append({"panel_id": panel_id,
                       "b4": [{"position": i, "source_id": sid} for i, sid in enumerate(b4)],
                       "fast": [{"position": i, "source_id": sid} for i, sid in enumerate(fast)]})
        for cue in cues:
            cases.append({"case_id": f"c{len(cases) + 1:03d}", "panel_id": panel_id, "cue_source_id": cue})
    return panels, cases


def main():
    OUT.mkdir(exist_ok=False)
    watched = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
               for p in (*SOURCE_PATHS, CONTRACT, INVENTORY_DOC)}
    tree = ast.parse((ROOT / SOURCE_PATHS[0]).read_text(encoding="utf-8-sig"))
    config = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "LogSpectralConfig")
    defaults = {n.target.id: ast.literal_eval(n.value) for n in config.body if isinstance(n, ast.AnnAssign)}
    if defaults != PROFILE:
        raise ValueError("existing receptor profile differs")
    sources = []
    for ordinal, recipe in enumerate(inventory(), 1):
        payload = pcm_bytes(recipe)
        if len(payload) != 19200:
            raise ValueError("PCM byte length differs")
        sources.append({**recipe, "ordinal": ordinal, "clock_id": "s2nc-source-sample-clock",
                        "window_start_sample": (ordinal - 1) * 4800, "window_end_sample": ordinal * 4800,
                        "recipe_digest": digest(recipe), "pcm_sha256": hashlib.sha256(payload).hexdigest(),
                        "pcm_byte_count": len(payload)})
        del payload
    panels, cases = panels_and_cases()
    execution = {
        "schema": "s2nc.source-panel-execution-plan.v1", "sources": sources,
        "candidate_sources": [f"s{i:03d}" for i in range(1, 10)],
        "cue_sources": [f"s{i:03d}" for i in range(10, 24)],
        "panels": panels, "cases": cases, "receptor_profile": PROFILE,
        "receptor_method": "LogSpectralReceptor.analyze, one complete window per source in ordinal order",
        "time_semantics": "declared PCM source clock; no rolling-clock state or inferred receptor timestamps",
        "observed_bands": list(range(24)), "unobserved_bands": list(range(24, 48)),
        "rules": [{"id": "MEAN_L1_24", "reduction": "mean", "threshold": 0.2},
                  {"id": "ALL_BANDS_24", "reduction": "max", "threshold": 0.2}],
        "a_resolution": "existing S2-KZ _resolve_a semantics; no B or context admission",
        "no_deduplication": True, "full_values_use": "internal 48-value candidate equality only",
        "budgets": {"source_windows": 23, "pcm_samples": 110400, "pcm_bytes_total": 441600,
                    "live_pcm_payload_bytes": 19200, "receptor_calls": 23, "receptor_values": 1104,
                    "panel_count": 6, "case_count_per_arm": 48, "occupied_relations_per_arm": 528,
                    "position_visits_per_arm": 576, "absolute_differences_per_arm": 12672,
                    "absolute_differences_both_arms": 25344, "decision_rows_both_arms": 1056,
                    "a_decisions_both_arms": 96, "full_value_equality_terms_max_per_arm": 2304,
                    "direct_table_baseline_decisions_both_arms": 96,
                    "baseline_full_value_equality_terms_max_per_arm": 2304,
                    "full_value_equality_terms_all_max": 9216,
                    "output_bytes_max": 4194304, "memory_calls": 0, "field_calls": 0,
                    "context_calls": 0, "rule_execution_authorized": False}}
    execution["execution_digest"] = digest(execution)
    role_map = {
        "s010": ("KNOWN_EXACT", "s001"), "s011": ("KNOWN_GAIN_VARIANT", "s001"),
        "s012": ("KNOWN_FREQUENCY_VARIANT", "s001"), "s013": ("KNOWN_EXACT", "s002"),
        "s014": ("KNOWN_GAIN_VARIANT", "s002"), "s015": ("KNOWN_FREQUENCY_VARIANT", "s002"),
        "s016": ("KNOWN_EXACT", "s003"), "s017": ("KNOWN_GAIN_VARIANT", "s003"),
        "s018": ("KNOWN_FREQUENCY_VARIANT", "s003"), "s019": ("UNKNOWN", None),
        "s020": ("UNKNOWN", None), "s021": ("LOW_INFORMATION_SILENCE", None),
        "s022": ("LOW_INFORMATION_QUIET", None), "s023": ("MIXED_SOURCE", None)}
    evaluations = []
    for case in cases:
        category, expected = role_map[case["cue_source_id"]]
        panel = next(p for p in panels if p["panel_id"] == case["panel_id"])
        present = expected is not None and any(x["source_id"] == expected for x in panel["b4"] + panel["fast"])
        evaluations.append({"case_id": case["case_id"], "category": category,
                            "related_reference": expected, "reference_present": present,
                            "expected": "UNIQUE_CORRECT_REFERENCE" if present else "ABSTAIN",
                            "accepted_source_ids": [expected] if present else []})
    evaluation = {"schema": "s2nc.source-panel-evaluation-plan.v1", "execution_digest": execution["execution_digest"],
                  "cases": evaluations, "category_relations_are_external": True,
                  "unknown_or_low_information_is_not_semantic_identity": True,
                  "present_known_denominators": {"exact": 3, "gain_variant": 3, "frequency_variant": 3},
                  "absent_known_denominator": 9, "unknown_denominator": 12,
                  "low_information_denominator": 12, "mixed_source_denominator": 6,
                  "success_contract_sha256": watched[CONTRACT]}
    evaluation["evaluation_digest"] = digest(evaluation)
    exact_pairs = ((0, 9), (1, 12), (2, 15))
    if not all(sources[a]["pcm_sha256"] == sources[b]["pcm_sha256"] for a, b in exact_pairs):
        raise ValueError("intended exact repetitions differ")
    if len({s["pcm_sha256"] for s in sources}) != 20:
        raise ValueError("unplanned payload collision")
    for p, expected in watched.items():
        if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != expected:
            raise ValueError("source or contract changed during sealing")
    seal = {"schema": "s2nc.source-panel-seal.v1", "status": "SOURCE_INVENTORY_AND_PANELS_PRESEALED",
            "execution_digest": execution["execution_digest"], "evaluation_digest": evaluation["evaluation_digest"],
            "source_hashes": watched, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "python_version": sys.version, "pcm_window_count": 23, "unique_payload_count": 20,
            "prescribed_exact_repetition_pairs": [["s001", "s010"], ["s002", "s013"], ["s003", "s016"]],
            "panel_count": 6, "case_count_per_arm": 48,
            "receptor_calls": 0, "distance_calculations": 0, "rule_calls": 0,
            "memory_calls": 0, "field_calls": 0, "context_calls": 0,
            "historical_vectors_read": 0, "pcm_payloads_persisted": 0}
    seal["seal_digest"] = digest(seal)
    for name, record in (("execution-plan.json", execution), ("evaluation-plan.json", evaluation), ("seal.json", seal)):
        with (OUT / name).open("xb") as handle:
            handle.write(canonical(record) + b"\n")
    print(json.dumps(seal, ensure_ascii=True))


if __name__ == "__main__":
    main()
