"""Only the three previously bound NL pairs; no formations or raw sources."""

import json
import os
from dataclasses import asdict
from pathlib import Path
import unittest

from mcm_field_organism import _tspm1_private as core
from mcm_field_organism import _tspm1_s2dr_private_comparison as fifo
from mcm_field_organism.broadband_hearing_path import AuditoryReceptorState, AuditoryReceptorContact
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig
from tools import _s2jw_default_live_profile as profile
from tools import _s2jw_profiled_memory_coordinator as memory
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools import _s2nj_private_auditory_output_projection as half
from tools import _s2nl_private_half_profile_binding as adapter
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as kz
from tools import _s2ne_private_auditory_transfer as ne
from tools import _s2ne_private_direct_and_verification as direct

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "reports/s2nl/s2nl-versioned-rank-scale-qualification-20260907-01/observations.json"
PAIRS = (
    ("0x0.0000000000001p-1022", "0x0.0p+0"),
    ("0x0.0000000000003p-1022", "0x0.0000000000004p-1022"),
    ("0x1.0000000000000p-1022", "0x0.fffffffffffffp-1022"),
)
ROWS = []


def project(values):
    config = LogSpectralConfig()
    state = AuditoryReceptorState("auditory", half.RAW_GEOMETRY, 0, 0, 4800,
        tuple(b.channel_id for b in half.spectral.logarithmic_bands(config)), values,
        AuditoryReceptorContact.ACTIVE_ENERGY if any(values) else AuditoryReceptorContact.ACTIVE_ZERO)
    return half.project_auditory_half_v1(state, config=config,
                                       source_profile_digest=half.RAW_PROFILE_DIGEST)


def seed(config, b4_values, fast_values):
    """Valid synthetic B4/Fast fixture, explicitly not a formation history."""
    null = core.initial_tspm1_composite_state(config.tspm_config)
    slots = (core.TSPM1FastSlot("tspm1.fast.slot.000", True, fast_values,
        (0.0,)*288, 1, 1, 0, None),) + tuple(
        core.TSPM1FastSlot.free(f"tspm1.fast.slot.{i:03d}") for i in range(1, 3))
    fast = core._make_fast_state(config.tspm_config.fast_config, 1, "audio.sample", 4800,
                                 "video.frame", 3, slots)
    ts = core._make_composite_state(config.tspm_config, 1, "1"*64, "2"*64,
        fast, null.auditory_ppb1_state, null.visual_ppb1_state)
    b4 = fifo._B4State(1, (fifo._FIFOEntry("b4.slot.000", True, b4_values+(0.0,)*288, 1),)
        + tuple(fifo._FIFOEntry(f"b4.slot.{i:03d}", False, (), None) for i in range(1, 9)))
    return memory._validate_state(config, memory._make_state(config, 1, "3"*64, "4"*64, b4, ts))


def tearDownModule():
    data = half.canonical(dict(rows=ROWS, primary_decisions=len(ROWS),
        evidence_records=sum(len(r["arms"]) for r in ROWS),
        semantic_changes=[dict(pair=i, rule=rule,
            old=next(r["decision"] for r in ROWS if r["pair"] == i and r["rule"] == rule and r["profile"] == "OLD"),
            new=next(r["decision"] for r in ROWS if r["pair"] == i and r["rule"] == rule and r["profile"] == "HALF"))
            for i in range(3) for rule in ne.RULES
            if sum(r["pair"] == i and r["rule"] == rule for r in ROWS) == 2]))
    if len(data) > 1048576:
        raise ValueError("S2NM_OUTPUT_LIMIT")
    with (Path(os.environ["S2NM_QUAL_DIR"])/"observations.json").open("xb") as handle:
        handle.write(data)


class SubnormalConflictTests(unittest.TestCase):
    def check_pair(self, index):
        historical = json.loads(HISTORY.read_bytes())
        bound = next(r for r in historical["numerical"] if r["case"] == f"subnormal.{index}")
        self.assertEqual(tuple(bound["old_last"]), PAIRS[index])
        raw = tuple((0.0,)*47+(float.fromhex(h),) for h in PAIRS[index])
        projected = tuple(project(v) for v in raw)
        scaled = tuple(p.values for p in projected)
        self.assertEqual([v[47].hex() for v in scaled], bound["new_last"])
        p = profile.build_s2jw_default_live_profile()
        old = memory.build_s2jv_coordinator_config(tspm_config=p.tspm_config, b4_capacity=9,
                                                   ledger_limits=build_s2jv_ledger_limits(p))
        new = adapter.build_config()
        self.assertEqual(old.config_digest, historical["historical_config_digest"])
        self.assertEqual(new.config_digest, historical["new_config_digest"])
        plan = kz.build_auditory_band_plan_48()
        for label, config, vectors in (("OLD", old, raw), ("HALF", new, scaled)):
            state = seed(config, *vectors)
            before = half.canonical(asdict(state))
            cue = kz.build_masked_auditory_cue_48(
                pcm_payload_digest=half.digest("neutral-no-pcm-generated"),
                receptor_state_digest=half.digest(dict(neutral=True, profile=label, endpoint=9600)),
                receptor_values_digest=half.digest([0.0]*48), config_digest=config.config_digest,
                auditory_source_clock_id="audio.sample", auditory_window_start_tick=4800,
                auditory_window_end_tick=9600, observed_values=(0.0,)*24, band_plan=plan)
            cue_before = half.canonical(cue.payload_without_digest())
            for rule in ne.RULES:
                kwargs = dict(rule=rule, config=config, state=state, cue=cue, band_plan=plan)
                primary = ne.retrieve(**kwargs)
                baseline = direct.direct_retrieve(**kwargs)
                e = primary.evidence
                row = dict(pair=index, profile=label, rule=rule, differing_position=47,
                    candidate_hex=[[v.hex() for v in values] for values in vectors],
                    candidate_digests=[half.digest(list(values)) for values in vectors],
                    full_vector_equal=vectors[0] == vectors[1], a_status=e.a_recent.status,
                    decision=e.decision, hypothesis_present=e.hypothesis is not None,
                    state=asdict(state), cue=cue.payload_without_digest(),
                    projection_digests=[p.projection_digest for p in projected] if label == "HALF" else [],
                    arms=[a.canonical_payload() for a in (primary, baseline)],
                    verification=[], baseline_equal=direct.compare_technical(primary, baseline))
                ROWS.append(row)
                for arm in (primary, baseline):
                    row["verification"].append(direct.verify_arm(arm=arm, config=config,
                        state=state, cue=cue, band_plan=plan))
                    self.assertLess(len(half.canonical(arm.canonical_payload())), 32768)
                    self.assertEqual(tuple(len(s.records) for s in arm.evidence.bank_scans), (9, 3, 8))
                    self.assertEqual(tuple(s.match_count for s in arm.evidence.bank_scans), (1, 1, 0))
                    self.assertEqual(arm.evidence.prestate_digest, arm.evidence.poststate_digest)
                    self.assertEqual(state.state_digest, arm.evidence.poststate_digest)
                    self.assertLessEqual(arm.evidence.resource_ledger.total_value_comparison_count, 528)
                    self.assertEqual(arm.evidence.resource_ledger.total_value_comparison_count, 96)
                    self.assertEqual(arm.evidence.resource_ledger.memory_receptor_consumer_context_or_field_call_count, 0)
                self.assertTrue(row["baseline_equal"])
                self.assertEqual(before, half.canonical(asdict(state)))
                self.assertEqual(cue_before, half.canonical(cue.payload_without_digest()))
                self.assertEqual(vectors[0] == vectors[1], label == "HALF")
                self.assertEqual(e.a_recent.status, "A_RECENT_INTERNAL_CONFLICT" if label == "OLD" else "A_RECENT_APPLICABLE")
                self.assertEqual(e.decision, "ABSTAIN_INTERNAL_CONFLICT" if label == "OLD" else "ADMIT_SINGLE_CONTEXT")
                if label == "OLD":
                    self.assertIsNone(e.hypothesis)
                else:
                    self.assertEqual(e.hypothesis.area, "A_RECENT")
                    self.assertEqual(len(e.hypothesis.proposed_values), 24)
                    self.assertEqual(e.hypothesis.proposed_values[-1].hex(), vectors[0][-1].hex())

    def test_01_smallest_subnormal_zero(self):
        self.check_pair(0)

    def test_02_three_four_subnormal(self):
        self.check_pair(1)

    def test_03_normal_boundary(self):
        self.check_pair(2)
