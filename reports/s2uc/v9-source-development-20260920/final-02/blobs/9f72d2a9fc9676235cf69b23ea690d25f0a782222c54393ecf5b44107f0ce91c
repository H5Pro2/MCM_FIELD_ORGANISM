"""One-shot S2-ND PCM preseal; standard library only, no receptor imports."""

import ast
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys


ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "s2nd-source-panel-preseal-20260906-02"
OUT = Path(__file__).resolve().parent / RUN_ID
CONTRACT = "docs/S2ND_PROSPEKTIVER_ERHALTUNGS_UND_VERLUSTVERGLEICH_AUDIO_PLAN.md"
PROFILE = dict(sample_rate=48000, window_size=4800, hop_size=480,
               min_frequency=50.0, max_frequency=18000.0, band_count=48)
WATCHED = (
    CONTRACT, "reports/s2nd/seal_inventory.py",
    "mcm_field_organism/log_spectral_receptor.py",
    "tools/_s2nc_private_rule_comparison.py",
    "tools/_s2nc_private_decision_baseline.py",
    "tools/_s2nc_private_rule_evaluation.py",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def filehash(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def require(condition, code):
    if not condition:
        raise ValueError(code)


def math_identity(module, builtin_names):
    require(getattr(module, "__name__", None) == "math", "MATH_MODULE_NAME_INVALID")
    spec = getattr(module, "__spec__", None)
    origin = getattr(spec, "origin", None)
    require(type(origin) is str and bool(origin), "MATH_MODULE_ORIGIN_INVALID")
    builtin = "math" in builtin_names
    if origin == "built-in":
        require(builtin, "MATH_BUILTIN_BINDING_INVALID")
        return {"kind": "BUILT_IN", "module_name": "math",
                "spec_origin": origin, "builtin_membership": True}
    require(not builtin and origin != "frozen" and getattr(spec, "has_location", False) is True,
            "MATH_FILE_ORIGIN_INVALID")
    filename = getattr(module, "__file__", None)
    require(type(filename) is str and bool(filename), "MATH_MODULE_FILE_INVALID")
    require(Path(origin).is_absolute() and Path(filename).is_absolute(), "MATH_MODULE_FILE_INVALID")
    try:
        path = Path(filename).resolve(strict=True)
        origin_path = Path(origin).resolve(strict=True)
    except (OSError, ValueError):
        raise ValueError("MATH_MODULE_FILE_INVALID") from None
    require(path == origin_path and path.is_file(), "MATH_MODULE_FILE_INVALID")
    return {"kind": "FILE_BASED", "module_name": "math", "spec_origin": origin,
            "builtin_membership": False, "path": str(path), "sha256": filehash(path)}


def publish(name, value):
    data = canonical(value)
    with (OUT / name).open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    return hashlib.sha256(data).hexdigest()


def inventory():
    a0 = ((8, 20), (2, 20), (1, 20))
    a1 = ((6, 20), (3, 40), (3, 80))
    a2 = ((6, 20), (4, 20), (1, 20))
    specifications = (
        ("s001", (240000, 480000, 720000), a0, "s2nd-pcm-001"),
        ("s002", (360000, 720000, 1080000), a0, "s2nd-pcm-002"),
        ("s003", (600000, 1200000, 1800000), a0, "s2nd-pcm-003"),
        ("s004", (1440000, 2880000, 4320000), a0, "s2nd-pcm-004"),
        ("s005", (2160000, 4320000, 6480000), a0, "s2nd-pcm-005"),
        ("s006", (3600000, 7200000, 10800000), a0, "s2nd-pcm-006"),
        ("s007", (240000, 480000, 720000), a0, "s2nd-pcm-001"),
        ("s008", (240000, 480000, 720000), a1, "s2nd-pcm-001"),
        ("s009", (247200, 494400, 741600), a0, "s2nd-pcm-001"),
        ("s010", (240000, 480000, 720000), a2, "s2nd-pcm-001"),
        ("s011", (360000, 720000, 1080000), a0, "s2nd-pcm-002"),
        ("s012", (360000, 720000, 1080000), a1, "s2nd-pcm-002"),
        ("s013", (370800, 741600, 1112400), a0, "s2nd-pcm-002"),
        ("s014", (360000, 720000, 1080000), a2, "s2nd-pcm-002"),
        ("s015", (600000, 1200000, 1800000), a0, "s2nd-pcm-003"),
        ("s016", (600000, 1200000, 1800000), a1, "s2nd-pcm-003"),
        ("s017", (618000, 1236000, 1854000), a0, "s2nd-pcm-003"),
        ("s018", (600000, 1200000, 1800000), a2, "s2nd-pcm-003"),
    )
    return tuple({"source_id": sid, "format": "PCM_F32LE", "channels": 1,
                  "sample_rate": 48000, "sample_count": 4800,
                  "algorithm": "SEEDED_PHASE_HARMONIC_SUM_F32LE_V1", "seed": seed,
                  "partials": [{"frequency_millihz": f, "amplitude_ratio": list(a)}
                               for f, a in zip(frequencies, amplitudes, strict=True)]}
                 for sid, frequencies, amplitudes, seed in specifications)


def pcm_payload(recipe):
    oscillators = []
    for index, partial in enumerate(recipe["partials"]):
        word = int.from_bytes(hashlib.sha256((recipe["seed"] + ":" + str(index)).encode("ascii")).digest()[:4], "little")
        phase = (float(word) / 4294967296.0) * math.tau
        frequency = float(partial["frequency_millihz"]) / 1000.0
        numerator, denominator = partial["amplitude_ratio"]
        amplitude = float(numerator) / float(denominator)
        oscillators.append((frequency, amplitude, phase))
    payload = bytearray(19200)
    for sample_index in range(4800):
        time = float(sample_index) / 48000.0
        value = 0.0
        for frequency, amplitude, phase in oscillators:
            angle = ((math.tau * frequency) * time) + phase
            value = value + amplitude * math.sin(angle)
        require(math.isfinite(value) and -1.0 <= value <= 1.0, "PCM_SAMPLE_INVALID")
        struct.pack_into("<f", payload, sample_index * 4, value)
        stored = struct.unpack_from("<f", payload, sample_index * 4)[0]
        require(math.isfinite(stored) and -1.0 <= stored <= 1.0, "PCM_F32_INVALID")
    return payload


def panel_inventory():
    definitions = (
        ("p01", "s001", None, "s001", ("s007", "s008", "s009", "s010")),
        ("p02", None, None, None, ("s007", "s008", "s009", "s010")),
        ("p03", "s001", "s004", "s001", ("s007", "s008", "s009", "s010")),
        ("p04", None, "s004", None, ("s007", "s008", "s009", "s010")),
        ("p05", "s002", None, "s002", ("s011", "s012", "s013", "s014")),
        ("p06", None, None, None, ("s011", "s012", "s013", "s014")),
        ("p07", "s002", "s005", "s002", ("s011", "s012", "s013", "s014")),
        ("p08", None, "s005", None, ("s011", "s012", "s013", "s014")),
        ("p09", "s003", None, "s003", ("s015", "s016", "s017", "s018")),
        ("p10", None, None, None, ("s015", "s016", "s017", "s018")),
        ("p11", "s003", "s006", "s003", ("s015", "s016", "s017", "s018")),
        ("p12", None, "s006", None, ("s015", "s016", "s017", "s018")),
    )
    panels, cases = [], []
    for pid, b0, b1, f0, cues in definitions:
        panels.append({"panel_id": pid,
                       "b4": [{"position": i, "source_id": s} for i, s in enumerate((b0, b1) + (None,) * 7)],
                       "fast": [{"position": i, "source_id": s} for i, s in enumerate((f0, None, None))]})
        for cue in cues:
            cases.append({"case_id": f"c{len(cases) + 1:03d}", "panel_id": pid, "cue_source_id": cue})
    return panels, cases


def evaluation_plan(execution, contract_hash):
    relations = (
        ("s007", "s001", "KNOWN_EXACT", "EXACT"),
        ("s008", "s001", "KNOWN_GAIN_VARIANT", "UNIFORM_GAIN"),
        ("s009", "s001", "KNOWN_FREQUENCY_VARIANT", "FREQUENCY"),
        ("s010", "s001", "KNOWN_GAIN_VARIANT", "SPECTRAL_REWEIGHT"),
        ("s011", "s002", "KNOWN_EXACT", "EXACT"),
        ("s012", "s002", "KNOWN_GAIN_VARIANT", "UNIFORM_GAIN"),
        ("s013", "s002", "KNOWN_FREQUENCY_VARIANT", "FREQUENCY"),
        ("s014", "s002", "KNOWN_GAIN_VARIANT", "SPECTRAL_REWEIGHT"),
        ("s015", "s003", "KNOWN_EXACT", "EXACT"),
        ("s016", "s003", "KNOWN_GAIN_VARIANT", "UNIFORM_GAIN"),
        ("s017", "s003", "KNOWN_FREQUENCY_VARIANT", "FREQUENCY"),
        ("s018", "s003", "KNOWN_GAIN_VARIANT", "SPECTRAL_REWEIGHT"),
    )
    mapping = {sid: (reference, category, subtype) for sid, reference, category, subtype in relations}
    panels = {p["panel_id"]: p for p in execution["panels"]}
    rows = []
    for case in execution["cases"]:
        reference, category, subtype = mapping[case["cue_source_id"]]
        panel = panels[case["panel_id"]]
        occupied = tuple(s["source_id"] for s in panel["b4"] + panel["fast"] if s["source_id"] is not None)
        present = reference in occupied
        rows.append({**case, "related_reference": reference, "category": category, "variant_subtype": subtype,
                     "reference_present": present, "accepted_source_ids": [reference] if present else [],
                     "expected": "UNIQUE_CORRECT_REFERENCE" if present else "ABSTAIN",
                     "competition": "COMPETITOR_PRESENT" if any(s != reference for s in occupied) else "NO_COMPETITOR"})
    return {"schema": "s2nd.retention-evaluation-plan.v1", "execution_digest": execution["execution_digest"],
            "contract_sha256": contract_hash, "cases": rows,
            "denominators": {"positive_cases": 24, "exact_positive": 6, "variant_positive": 18,
                             "positive_per_variant_subtype": 6, "removal_controls": 24,
                             "distinct_exact_cues": 3, "distinct_variant_cues": 9},
            "retention": {"N": "all present-reference cases in subgroup",
                          "D": "correct uniquely admitted MEAN_L1_24 cases in subgroup",
                          "R": "D cases still correctly uniquely admitted by ALL_BANDS_24",
                          "L": "D cases not retained correctly; separate abstention and wrong admission",
                          "identity": "D = R + L", "empty_denominator": "ERHALTUNG_NICHT_GEPRUEFT",
                          "nonempty_no_loss": "RETENTION_CONFIRMED_ON_OBSERVED_SUBSET",
                          "any_loss": "RETENTION_FALSIFIED",
                          "strata": ["EXACT", "UNIFORM_GAIN", "FREQUENCY", "SPECTRAL_REWEIGHT", "ALL_VARIANTS"],
                          "additional_strata": ["competition", "non_bitidentical_receptor_values"],
                          "aggregate_gain_does_not_cancel_loss": True,
                          "exact_controls_do_not_replace_variant_denominator": True},
            "no_postanalysis_selection": True, "relations_are_external_not_semantic": True}


def main():
    OUT.mkdir(exist_ok=False)
    phase, source_id, sources = "BINDING", None, []
    before = {p: filehash(ROOT / p) for p in WATCHED}
    try:
        tree = ast.parse((ROOT / "mcm_field_organism/log_spectral_receptor.py").read_text(encoding="utf-8-sig"))
        config = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "LogSpectralConfig")
        defaults = {n.target.id: ast.literal_eval(n.value) for n in config.body if isinstance(n, ast.AnnAssign)}
        require(defaults == PROFILE, "PROFILE_SOURCE_DIFFERS")
        identity = {"python_version": sys.version, "python_executable": sys.executable,
                    "python_executable_sha256": filehash(Path(sys.executable)),
                    "math_module": math_identity(math, sys.builtin_module_names),
                    "generator_path": "reports/s2nd/seal_inventory.py",
                    "generator_sha256": before["reports/s2nd/seal_inventory.py"]}
        phase = "PCM_GENERATION"
        for ordinal, recipe in enumerate(inventory(), 1):
            source_id = recipe["source_id"]
            payload = pcm_payload(recipe)
            require(len(payload) == 19200, "PCM_SIZE_INVALID")
            sources.append({**recipe, "ordinal": ordinal, "recipe_digest": digest(recipe),
                            "pcm_sha256": hashlib.sha256(payload).hexdigest(), "pcm_byte_count": len(payload),
                            "clock_id": "s2nd-source-sample-clock", "window_start_sample": (ordinal - 1) * 4800,
                            "window_end_sample": ordinal * 4800})
            del payload
        phase, source_id = "PLAN_BINDING", None
        require(len(sources) == 18, "SOURCE_COUNT_INVALID")
        panels, cases = panel_inventory()
        require(len(panels) == 12 and len(cases) == 48, "PLAN_COUNT_INVALID")
        occupied = {p["panel_id"]: sum(s["source_id"] is not None for s in p["b4"] + p["fast"]) for p in panels}
        require(sum(occupied[c["panel_id"]] for c in cases) == 72, "RELATION_BUDGET_INVALID")
        execution = {"schema": "s2nd.source-panel-execution-plan.v1", "sources": sources,
                     "generator_identity": identity, "contract_sha256": before[CONTRACT],
                     "candidate_sources": [f"s{i:03d}" for i in range(1, 7)],
                     "cue_sources": [f"s{i:03d}" for i in range(7, 19)], "panels": panels, "cases": cases,
                     "receptor_profile": PROFILE, "receptor_profile_digest": digest(PROFILE),
                     "receptor_method": "LogSpectralReceptor.analyze, one call per complete source window",
                     "time_semantics": "declared source sample clock; no rolling receptor time",
                     "observed_bands": list(range(24)), "unobserved_bands": list(range(24, 48)),
                     "rules": [{"id": "MEAN_L1_24", "reduction": "statistics.mean", "threshold": 0.2},
                               {"id": "ALL_BANDS_24", "reduction": "max", "threshold": 0.2}],
                     "a_resolution": "unchanged S2-NC A-resolution and direct table; full scans, no deduplication",
                     "hidden_values_use": "internal full-candidate equality only",
                     "budgets": {"source_windows": 18, "samples": 86400, "pcm_bytes": 345600,
                                 "live_payloads_max": 1, "live_pcm_bytes_max": 19200,
                                 "future_receptor_calls": 18, "future_receptor_values": 864,
                                 "cases_per_rule": 48, "position_visits_per_rule": 576,
                                 "relations_per_rule": 72, "band_differences_per_rule": 1728,
                                 "a_decisions_total": 96, "baseline_decisions_total": 96,
                                 "equality_terms_with_verification_max": 6912,
                                 "relation_ceiling_per_rule": 528, "band_difference_ceiling_per_rule": 12672,
                                 "equality_terms_ceiling": 9216, "output_bytes_max": 4194304},
                     "receptor_execution_authorized": False, "rule_execution_authorized": False}
        execution["execution_digest"] = digest(execution)
        evaluation = evaluation_plan(execution, before[CONTRACT])
        evaluation["evaluation_digest"] = digest(evaluation)
        source_map = {s["source_id"]: s for s in sources}
        exact_pairs = (("s001", "s007"), ("s002", "s011"), ("s003", "s015"))
        require(all(source_map[a]["pcm_sha256"] == source_map[b]["pcm_sha256"] for a, b in exact_pairs),
                "EXACT_CONTROL_DIFFERS")
        after = {p: filehash(ROOT / p) for p in WATCHED}
        require(before == after, "SOURCE_CHANGED")
        phase = "PUBLICATION"
        execution_sha = publish("execution-plan.json", execution)
        evaluation_sha = publish("evaluation-plan.json", evaluation)
        seal = {"schema": "s2nd.source-panel-seal.v1", "run_id": RUN_ID, "status": "SOURCE_INVENTORY_AND_PANELS_PRESEALED",
                "execution_digest": execution["execution_digest"], "evaluation_digest": evaluation["evaluation_digest"],
                "execution_file_sha256": execution_sha, "evaluation_file_sha256": evaluation_sha,
                "source_hashes_before": before, "source_hashes_after": after, "sources_unchanged": True,
                "generator_identity": identity, "completed_pcm_sources": len(sources),
                "pcm_samples": 86400, "generated_pcm_bytes": 345600, "max_live_pcm_payload_bytes": 19200,
                "max_live_payload_count": 1, "raw_payloads_persisted": 0,
                "exact_pairs_preserved": exact_pairs, "unique_payload_count": len({s["pcm_sha256"] for s in sources}),
                "panel_count": 12, "case_count_per_rule": 48,
                "receptor_calls": 0, "distance_calculations": 0, "tests": 0, "rule_calls": 0,
                "memory_calls": 0, "context_calls": 0, "field_calls": 0, "runtime_calls": 0}
        seal["seal_digest"] = digest(seal)
        seal_sha = publish("seal.json", seal)
        print(json.dumps({"run_id": RUN_ID, "status": seal["status"], "execution_digest": execution["execution_digest"],
                          "evaluation_digest": evaluation["evaluation_digest"], "seal_digest": seal["seal_digest"],
                          "seal_file_sha256": seal_sha, "completed_pcm_sources": len(sources)}, sort_keys=True))
        return 0
    except Exception as error:
        publish("failure.json", {"run_id": RUN_ID, "status": "NOT_EVALUABLE", "phase": phase,
                                 "source_id": source_id, "completed_pcm_sources": len(sources),
                                 "error_class": type(error).__name__, "error_code": str(error),
                                 "source_hashes_before": before})
        print(json.dumps({"run_id": RUN_ID, "status": "NOT_EVALUABLE", "phase": phase,
                          "source_id": source_id, "completed_pcm_sources": len(sources)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
