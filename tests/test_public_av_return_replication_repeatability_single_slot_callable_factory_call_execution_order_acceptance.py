from dataclasses import replace
import unittest

from audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order import (
    build_callable_factory_call_execution_order,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order_acceptance import *
class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.accepted_order=build_callable_factory_call_execution_order(1)
    def test_accepts_locked_execution_order(self):
        a=accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order(self.accepted_order); self.assertTrue(a.acceptance_complete); self.assertFalse(a.execution_order.future_callable_call_execution_step.executed)
    def test_rejects_execution_surfaces(self):
        a=accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order(self.accepted_order)
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptanceError): replace(a, callable_factory_called=True)
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionOrderAcceptanceError): execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_order(a)
    def test_json_has_no_result_or_score(self):
        p=public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order_acceptance_to_jsonable(accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order(self.accepted_order)); self.assertNotIn("result",p); self.assertNotIn("memory_score",p)
