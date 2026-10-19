import unittest
from tools import _s2tw_source_schedule as schedule


class ScheduleTests(unittest.TestCase):
    def test_bound_counts_and_materialized_endpoints_are_distinct(self):
        bound = schedule.binding()
        self.assertEqual((len(bound["events"]), sum(event["source_id"] is not None for event in bound["events"])), (26, 22))
        self.assertEqual(bound["resources"]["native_vector_peak_both_arms"], 10752)
