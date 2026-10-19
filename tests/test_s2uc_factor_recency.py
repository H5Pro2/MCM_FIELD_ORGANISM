import unittest
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_factor_hint import FactorHintArm
from tools._s2uc_perception_recency import PerceptionRecencyArm
from tests.test_s2uc_perception_recency import RecencyIntegrationTests
from unittest.mock import patch
class CombinedMethodTests(unittest.TestCase):
    def test_exact_method_reuse(self):
        self.assertIs(FactorRecencyArm.hint,FactorHintArm.hint)
        for name in ('form','close_segment','close_owner','resources'):
            self.assertIs(getattr(FactorRecencyArm,name),getattr(PerceptionRecencyArm,name))
    def test_recency_controls_on_combined_class(self):
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(RecencyIntegrationTests)
        # hint_inherited asserts the separate E-only class identity; all behavioral controls apply.
        suite=unittest.TestSuite(t for t in suite if t._testMethodName!='test_hint_inherited')
        with patch('tests.test_s2uc_perception_recency.PerceptionRecencyArm',FactorRecencyArm):
            result=unittest.TestResult();suite.run(result)
        self.assertEqual(result.testsRun,8);self.assertEqual(result.errors,[]);self.assertEqual(result.failures,[])
if __name__=='__main__':unittest.main()
