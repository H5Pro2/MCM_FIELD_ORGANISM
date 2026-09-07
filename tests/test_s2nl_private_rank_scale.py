"""Prospectively fixed neutral checks; no NH sources or system execution."""

from copy import deepcopy
from dataclasses import asdict, replace
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import sys
import unittest

from mcm_field_organism import _tspm1_private as core
from mcm_field_organism import _ppb1_reference as ppb
from mcm_field_organism import _ppb1_receptor_profiles as profiles
from mcm_field_organism import _tspm1_s2dr_private_comparison as fifo
from mcm_field_organism.broadband_hearing_path import AuditoryReceptorState, AuditoryReceptorContact
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.receptor_contract import ReceptorContactFrame, CommonFieldTime
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools import _s2jw_default_live_profile as profile
from tools import _s2jw_default_live_av_pairing as pairing
from tools import _s2jw_profiled_memory_coordinator as memory
from tools import _s2jw_profiled_memory_read_only as read
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools import _s2nj_private_auditory_output_projection as half
from tools import _s2nl_private_half_profile_binding as adapter
from tools import _s2nl_private_rank_verification as direct
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as kz
from tools import _s2ne_private_auditory_transfer as ne
from tools import _s2ne_private_direct_and_verification as ne_direct

NUMERICAL = []
TRACES = []
COUNTS = dict(atomic_formations=0, direct_ppb_steps=0, neutral_receptor_calls=0,
              match_pairs=0, subnormal_pairs=0)


def raw(values, index=0):
    return AuditoryReceptorState("auditory", half.RAW_GEOMETRY, index*10, index*4800,
        (index+1)*4800, tuple(b.channel_id for b in half.spectral.logarithmic_bands(LogSpectralConfig())),
        tuple(values), AuditoryReceptorContact.ACTIVE_ENERGY if any(values) else AuditoryReceptorContact.ACTIVE_ZERO)


def project(values, index=0):
    return half.project_auditory_half_v1(raw(values, index), config=LogSpectralConfig(),
                                       source_profile_digest=half.RAW_PROFILE_DIGEST)


def old_config():
    p = profile.build_s2jw_default_live_profile()
    return memory.build_s2jv_coordinator_config(tspm_config=p.tspm_config, b4_capacity=9,
                                               ledger_limits=build_s2jv_ledger_limits(p))


def pair(config, audio, visual, index=0):
    audio = (float(audio),)*48 if isinstance(audio, (int, float)) else tuple(audio)
    visual = (float(visual),)*288 if isinstance(visual, (int, float)) else tuple(visual)
    time = CommonFieldTime("neutral.scale.field", index*100_000_000+90_000_000, (index+1)*100_000_000)
    v = OrganismTimedReceptorFrame(ReceptorContactFrame("visual", config.profile.profile.visual_config.geometry_id,
        f"neutral.visual.{index}", "video.frame", index*3+2, index*3+3,
        config.profile.profile.visual_config.carrier_ids, visual), time)
    pcm, rgb = half.digest(dict(audio=audio, index=index)), half.digest(dict(visual=visual, index=index))
    if config.schema == memory.HALF_COORDINATOR_SCHEMA:
        return adapter.bind_pair(projection=project(audio, index), visual=v, common_time=time,
                                 pcm_digest=pcm, rgb_digest=rgb, pair_id=f"neutral.pair.{index}")
    a = OrganismTimedReceptorFrame(ReceptorContactFrame("auditory", half.RAW_GEOMETRY,
        f"neutral.audio.{index}", "audio.sample", index*4800, (index+1)*4800,
        config.profile.profile.auditory_config.carrier_ids, audio), time)
    plan = pairing.build_s2jv_pairing_plan(pair_id=f"neutral.pair.{index}", source_contract_id="neutral.scale",
        profile=config.profile, auditory=a, visual=v, auditory_payload_digest=pcm, visual_payload_digest=rgb)
    return pairing.bind_s2jv_default_live_pair(pairing_plan=plan, profile=config.profile, auditory=a, visual=v)


def formation(config, state, source):
    bound = memory.bind_s2jv_coordinator_input(config=config, source=source)
    owner = memory.S2JVFormationOwner(f"neutral.owner.{state.generation}", "neutral.auth", "neutral.use",
        config.config_digest, state.state_digest, bound.input_digest)
    COUNTS["atomic_formations"] += 1
    result = memory.advance_s2jv_atomic(config=config, prestate=state, source=bound, owner=owner)
    return result, bound


def seed(config, specs):
    """Explicit synthetic slot fixture, not a claimed formation history."""
    n = len(specs)
    null = core.initial_tspm1_composite_state(config.tspm_config)
    factor = 0.5 if config.schema == memory.HALF_COORDINATOR_SCHEMA else 1.0
    slots = tuple(core.TSPM1FastSlot(f"tspm1.fast.slot.{i:03d}", True,
        (a*factor,)*48, (v,)*288, 1, i+1, 0, None) for i, (a, v) in enumerate(specs))
    slots += tuple(core.TSPM1FastSlot.free(f"tspm1.fast.slot.{i:03d}") for i in range(n, 3))
    fast = core._make_fast_state(config.tspm_config.fast_config, n, "audio.sample", n*4800,
                                 "video.frame", n*3, slots)
    ts = core._make_composite_state(config.tspm_config, n, "1"*64, "2"*64,
        fast, null.auditory_ppb1_state, null.visual_ppb1_state)
    b4 = fifo._B4State(n, tuple(fifo._FIFOEntry(f"b4.slot.{i:03d}", True,
        (a*factor,)*48+(v,)*288, i+1) for i, (a, v) in enumerate(specs)) +
        tuple(fifo._FIFOEntry(f"b4.slot.{i:03d}", False, (), None) for i in range(n, 9)))
    return memory._validate_state(config, memory._make_state(config, n, "3"*64, "4"*64, b4, ts))


def compare_numbers(label, old, new):
    NUMERICAL.append(dict(case=label, old_hex=old.hex(), new_hex=new.hex(),
        expected_half_hex=(old*0.5).hex(), exact_scale_equal=new.hex() == (old*0.5).hex()))


class RankScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = old_config()
        cls.new = adapter.build_config()

    def test_01_historical_payload_and_digest(self):
        f = self.old.tspm_config.fast_config
        expected = dict(schema_version="tspm1.private.v1", fast_bank_id="tspm1.fast", capacity=3,
            auditory_match_threshold=0.2, visual_match_threshold=0.2, update_factor=0.5,
            consolidate_after=2, expire_after_exposures=8)
        self.assertEqual(expected, f.canonical_payload())
        self.assertEqual(profile.EXPECTED_FAST_CONFIG_DIGEST, f.digest())
        self.assertEqual(profile.EXPECTED_TSPM_CONFIG_DIGEST, self.old.tspm_config.config_binding_digest)
        self.assertEqual(profile.EXPECTED_PROFILE_BINDING_DIGEST, self.old.profile.profile.digest())
        self.assertEqual(profile.EXPECTED_SOURCE_PROFILE_DIGEST, self.old.profile.source_profile_digest)

    def test_02_fixed_new_profile(self):
        c = self.new.tspm_config
        self.assertEqual((0.1, 0.01, 0.2, 0.01), (c.fast_config.auditory_match_threshold,
            c.profile.auditory_config.match_threshold, c.fast_config.visual_match_threshold,
            c.profile.visual_config.match_threshold))
        self.assertEqual(core.HALF_RANK, c.fast_config.rank_binding)
        self.assertEqual(self.old.tspm_config.profile.visual_config, c.profile.visual_config)
        self.assertEqual(core.TSPM1_HALF_SCHEMA, c.schema_version)
        self.assertEqual(adapter.build_config(), self.new)

    def test_03_mixed_profile_rejected(self):
        for fast, p in ((self.old.tspm_config.fast_config, self.new.profile.profile),
                        (self.new.tspm_config.fast_config, self.old.profile.profile)):
            with self.assertRaises(core.TSPM1Error):
                core.TSPM1ConfigBinding.build(fast, p)
        with self.assertRaises(profiles.PPB1ReceptorProfileError):
            replace(self.new.profile.profile, schema_version=profiles.PPB1_PROFILE_SCHEMA_VERSION)

    def test_04_rank_manipulation_rejected(self):
        for kwargs in (dict(rank_binding="arbitrary"), dict(rank_binding=core.HISTORICAL_RANK),
                       dict(auditory_match_threshold=0.2), dict(schema_version=core.TSPM1_SCHEMA_VERSION)):
            with self.assertRaises(core.TSPM1Error):
                replace(self.new.tspm_config.fast_config, **kwargs)
        broken = deepcopy(self.new.tspm_config)
        object.__setattr__(broken.fast_config, "rank_binding", "arbitrary")
        with self.assertRaises(core.TSPM1Error):
            core._validate_config(broken)

    def test_05_counterexample(self):
        points = ((3/16, 1/32), (1/32, 1/8))
        old = [core.joint_rank_prefix(self.old.tspm_config.fast_config, a, v) for a, v in points]
        naive = [core.joint_rank_prefix(self.old.tspm_config.fast_config, a/2, v) for a, v in points]
        new = [core.joint_rank_prefix(self.new.tspm_config.fast_config, a/2, v) for a, v in points]
        self.assertEqual((1, 0, 1), tuple(min(range(2), key=lambda i: keys[i]) for keys in (old, naive, new)))
        self.assertEqual(old, new)
        TRACES.append(dict(kind="dyadic_counterexample", old=old, naive=naive, new=new))

    def test_06_maximum_then_sum(self):
        for config, factor in ((self.old, 1.0), (self.new, 0.5)):
            a = direct.direct_key(config.tspm_config, (1/8)*factor, 1/32, "slot.a")
            b = direct.direct_key(config.tspm_config, (1/8)*factor, 1/16, "slot.b")
            self.assertEqual(a[0], b[0])
            self.assertLess(a, b)

    def test_07_slot_and_age_tie_break(self):
        for config, factor in ((self.old, 1.0), (self.new, 0.5)):
            key = lambda slot, age=None: direct.direct_key(config.tspm_config,
                (1/8)*factor, 1/8, slot, formation_index=age)
            self.assertLess(key("slot.a"), key("slot.b"))
            self.assertLess(key("slot.b", 2), key("slot.a", 1))
            self.assertLess(key("slot.a", 2), key("slot.b", 2))

    def test_08_thirty_match_pairs(self):
        routes = (("fast", 48, 0.2, "fsum"), ("ppb", 48, 0.02, "fsum"),
                  ("reference-a", 24, 0.2, "sum"), ("alternative-a", 24, 0.2, "max"),
                  ("slow", 24, 0.02, "sum"))
        for route, n, t, method in routes:
            pairs = [((0.0,)*n, (delta,)*n) for delta in (0.0, t, math.nextafter(t, 0.0), math.nextafter(t, math.inf))]
            pairs += [((0.0,)*n, (4*t,)*(n//4)+(0.0,)*(n-n//4)), ((0.25,)*n, (0.25+t,)*n)]
            for index, (x, y) in enumerate(pairs):
                distances = []
                for config, factor in ((self.old, 1.0), (self.new, 0.5)):
                    left, right = tuple(v*factor for v in x), tuple(v*factor for v in y)
                    terms = tuple(abs(a-b) for a, b in zip(left, right, strict=True))
                    d = ppb.normalized_mean_l1_distance(left, right) if method == "fsum" else max(terms) if method == "max" else sum(terms)/24
                    if n == 24:
                        cue = kz.build_masked_auditory_cue_48(pcm_payload_digest="a"*64,
                            receptor_state_digest="b"*64, receptor_values_digest="c"*64,
                            config_digest=config.config_digest, auditory_source_clock_id="audio.sample",
                            auditory_window_start_tick=9600, auditory_window_end_tick=14400,
                            observed_values=right, band_plan=kz.build_auditory_band_plan_48())
                        if method == "max":
                            scan, _ = ne._a_scan(config, seed(config, ((x[0], 0.0),)), cue, 0)
                            observed = scan.records[0]
                        else:
                            observed, _ = kz._slot_record(bank_role=kz.BANK_ROLES[0], slot_id="neutral.slot",
                                slot_digest="d"*64, values=(left[0],)*48, support=None,
                                threshold=t*factor, cue=cue)
                        self.assertEqual(d.hex(), observed.observed_distance.hex())
                        self.assertEqual(d <= t*factor, observed.observed_match)
                    distances.append(d)
                compare_numbers(f"{route}.{index}", *distances)
                NUMERICAL[-1].update(old_match=distances[0] <= t, new_match=distances[1] <= t*0.5,
                    rational_match=(max(abs(Fraction(a)-Fraction(b)) for a,b in zip(x,y)) if method == "max"
                        else sum(abs(Fraction(a)-Fraction(b)) for a,b in zip(x,y))/n) <= Fraction(t))
                COUNTS["match_pairs"] += 1
        self.assertEqual(30, COUNTS["match_pairs"])

    def test_09_subnormal_visibility(self):
        s, m = math.ulp(0.0), sys.float_info.min
        for index, (x, y) in enumerate(((s, 0.0), (3*s, 4*s), (m, math.nextafter(m, 0.0)))):
            old_x, old_y = (0.0,)*47+(x,), (0.0,)*47+(y,)
            nx, ny = project(old_x).values, project(old_y).values
            do, dn = ppb.normalized_mean_l1_distance(old_x, old_y), ppb.normalized_mean_l1_distance(nx, ny)
            compare_numbers(f"subnormal.{index}", do, dn)
            NUMERICAL[-1].update(old_equal=old_x == old_y, new_equal=nx == ny,
                old_last=(x.hex(), y.hex()), new_last=(nx[-1].hex(), ny[-1].hex()),
                old_key=core.joint_rank_prefix(self.old.tspm_config.fast_config, do, 0.0),
                new_key=core.joint_rank_prefix(self.new.tspm_config.fast_config, dn, 0.0))
            COUNTS["subnormal_pairs"] += 1
        self.assertEqual(0.0, project((s,)*48).values[0])
        self.assertEqual((4*s)*0.5, (3*s)*0.5)

    def test_10_ppb_two_chains(self):
        for chain in ((1/8,)*4, (1/8, 17/128, 15/128, 1/8)):
            trajectories = []
            for config, factor in ((self.old, 1.0), (self.new, 0.5)):
                bank = config.profile.profile.auditory_config
                state = ppb.initial_ppb1_bank_state(bank)
                values = []
                expected = None
                for i, x in enumerate(chain):
                    v = x*factor
                    frame = ReceptorContactFrame("auditory", bank.geometry_id, f"ppb.{i}", "audio.sample",
                                                 i*4800, (i+1)*4800, bank.carrier_ids, (v,)*48)
                    result = ppb.advance_ppb1_bank(bank, state, frame)
                    COUNTS["direct_ppb_steps"] += 1
                    state = result.poststate
                    slot = next(s for s in state.slots if s.occupied)
                    expected = v if expected is None else (1.0-bank.update_rate)*expected + bank.update_rate*v
                    self.assertEqual((expected.hex(),)*48, tuple(z.hex() for z in slot.prototype_values))
                    self.assertEqual(min(3, i+1), slot.support_count)
                    values.append(slot.prototype_values[0])
                    TRACES.append(dict(kind="ppb", scale=factor, step=i, state=state.digest(),
                        slot_digest=ppb._digest(slot.canonical_payload()), support=slot.support_count,
                        prototype_hex=[z.hex() for z in slot.prototype_values]))
                trajectories.append(values)
            for i, (x, y) in enumerate(zip(*trajectories)):
                compare_numbers(f"ppb.{chain}.{i}", x, y)

    def test_11_projection_contact_once(self):
        COUNTS["neutral_receptor_calls"] += 1
        energy = LogSpectralReceptor(LogSpectralConfig()).analyze((0.0,)*4800)
        p = pair(self.new, energy, 0.25)
        self.assertEqual(energy, p.auditory.timed_frame.frame.values)
        self.assertEqual(half.GEOMETRY, p.auditory.timed_frame.frame.geometry_id)
        p = pair(self.new, 0.25, 0.375)
        self.assertEqual((0.125,)*48, p.auditory.timed_frame.frame.values)
        self.assertEqual((0.375,)*288, p.visual.timed_frame.frame.values)

    def test_12_source_mixing_rejected(self):
        with self.assertRaises(memory.S2JWCoordinatorError):
            memory.bind_s2jv_coordinator_input(config=self.new, source=pair(self.old, 0.1, 0.1))
        with self.assertRaises(memory.S2JWCoordinatorError):
            memory.bind_s2jv_coordinator_input(config=self.old, source=pair(self.new, 0.1, 0.1))
        with self.assertRaises(pairing.S2JWPairingError):
            replace(pair(self.new, 0.1, 0.1).plan, source_profile_digest=profile.EXPECTED_SOURCE_PROFILE_DIGEST)

    def test_13_atomic_four_step_compatibility(self):
        outputs = []
        for config in (self.old, self.new):
            state = memory.initial_s2jv_composite_state(config)
            for i, v in enumerate((1/8, 17/128, 15/128, 1/8)):
                before = state.state_digest
                result, source = formation(config, state, pair(config, v, 1/4, i))
                self.assertEqual(before, result.poststate.parent_state_digest)
                self.assertEqual(config.config_digest, result.receipt.config_digest)
                self.assertEqual(config.config_digest, result.owner_poststate.authorized_config_digest)
                self.assertEqual(config.tspm_config.fast_config.digest(), result.poststate.tspm_state.fast_state.fast_config_digest)
                state = result.poststate
                TRACES.append(dict(kind="atomic", config=config.config_digest, receipt=asdict(result.receipt),
                    auditory_slots=[s.canonical_payload() for s in state.tspm_state.auditory_ppb1_state.slots if s.occupied],
                    visual_slots=[s.canonical_payload() for s in state.tspm_state.visual_ppb1_state.slots if s.occupied]))
            self.assertEqual([3], [s.support_count for s in state.tspm_state.auditory_ppb1_state.slots if s.occupied])
            outputs.append(state)
        self.assertEqual(outputs[0].tspm_state.visual_ppb1_state.slots, outputs[1].tspm_state.visual_ppb1_state.slots)
        old_slot = next(s for s in outputs[0].tspm_state.auditory_ppb1_state.slots if s.occupied)
        new_slot = next(s for s in outputs[1].tspm_state.auditory_ppb1_state.slots if s.occupied)
        compare_numbers("atomic.final", old_slot.prototype_values[0], new_slot.prototype_values[0])

    def test_14_core_multimatch_and_relation(self):
        for config in (self.old, self.new):
            state = seed(config, ((3/16, 1/32), (1/32, 1/8)))
            source = memory.bind_s2jv_coordinator_input(config=config, source=pair(config, 0.0, 0.0, 2))
            evidence = direct.direct_scan(config, state, source, mode="FAST_FORMATION")
            candidate = core.advance_tspm1_fast(config.tspm_config, state.tspm_state.fast_state, source.tspm_exposure)
            self.assertTrue(direct.verify_fast_candidate(config, state, source, candidate, evidence))
            core._validate_fast_candidate_relations(config.tspm_config, state.tspm_state.fast_state, source.tspm_exposure, candidate)
            self.assertEqual("tspm1.fast.slot.001", candidate.selected_slot_id)
            TRACES.append(dict(kind="rank", evidence=asdict(evidence)))

    def test_15_native_probe_direct_and_read_only(self):
        for config in (self.old, self.new):
            state = seed(config, ((3/16, 1/32), (1/32, 1/8)))
            probe = memory.bind_s2jv_probe(config=config, source=pair(config, 0.0, 0.0, 2))
            before = state.state_digest
            finding = read.probe_s2jv_composite_read_only(config=config, state=state, probe=probe)
            b4 = direct.direct_scan(config, state, probe, mode="B4_PROBE")
            fast = direct.direct_scan(config, state, probe, mode="FAST_PROBE")
            self.assertTrue(direct.verify_probe(config, state, probe, finding, b4, fast))
            self.assertEqual("tspm1.fast.slot.001", finding.fast_selected.slot_id)
            self.assertEqual(before, state.state_digest)

    def test_16_partial_scans_stay_unranked(self):
        state = memory.initial_s2jv_composite_state(self.new)
        for i in range(4):
            state = formation(self.new, state, pair(self.new, 0.125, 0.25, i))[0].poststate
        cue = adapter.bind_cue(projection=project((0.125,)*48, 4), pcm_digest="a"*64, config=self.new)
        plan = kz.build_auditory_band_plan_48()
        for rule in ne.RULES:
            result = ne.retrieve(rule=rule, config=self.new, state=state, cue=cue, band_plan=plan)
            baseline = ne_direct.direct_retrieve(rule=rule, config=self.new, state=state, cue=cue, band_plan=plan)
            for arm in (result, baseline):
                ne_direct.verify_arm(arm=arm, config=self.new, state=state, cue=cue, band_plan=plan)
            self.assertEqual(result.evidence.bank_scans, baseline.evidence.bank_scans)
            self.assertEqual(result.evidence.decision, baseline.evidence.decision)
            self.assertIsNone(result.evidence.ranking)
            self.assertEqual([0.1, 0.1, 0.01], [b.records[0].match_threshold for b in result.evidence.bank_scans])
            self.assertEqual((9, 3, 8), tuple(len(b.records) for b in result.evidence.bank_scans))
            self.assertEqual(state.state_digest, result.evidence.prestate_digest)
            self.assertEqual(state.state_digest, result.evidence.poststate_digest)
            self.assertLess(len(kz.canonical_bytes(result.canonical_payload())), 32768)

    def test_17_empty_valid_abstention(self):
        state = memory.initial_s2jv_composite_state(self.new)
        probe = memory.bind_s2jv_probe(config=self.new, source=pair(self.new, 0.0, 0.0))
        finding = read.probe_s2jv_composite_read_only(config=self.new, state=state, probe=probe)
        b4 = direct.direct_scan(self.new, state, probe, mode="B4_PROBE")
        fast = direct.direct_scan(self.new, state, probe, mode="FAST_PROBE")
        self.assertTrue(direct.verify_probe(self.new, state, probe, finding, b4, fast))
        self.assertIsNone(finding.fast_selected)

    def test_18_tampered_rank_evidence(self):
        state = seed(self.new, ((3/16, 1/32), (1/32, 1/8)))
        probe = memory.bind_s2jv_probe(config=self.new, source=pair(self.new, 0.0, 0.0, 2))
        evidence = direct.direct_scan(self.new, state, probe, mode="FAST_PROBE")
        for broken in (replace(evidence, rows=evidence.rows[::-1]),
                       replace(evidence, selected_slot_id="tspm1.fast.slot.000"),
                       replace(evidence, selected_slot_digest="0"*64),
                       replace(evidence, selected_key=(0.0, 0.0, "wrong"))):
            with self.assertRaises(direct.RankBindingError):
                direct.verify_evidence(self.new, state, probe, broken)

    def test_19_manipulated_native_slot_rejected(self):
        state = seed(self.new, ((3/16, 1/32), (1/32, 1/8)))
        probe = memory.bind_s2jv_probe(config=self.new, source=pair(self.new, 0.0, 0.0, 2))
        native = core.probe_tspm1_read_only(self.new.tspm_config, state.tspm_state, probe.tspm_probe)
        broken = deepcopy(native)
        object.__setattr__(broken, "fast_slot_id", "tspm1.fast.slot.000")
        with self.assertRaises(core.TSPM1Error):
            core._validate_read_only_finding_relations(self.new.tspm_config, state.tspm_state, probe.tspm_probe, broken)

    def test_20_state_and_owner_scale_rejection(self):
        old_state = memory.initial_s2jv_composite_state(self.old)
        with self.assertRaises(core.TSPM1Error):
            memory._validate_state(self.new, old_state)
        new_state = memory.initial_s2jv_composite_state(self.new)
        source = memory.bind_s2jv_coordinator_input(config=self.new, source=pair(self.new, 0.0, 0.0))
        owner = memory.S2JVFormationOwner("mixed.owner", "mixed.auth", "mixed.use", self.old.config_digest,
                                         new_state.state_digest, source.input_digest)
        with self.assertRaises(memory.S2JWCoordinatorError):
            owner.consume_once(self.new, new_state, source)
        self.assertEqual("FAILED", owner.snapshot().status)
        self.assertEqual(0, new_state.generation)

    def test_21_stale_source_rejected(self):
        p = pair(self.new, 0.125, 0.25)
        state = formation(self.new, memory.initial_s2jv_composite_state(self.new), p)[0].poststate
        source = memory.bind_s2jv_coordinator_input(config=self.new, source=p)
        with self.assertRaises(core.TSPM1Error):
            direct.direct_scan(self.new, state, source, mode="FAST_FORMATION")

    def test_22_output_and_numeric_state_limits(self):
        state = seed(self.new, ((0.1, 0.1), (0.3, 0.3), (0.5, 0.5)))
        probe = memory.bind_s2jv_probe(config=self.new, source=pair(self.new, 0.2, 0.2, 3))
        evidence = direct.direct_scan(self.new, state, probe, mode="FAST_PROBE")
        self.assertEqual(1008, evidence.term_count)
        self.assertLessEqual(len(half.canonical(asdict(evidence))), direct.MAX_RANK_BYTES)
        self.assertEqual(44544, self.new.ledger_limits.maximum_state_float64_bytes)
        self.assertLessEqual(len(half.canonical(asdict(pair(self.new, 0.125, 0.25)))), adapter.MAX_PAIR_BYTES)

    def test_23_actual_ties_in_probe(self):
        for config in (self.old, self.new):
            state = seed(config, ((1/8, 1/8), (1/8, 1/8)))
            probe = memory.bind_s2jv_probe(config=config, source=pair(config, 0.0, 0.0, 2))
            finding = read.probe_s2jv_composite_read_only(config=config, state=state, probe=probe)
            self.assertEqual("tspm1.fast.slot.000", finding.fast_selected.slot_id)
            self.assertEqual("b4.slot.001", finding.b4_selected.slot_id)
            self.assertTrue(direct.verify_probe(config, state, probe, finding,
                direct.direct_scan(config, state, probe, mode="B4_PROBE"),
                direct.direct_scan(config, state, probe, mode="FAST_PROBE")))

    def test_24_legacy_initial_payload_reconstruction(self):
        state = core.initial_tspm1_composite_state(self.old.tspm_config)
        fast = state.fast_state
        payload = dict(schema_version="tspm1.private.v1", fast_bank_id="tspm1.fast",
            fast_config_digest=profile.EXPECTED_FAST_CONFIG_DIGEST, accepted_exposure_count=0,
            auditory_source_clock_id=None, auditory_last_end_tick=None,
            visual_source_clock_id=None, visual_last_end_tick=None,
            slots=[dict(slot_id=f"tspm1.fast.slot.{i:03d}", occupied=False, auditory_values=[],
                visual_values=[], support_count=None, last_selected_step=None, consolidation_count=0,
                last_consolidation_exposure_digest=None) for i in range(3)])
        self.assertEqual(payload, fast.payload_without_digest())
        self.assertEqual(core._digest(payload), fast.fast_state_digest)

    @classmethod
    def tearDownClass(cls):
        output = os.environ.get("S2NL_QUAL_DIR")
        if output:
            payload = dict(numerical=NUMERICAL, traces=TRACES, counters=COUNTS,
                historical_config_digest=cls.old.config_digest, new_config_digest=cls.new.config_digest,
                new_profile=asdict(cls.new.profile), universal_float_guarantee=False)
            data = half.canonical(payload)
            if len(data) > 1048576:
                raise AssertionError("QUALIFICATION_ARTIFACT_LIMIT")
            with (Path(output)/"observations.json").open("xb") as handle:
                handle.write(data)
