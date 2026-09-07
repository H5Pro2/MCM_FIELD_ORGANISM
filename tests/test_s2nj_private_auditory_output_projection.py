"""Fixed neutral PCM only. No NH sources or integration calls."""

from copy import deepcopy
from dataclasses import FrozenInstanceError, asdict, replace
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import unittest

from mcm_field_organism.broadband_hearing_path import AuditoryReceptorContact, AuditoryReceptorState
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from tools import _s2nj_private_auditory_output_projection as p


NEUTRAL_CASES = (
    ("zero", "constant", (0.0,)),
    ("positive-full", "constant", (1.0,)),
    ("negative-full", "constant", (-1.0,)),
    ("alternating-full", "alternating", (1.0, -1.0)),
    ("impulse-edge", "impulse", (0, 1.0)),
    ("impulse-center", "impulse", (2400, -1.0)),
    ("mixture-one", "sines", ((300.0, 0.25, 0.0), (1100.0, 0.25, 0.5), (6000.0, 0.25, 1.0))),
    ("mixture-two", "sines", ((440.0, 0.4, 0.125), (3000.0, 0.2, 0.75), (11000.0, 0.1, -0.25))),
)
MEASUREMENTS = []
COUNTERS = dict(pcm_generations=0, receptor_calls=0, completed_analyses=0, recorded_projections=0)


def pcm(case):
    COUNTERS["pcm_generations"] += 1
    _, kind, args = case
    result = bytearray(4800*4)
    for n in range(4800):
        if kind == "constant":
            value = args[0]
        elif kind == "alternating":
            value = args[n % 2]
        elif kind == "impulse":
            value = args[1] if n == args[0] else 0.0
        else:
            value = sum(amplitude * math.sin(((2.0*math.pi*frequency*n)/48000)+phase)
                        for frequency, amplitude, phase in args)
        struct.pack_into("<f", result, n*4, value)
    return result


def state(values=None):
    values = (0.0,)*48 if values is None else values
    return AuditoryReceptorState("auditory", p.RAW_GEOMETRY, 0, 0, 4800,
        tuple(b.channel_id for b in p.spectral.logarithmic_bands(LogSpectralConfig())), values,
        AuditoryReceptorContact.ACTIVE_ENERGY if any(v != 0.0 for v in values) else AuditoryReceptorContact.ACTIVE_ZERO)


def project(s, **kwargs):
    return p.project_auditory_half_v1(s, config=kwargs.get("config", LogSpectralConfig()),
                                    source_profile_digest=kwargs.get("source_profile_digest", p.RAW_PROFILE_DIGEST))


class ProjectionTests(unittest.TestCase):
    def test_01_real_fixed_pcm(self):
        receptor = LogSpectralReceptor(LogSpectralConfig())
        for spec in NEUTRAL_CASES:
            with self.subTest(case=spec[0]):
                payload = pcm(spec)
                payload_sha = hashlib.sha256(payload).hexdigest()
                samples = tuple(v[0] for v in struct.iter_unpack("<f", payload))
                self.assertTrue(all(math.isfinite(v) and abs(v) <= 1 for v in samples))
                COUNTERS["receptor_calls"] += 1
                energy = receptor.analyze(samples)
                COUNTERS["completed_analyses"] += 1
                del samples, payload
                raw = state(energy)
                before = raw.digest()
                scaled = project(raw)
                reference = tuple(float(Fraction.from_float(v)/2) for v in energy)
                self.assertEqual(tuple(v.hex() for v in scaled.values), tuple(v.hex() for v in reference))
                self.assertEqual(before, raw.digest())
                self.assertTrue(all(math.isfinite(v) and 0 <= v <= 1 for v in scaled.values))
                MEASUREMENTS.append(dict(case_id=spec[0], pcm_sha256=payload_sha, raw_state_digest=before,
                    raw_values=list(energy), raw_hex=[v.hex() for v in energy],
                    projection=asdict(scaled), output_hex=[v.hex() for v in scaled.values],
                    raw_max=max(energy), output_max=max(scaled.values),
                    output_bytes=len(p.canonical(asdict(scaled)))))
                COUNTERS["recorded_projections"] += 1

    def test_02_profile_mismatch(self):
        for key, value in (("sample_rate", 44100), ("window_size", 9600), ("hop_size", 240),
                           ("min_frequency", 60.0), ("max_frequency", 17000.0), ("band_count", 47)):
            with self.subTest(key=key), self.assertRaises(p.S2NJProjectionError):
                project(state(), config=replace(LogSpectralConfig(), **{key: value}))
        for h in (p.PROFILE_DIGEST, "0"*64, None):
            with self.subTest(digest=h), self.assertRaises(p.S2NJProjectionError):
                project(state(), source_profile_digest=h)
        wrong_type = LogSpectralConfig()
        object.__setattr__(wrong_type, "sample_rate", 48000.0)
        with self.assertRaises(p.S2NJProjectionError): project(state(), config=wrong_type)

    def test_03_scale_type_separation(self):
        output = project(state())
        self.assertNotIsInstance(output, AuditoryReceptorState)
        self.assertNotEqual(p.GEOMETRY, p.RAW_GEOMETRY)
        self.assertNotEqual(p.PROFILE_DIGEST, p.RAW_PROFILE_DIGEST)
        with self.assertRaises(p.S2NJProjectionError): project(output)
        with self.assertRaises(p.S2NJProjectionError): project(replace(state(), geometry_id=p.GEOMETRY))

    def test_04_dimensions_and_types(self):
        for values in ([0.0]*48, (0.0,)*47, (0.0,)*49, (False,)+(0.0,)*47, (0,)+(0.0,)*47):
            with self.subTest(values=type(values)), self.assertRaises(p.S2NJProjectionError):
                project(state(values))

    def test_05_carrier_binding(self):
        raw = state()
        for carriers in (list(raw.carrier_ids), raw.carrier_ids[::-1], (raw.carrier_ids[0],)*48):
            with self.subTest(carriers=type(carriers)), self.assertRaises(p.S2NJProjectionError):
                project(replace(raw, carrier_ids=carriers))

    def test_06_time_and_modality(self):
        for changes in (dict(snapshot_index=True), dict(window_start_sample=-1), dict(window_end_sample=4801),
                        dict(snapshot_index=1), dict(modality_id="visual")):
            with self.subTest(changes=changes), self.assertRaises(p.S2NJProjectionError):
                project(replace(state(), **changes))
        valid = replace(state(), snapshot_index=10, window_start_sample=4800, window_end_sample=9600)
        self.assertEqual(project(valid).window_end_tick, 9600)

    def test_07_nonfinite_no_partial_projection(self):
        for bad in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=repr(bad)):
                published = None
                with self.assertRaises(p.S2NJProjectionError):
                    published = project(state((0.5,)*47+(bad,)))
                self.assertIsNone(published)

    def test_08_negative_and_activity(self):
        for raw in (state((-1.0,)+(0.0,)*47), state((-float.fromhex("0x0.0000000000001p-1022"),)+(0.0,)*47),
                    replace(state(), contact=AuditoryReceptorContact.ACTIVE_ENERGY)):
            with self.subTest(raw=raw.energy[0]), self.assertRaises(p.S2NJProjectionError): project(raw)

    def test_09_inclusive_boundary_no_clipping(self):
        self.assertEqual(project(state((2.0,)*48)).values, (1.0,)*48)
        self.assertEqual(project(state((1.5,)*48)).values, (0.75,)*48)
        with self.assertRaises(p.S2NJProjectionError):
            project(state((0.0,)*47+(math.nextafter(2.0, math.inf),)))

    def test_10_subnormal_and_underflow(self):
        tiny = float.fromhex("0x0.0000000000001p-1022")
        raw = state((tiny, tiny*2, tiny*3, sys.float_info.min)+(0.0,)*44)
        output = project(raw)
        self.assertEqual(output.values[:4], (0.0, tiny, tiny*2, sys.float_info.min/2))
        self.assertEqual(output.underflow_band_indices, (0,))
        self.assertEqual(output.subnormal_band_indices, (1, 2, 3))

    def test_11_signed_zero(self):
        output = project(state((-0.0,)+(0.0,)*47))
        self.assertEqual(output.values[0].hex(), "-0x0.0p+0")
        self.assertEqual(output.underflow_band_indices, ())

    def test_12_immutable_source_and_output(self):
        raw = state((0.25,)*48)
        before = deepcopy(raw.canonical_payload())
        output = project(raw)
        self.assertEqual(raw.canonical_payload(), before)
        with self.assertRaises(FrozenInstanceError): output.values = ()
        with self.assertRaises(FrozenInstanceError): raw.energy = ()
        changed_payload = output.payload()
        changed_payload["values"] = [1.0]*48
        self.assertEqual(output.values, (0.125,)*48)

    def test_13_output_tampering(self):
        original = project(state())
        for changes in (dict(profile_digest=p.RAW_PROFILE_DIGEST), dict(source_state_digest="invalid"),
                        dict(clock_id="video.frame"), dict(projection_digest="0"*64), dict(values=[0.0]*48),
                        dict(values=(float("inf"),)+(0.0,)*47), dict(underflow_band_indices=(49,))):
            with self.subTest(changes=tuple(changes)), self.assertRaises(p.S2NJProjectionError):
                replace(original, **changes)
        corrupt = deepcopy(original)
        object.__setattr__(corrupt, "values", (0.25,)*48)
        with self.assertRaises(p.S2NJProjectionError): p.validate_projection(corrupt)

    def test_14_digest_binding(self):
        raw = state((0.125,)*48)
        output = project(raw)
        self.assertEqual(output.source_state_digest, raw.digest())
        self.assertEqual(output.source_values_digest, p.digest(list(raw.energy)))
        self.assertEqual(output.projection_digest, p.digest(output.payload()))
        self.assertEqual(p.PROFILE_DIGEST, p.digest(p.profile_payload()))
        self.assertEqual(p.RAW_PROFILE_DIGEST, p.digest(p.raw_profile_payload()))

    def test_15_output_bound(self):
        value = math.nextafter(2.0, 0.0)
        output = project(state((value,)*48))
        data = p.canonical(asdict(output))
        self.assertLessEqual(len(data), 16384)
        self.assertNotIn("samples", json.loads(data))
        self.assertEqual(len(output.values), 48)
        self.assertEqual(output.values[0].hex(), float(Fraction.from_float(value)/2).hex())

    def test_16_no_integration_imports(self):
        for name in ("tools._s2nh_private_runtime_binding", "tools._s2ng_private_runtime_comparison",
                     "tools._s2mr_private_minimal_mcm_runtime", "tools._s2jw_profiled_memory_coordinator",
                     "mcm_field_organism.receptor_contract", "mcm_field_organism._ppb1_reference"):
            self.assertNotIn(name, sys.modules)


def tearDownModule():
    destination = os.environ.get("S2NJ_QUAL_DIR")
    if destination:
        with (Path(destination)/"observations.json").open("xb") as f:
            f.write(p.canonical(dict(neutral_cases=MEASUREMENTS, counters=COUNTERS,
                                     profile=p.profile_payload(), raw_profile=p.raw_profile_payload())))
