"""Local integration only: unchanged factor hint and exact recency methods."""
from tools._s2uc_perception_recency import PerceptionRecencyArm
from tools._s2uc_factor_hint import FactorHintArm

class FactorRecencyArm(PerceptionRecencyArm):
    hint = FactorHintArm.hint
