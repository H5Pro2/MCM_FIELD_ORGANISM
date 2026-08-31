# S2-IP Precheck

- Qualification ID: `s2ip-joint-qualification-20260901-01`
- Registered invocation: `python -m unittest tests.test_s2ip_joint_qualification -v`
- Invocation limit: exactly one; no retry
- Active tests: `34` (`14` signal + `20` shell/lifecycle)
- Active test IDs: unique
- Per-test output roles: `34`, unique
- Corrected test 21: exactly one, fails `ie-op-003`
- Obsolete inherited test 21: excluded from discovery
- Product changes: none
- Main gate: `False`
- Memory histories and state functions: excluded

## Active Test List

1. `test_01_all_ten_paths_and_role_swaps_match_the_direct_baseline`
2. `test_02_status_boundaries_are_exclusive`
3. `test_03_atomic_owner_read_only_and_no_selection`
4. `test_04_e001_type_or_schema_fails_without_regular_result`
5. `test_05_e002_source_or_digest_mutation_fails_closed`
6. `test_06_e003_owner_binding_mutation_fails_closed`
7. `test_07_e004_probe_mask_mutation_fails_closed`
8. `test_08_e005_area_evidence_mutation_fails_closed`
9. `test_09_e006_read_only_state_mutation_fails_closed`
10. `test_10_e007_resource_mutation_fails_closed`
11. `test_11_e008_owner_reuse_is_terminal_and_has_no_second_output`
12. `test_12_ledger_formulas_cover_every_reachable_count_pair`
13. `test_13_worst_case_owner_and_success_artifacts_respect_limits`
14. `test_14_identifier_overflow_is_rejected_before_an_owner_exists`
15. `test_15_distinct_retrieval_and_signal_probes_bind_without_digest_equality`
16. `test_16_swapped_case_plan_and_probe_relations_fail_closed`
17. `test_17_owner_is_atomic_and_rejects_a_foreign_pairing`
18. `test_18_candidates_remain_bound_to_retrieval_and_status_to_signal_probe`
19. `test_19_registry_gate_and_complete_neutral_recording_are_valid`
20. `test_20_event_and_receipt_manipulations_are_rejected`
21. `test_21_complete_and_not_evaluable_are_exclusive`
22. `test_22_all_76_parent_sets_are_canonical_and_independently_reconstructed`
23. `test_23_zero_and_single_parent_operations_keep_the_legacy_projection`
24. `test_24_duplicate_parent_is_rejected_by_both_materializers`
25. `test_25_missing_parent_is_rejected_by_both_materializers`
26. `test_26_foreign_parent_is_rejected_by_both_materializers`
27. `test_27_later_parent_is_rejected_by_both_materializers`
28. `test_28_op_171_maximum_owner_start_is_exactly_814_bytes`
29. `test_29_all_envelopes_from_171_through_183_respect_the_bound_table`
30. `test_30_each_bootstrap_partial_failure_is_start_rejected`
31. `test_31_full_bootstrap_is_atomic_bounded_and_activates_at_operation_three`
32. `test_32_start_rejected_lifecycle_mutations_are_invalid`
33. `test_33_append_only_reuse_is_rejected_without_changing_complete_run`
34. `test_34_lifecycle_bounds_and_registry_remain_exact`

This is a technical qualification only. It cannot establish a memory-function result.
