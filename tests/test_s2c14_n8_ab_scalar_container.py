from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.s2_reference_runner import (
    S2N8ABScalarContainer,
    S2R8BC8BPairResult,
    S2R8C8PairResult,
    S2ReferenceRunnerError,
    S2ScalarMetric,
    assemble_s2c14_n8_ab_scalar_container,
)


_DIGEST_A = "a" * 64
_DIGEST_B = "b" * 64
_DIGEST_C = "c" * 64
_DIGEST_D = "d" * 64


def _pairs(model_id: str) -> tuple[S2R8C8PairResult, S2R8BC8BPairResult]:
    coupling = 0.0 if model_id == "b0" else 0.25
    values = (0.0, 0.0) if model_id == "b0" else (0.3, 0.2)
    common = {
        "model_id": model_id,
        "coupling_rate_per_second": coupling,
        "probe_plan_digest": _DIGEST_C,
        "probe_digest": _DIGEST_D,
        "support_count": 31,
    }
    return (
        S2R8C8PairResult(
            **common,
            r8_formation_digest=_DIGEST_A,
            c8_formation_digest=_DIGEST_B,
            metric=S2ScalarMetric("d_pair", values[0]),
        ),
        S2R8BC8BPairResult(
            **common,
            r8b_formation_digest=_DIGEST_A,
            c8b_formation_digest=_DIGEST_B,
            metric=S2ScalarMetric("d_pair", values[1]),
        ),
    )


class S2C14N8ABScalarContainerTests(unittest.TestCase):
    def test_b0_container_preserves_two_exact_zero_scalars(self) -> None:
        container = assemble_s2c14_n8_ab_scalar_container(*_pairs("b0"))

        self.assertEqual(0.0, container.a_d_pair)
        self.assertEqual(0.0, container.b_d_pair)
        self.assertFalse(hasattr(container, "difference"))
        self.assertFalse(hasattr(container, "delta"))
        self.assertFalse(hasattr(container, "decision"))
        self.assertFalse(hasattr(container, "world_specificity"))

    def test_b2_container_preserves_named_scalars_and_is_reproducible(self) -> None:
        first = assemble_s2c14_n8_ab_scalar_container(*_pairs("b2"))
        second = assemble_s2c14_n8_ab_scalar_container(*_pairs("b2"))

        self.assertEqual((0.3, 0.2), (first.a_d_pair, first.b_d_pair))
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertNotEqual(first.a_pair_digest, first.b_pair_digest)

    def test_container_rejects_mixed_model_arms(self) -> None:
        a_pair = _pairs("b0")[0]
        b_pair = _pairs("b2")[1]

        with self.assertRaisesRegex(S2ReferenceRunnerError, "matching model arm"):
            assemble_s2c14_n8_ab_scalar_container(a_pair, b_pair)

    def test_container_rejects_different_probe_support(self) -> None:
        a_pair, b_pair = _pairs("b2")
        b_pair = replace(b_pair, probe_digest=_DIGEST_A)

        with self.assertRaisesRegex(S2ReferenceRunnerError, "one probe support"):
            assemble_s2c14_n8_ab_scalar_container(a_pair, b_pair)

    def test_container_rejects_reversed_pair_types(self) -> None:
        a_pair, b_pair = _pairs("b2")

        with self.assertRaisesRegex(S2ReferenceRunnerError, "typed A8 and B8"):
            assemble_s2c14_n8_ab_scalar_container(  # type: ignore[arg-type]
                b_pair,
                a_pair,
            )

    def test_direct_b0_container_rejects_nonzero_scalar(self) -> None:
        with self.assertRaisesRegex(S2ReferenceRunnerError, "must remain zero"):
            S2N8ABScalarContainer(
                "b0",
                0.0,
                _DIGEST_C,
                _DIGEST_D,
                31,
                _DIGEST_A,
                _DIGEST_B,
                S2ScalarMetric("d_pair", 0.0),
                S2ScalarMetric("d_pair", 0.1),
            )


if __name__ == "__main__":
    unittest.main()
