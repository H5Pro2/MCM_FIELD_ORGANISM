"""Regression qualification for the S2-LQ auditory cue preflight adapter."""

from __future__ import annotations

import unittest

from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as auditory_scan
from tools import _s2lm_private_role_free_stream_processor as stream
from tools import _s2lo_private_role_free_stream_runner as lo_runner
from tools import _s2lq_private_multipattern_stream_runner as runner


QUALIFICATION_ID = "s2lq-auditory-cue-preflight-qualification-20260904-01"


class S2LQAuditoryCuePreflightRegressionTests(unittest.TestCase):
    def test_all_four_auditory_cues_use_validated_observed_bands(self) -> None:
        self.assertFalse(runner.MAIN_EXECUTION_ENABLED)
        config = lo_runner._build_config()
        preflight, materialized = runner._source_geometry_preflight(config)

        auditory_operations = tuple(
            item.operation_payload
            for item in materialized
            if item.spec.event_type == "PARTIAL_AUDITORY_CUE"
        )
        self.assertEqual(4, len(auditory_operations))
        plan = auditory_scan.build_auditory_band_plan_48()
        for operation in auditory_operations:
            self.assertIs(type(operation), stream.AuditoryCueOperationV1)
            cue = auditory_scan._validate_cue(operation.cue, plan)
            observed = tuple(
                float(cue.values[index]) for index in auditory_scan.OBSERVED_BANDS
            )
            self.assertEqual(24, len(observed))
            self.assertEqual(
                cue.observed_values_digest,
                auditory_scan.digest(list(observed)),
            )

        self.assertEqual(8, preflight["cue_count"])
        self.assertEqual(0, preflight["memory_calls"])
        self.assertFalse(runner.MAIN_EXECUTION_ENABLED)


if __name__ == "__main__":
    unittest.main()
