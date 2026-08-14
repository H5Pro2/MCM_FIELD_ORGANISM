from __future__ import annotations

import unittest

from mcm_field_organism.e1_completion_aligned_refinement import (
    _handoff_digest as envelope_digest,
)
from mcm_field_organism.e1_handoff_digest_schemas import e1_handoff_digest_pair
from mcm_field_organism.e1_refined_formation_runner import (
    _handoff_digest as assignment_digest,
)


class E1HandoffDigestSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from tests.test_e1_common_probe_n2_r2_object_handoff import (
            E1CommonProbeN2R2ObjectHandoffTests,
        )

        E1CommonProbeN2R2ObjectHandoffTests.setUpClass()
        cls.handoff = E1CommonProbeN2R2ObjectHandoffTests()._prepare()

    def test_pair_reproduces_both_legacy_digest_schemas(self) -> None:
        plan = self.handoff.formation_slots[0].formation_plan
        pair = e1_handoff_digest_pair(plan.handoff)

        self.assertEqual(assignment_digest(plan.handoff), pair.assignment_digest)
        self.assertEqual(envelope_digest(plan.handoff), pair.envelope_digest)
        self.assertEqual(plan.handoff_digest, pair.envelope_digest)
        self.assertNotEqual(pair.assignment_digest, pair.envelope_digest)


if __name__ == "__main__":
    unittest.main()
