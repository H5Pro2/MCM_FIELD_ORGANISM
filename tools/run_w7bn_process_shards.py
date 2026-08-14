"""Private W7-BN process-shard runner; emits only an in-memory summary."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

from mcm_field_organism.w7bc_const_v_r124_trajectory_contract import (
    build_w7bc_const_v_r124_trajectory_contract,
)
from mcm_field_organism.w7bd_const_v_runtime_adapter import (
    build_w7bd_const_v_runtime_adapter,
)
from mcm_field_organism.w7bj_const_v_r4_convergence_contract import (
    build_w7bj_const_v_r4_convergence_contract,
)
from mcm_field_organism.w7bl_const_v_seven_path_gate import (
    build_w7bl_const_v_seven_path_gate,
)
from mcm_field_organism.w7bn_const_v_shard_executor import (
    execute_w7bn_const_v_role_shard,
)
from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7w_symmetric_source_family import (
    build_w7w_source_authorization,
    build_w7w_symmetric_source_family,
)
from mcm_field_organism.w7y_seven_path_source_plan import (
    build_w7y_seven_path_source_plan,
)


PATHS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
REFINEMENTS = (1, 2, 4)


def run_one(item: tuple[str, int]) -> tuple[str, int, str, str]:
    path_id, refinement = item
    matrix = build_w7m_capacity_function_matrix_adapter()
    adapter = build_w7bd_const_v_runtime_adapter(
        matrix,
        build_w7bc_const_v_r124_trajectory_contract(),
    )
    family = build_w7w_symmetric_source_family(matrix)
    authorization = build_w7w_source_authorization(matrix, family)
    plan = build_w7y_seven_path_source_plan(matrix, family, authorization)
    contract = build_w7bj_const_v_r4_convergence_contract()
    gate = build_w7bl_const_v_seven_path_gate(plan, contract)
    shard = execute_w7bn_const_v_role_shard(
        matrix,
        family,
        authorization,
        plan,
        adapter,
        contract,
        gate,
        path_id,
        refinement,
    )
    return path_id, refinement, shard.role.role_digest, shard.shard_digest


def main() -> None:
    items = tuple(
        (path_id, refinement)
        for refinement in REFINEMENTS
        for path_id in PATHS
    )
    results = []
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=4, mp_context=context) as pool:
        futures = tuple(pool.submit(run_one, item) for item in items)
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: (item[1], item[0]))
    expected = tuple(
        (path_id, refinement)
        for refinement in REFINEMENTS
        for path_id in PATHS
    )
    if tuple(item[:2] for item in results) != expected:
        raise RuntimeError("W7-BN shard inventory is incomplete or unordered")
    if len({item[:2] for item in results}) != 21:
        raise RuntimeError("W7-BN shard inventory contains duplicates")
    print(f"complete_roles={len(results)}")
    print(f"role_digests={tuple(item[2] for item in results)}")
    print(f"shard_digests={tuple(item[3] for item in results)}")


if __name__ == "__main__":
    main()
