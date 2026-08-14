from __future__ import annotations

import unittest

from mcm_field_organism.w7bn_const_v_shard_executor import (
    W7BNConstVShardExecutorError,
    execute_w7bn_const_v_role_shard,
)


class W7BNConstVShardExecutorTests(unittest.TestCase):
    def test_invalid_shard_is_rejected_before_runtime(self) -> None:
        with self.assertRaises(W7BNConstVShardExecutorError):
            execute_w7bn_const_v_role_shard(
                object(), object(), object(), object(), object(), object(), object(), "xx", 1
            )

    def test_executor_is_not_publicly_exported(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(mcm_field_organism, "execute_w7bn_const_v_role_shard"))
        self.assertFalse(hasattr(current_api, "execute_w7bn_const_v_role_shard"))


if __name__ == "__main__":
    unittest.main()
