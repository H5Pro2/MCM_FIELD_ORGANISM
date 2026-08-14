"""Private W7-BN shard materialization followed by W7-BO evaluation."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

from mcm_field_organism.w7bc_const_v_r124_trajectory_contract import build_w7bc_const_v_r124_trajectory_contract
from mcm_field_organism.w7bd_const_v_runtime_adapter import build_w7bd_const_v_runtime_adapter
from mcm_field_organism.w7bj_const_v_r4_convergence_contract import build_w7bj_const_v_r4_convergence_contract
from mcm_field_organism.w7bl_const_v_seven_path_gate import build_w7bl_const_v_seven_path_gate
from mcm_field_organism.w7bn_const_v_shard_executor import execute_w7bn_const_v_role_shard
from mcm_field_organism.w7bo_const_v_convergence_evaluator import evaluate_w7bo_const_v_convergence
from mcm_field_organism.w7m_capacity_function_matrix import build_w7m_capacity_function_matrix_adapter
from mcm_field_organism.w7w_symmetric_source_family import build_w7w_source_authorization, build_w7w_symmetric_source_family
from mcm_field_organism.w7y_seven_path_source_plan import build_w7y_seven_path_source_plan

PATHS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
REFINEMENTS = (1, 2, 4)


def run_one(item):
    path_id, refinement = item
    matrix = build_w7m_capacity_function_matrix_adapter()
    adapter = build_w7bd_const_v_runtime_adapter(matrix, build_w7bc_const_v_r124_trajectory_contract())
    family = build_w7w_symmetric_source_family(matrix)
    authorization = build_w7w_source_authorization(matrix, family)
    plan = build_w7y_seven_path_source_plan(matrix, family, authorization)
    contract = build_w7bj_const_v_r4_convergence_contract()
    gate = build_w7bl_const_v_seven_path_gate(plan, contract)
    return execute_w7bn_const_v_role_shard(matrix, family, authorization, plan, adapter, contract, gate, path_id, refinement)


def main():
    items = tuple((path_id, refinement) for refinement in REFINEMENTS for path_id in PATHS)
    shards = []
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=4, mp_context=context) as pool:
        futures = tuple(pool.submit(run_one, item) for item in items)
        for future in as_completed(futures):
            shards.append(future.result())
    shards.sort(key=lambda shard: (shard.refinement, shard.path_id))
    roles = tuple(shard.role for shard in shards)
    matrix = build_w7m_capacity_function_matrix_adapter()
    family = build_w7w_symmetric_source_family(matrix)
    authorization = build_w7w_source_authorization(matrix, family)
    plan = build_w7y_seven_path_source_plan(matrix, family, authorization)
    contract = build_w7bj_const_v_r4_convergence_contract()
    gate = build_w7bl_const_v_seven_path_gate(plan, contract)
    result = evaluate_w7bo_const_v_convergence(roles, contract, gate)
    print(f"outcome={result.outcome}")
    print(f"component_count={len(result.components)}")
    print(f"epsilon={result.epsilon}")
    print(f"effect_floor={result.effect_floor}")
    print(f"result_digest={result.result_digest}")


if __name__ == "__main__":
    main()
