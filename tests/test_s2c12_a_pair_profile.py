from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.s2_reference_runner import (
    S2APairProfile,
    S2APairProfileEntry,
    S2C1IdentityControl,
    S2R2C2PairResult,
    S2R4C4PairResult,
    S2R8C8PairResult,
    S2ReferenceRunnerError,
    S2ScalarMetric,
    assemble_s2c12_a_pair_profile,
)


_DIGEST_A = "a" * 64
_DIGEST_B = "b" * 64
_DIGEST_C = "c" * 64
_DIGEST_D = "d" * 64


def _pairs(model_id: str) -> tuple[
    S2C1IdentityControl,
    S2R2C2PairResult,
    S2R4C4PairResult,
    S2R8C8PairResult,
]:
    coupling = 0.0 if model_id == "b0" else 0.25
    values = (0.0, 0.0, 0.0, 0.0) if model_id == "b0" else (0.0, 0.1, 0.2, 0.3)
    common = {
        "model_id": model_id,
        "coupling_rate_per_second": coupling,
        "probe_plan_digest": _DIGEST_C,
        "probe_digest": _DIGEST_D,
        "support_count": 31,
    }
    return (
        S2C1IdentityControl(
            **common,
            r1_formation_digest=_DIGEST_A,
            c1_formation_digest=_DIGEST_B,
            metric=S2ScalarMetric("d_pair", values[0]),
        ),
        S2R2C2PairResult(
            **common,
            r2_formation_digest=_DIGEST_A,
            c2_formation_digest=_DIGEST_B,
            metric=S2ScalarMetric("d_pair", values[1]),
        ),
        S2R4C4PairResult(
            **common,
            r4_formation_digest=_DIGEST_A,
            c4_formation_digest=_DIGEST_B,
            metric=S2ScalarMetric("d_pair", values[2]),
        ),
        S2R8C8PairResult(
            **common,
            r8_formation_digest=_DIGEST_A,
            c8_formation_digest=_DIGEST_B,
            metric=S2ScalarMetric("d_pair", values[3]),
        ),
    )


class S2C12APairProfileTests(unittest.TestCase):
    def test_b0_profile_is_exact_zero_without_decision_fields(self) -> None:
        profile = assemble_s2c12_a_pair_profile(*_pairs("b0"))

        self.assertEqual((1, 2, 4, 8), profile.contact_counts)
        self.assertEqual((0.0, 0.0, 0.0, 0.0), profile.d_pair_values)
        self.assertFalse(hasattr(profile, "decision"))
        self.assertFalse(hasattr(profile, "trend"))

    def test_b2_profile_preserves_only_ordered_scalars_and_is_reproducible(self) -> None:
        first = assemble_s2c12_a_pair_profile(*_pairs("b2"))
        second = assemble_s2c12_a_pair_profile(*_pairs("b2"))

        self.assertEqual((0.0, 0.1, 0.2, 0.3), first.d_pair_values)
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(64, len(first.digest()))

    def test_profile_rejects_mixed_model_arms(self) -> None:
        n1, n2, n4, _ = _pairs("b0")
        n8 = _pairs("b2")[3]

        with self.assertRaisesRegex(S2ReferenceRunnerError, "matching model arm"):
            assemble_s2c12_a_pair_profile(n1, n2, n4, n8)

    def test_profile_rejects_different_probe_support(self) -> None:
        n1, n2, n4, n8 = _pairs("b2")
        n8 = replace(n8, probe_digest=_DIGEST_A)

        with self.assertRaisesRegex(S2ReferenceRunnerError, "one probe support"):
            assemble_s2c12_a_pair_profile(n1, n2, n4, n8)

    def test_profile_rejects_wrong_pair_position(self) -> None:
        n1, n2, n4, n8 = _pairs("b2")

        with self.assertRaisesRegex(S2ReferenceRunnerError, "typed n=1,2,4,8"):
            assemble_s2c12_a_pair_profile(n1, n4, n2, n8)  # type: ignore[arg-type]

    def test_direct_profile_rejects_nonzero_b0_entry(self) -> None:
        entries = tuple(
            S2APairProfileEntry(
                count,
                _DIGEST_A,
                S2ScalarMetric("d_pair", value),
            )
            for count, value in zip((1, 2, 4, 8), (0.0, 0.0, 0.1, 0.0), strict=True)
        )

        with self.assertRaisesRegex(S2ReferenceRunnerError, "B0 profile"):
            S2APairProfile(
                "b0",
                0.0,
                _DIGEST_C,
                _DIGEST_D,
                31,
                entries,
            )


if __name__ == "__main__":
    unittest.main()
