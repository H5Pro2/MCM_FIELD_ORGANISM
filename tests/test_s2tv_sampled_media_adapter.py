from fractions import Fraction
import unittest

from tools import _s2tv_sampled_media_adapter as s


def receipt(event):
    midpoint_ticks = event.midpoint * 30000
    before = midpoint_ticks.numerator // midpoint_ticks.denominator
    return s.bind_frame(event, frame_pts=before, next_frame_pts=before + 1)


class SampledMediaAdapterTests(unittest.TestCase):
    def test_fixed_budget_and_second_pass_clock(self):
        events = s.schedule()
        self.assertEqual(len(events), 24)
        self.assertEqual(s.budget(events), dict(events=24, formations=20, audio_hints=2, visual_hints=2,
            audio_analyses=22, nj_projections=22, visual_analyses=22, scans=8, field_contacts=7392))
        p1 = next(event for event in events if event.pass_number == 1 and event.media_start == Fraction(1))
        p2 = next(event for event in events if event.pass_number == 2 and event.media_start == Fraction(1))
        self.assertLess(p1.runtime_time, p2.runtime_time)
        self.assertEqual(p2.media_start, Fraction(1))

    def test_frame_binding_keeps_native_rate_and_rejects_wrong_frame(self):
        event = s.schedule()[0]
        bound = receipt(event)
        self.assertEqual(bound["frame_rate"], [30000, 1001])
        self.assertEqual(bound["video_time_base"], [1, 30000])
        with self.assertRaisesRegex(s.S2TVError, "FRAME_SELECTION_INVALID"):
            s.bind_frame(event, frame_pts=1501, next_frame_pts=1502)
        with self.assertRaisesRegex(s.S2TVError, "VIDEO_PROFILE_INVALID"):
            s.bind_frame(event, frame_pts=1500, next_frame_pts=1501, frame_rate=(30, 1))

    def test_open_next_status_stop_is_ordered_and_non_restarting(self):
        events = s.schedule()
        session = s.SampleSession(events)
        self.assertEqual(session.open()["completed"], 0)
        event = session.next(receipt(events[0]))
        self.assertEqual(event.event_id, events[0].event_id)
        self.assertEqual(session.status()["next_event"], events[1].event_id)
        with self.assertRaisesRegex(s.S2TVError, "RECEIPT_BINDING_INVALID"):
            session.next(receipt(events[2]))
        self.assertEqual(session.stop()["closure"], "INCOMPLETE")
        with self.assertRaisesRegex(s.S2TVError, "SESSION_CLOSED"):
            session.next(receipt(events[1]))
