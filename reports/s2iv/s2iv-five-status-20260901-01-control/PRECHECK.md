# S2-IV Precheck

- Run ID: `s2iv-five-status-20260901-01`
- Owner ID: `s2iv-run-owner-20260901-01`
- Result root: `reports/s2iv/runs`
- Result directory existed before run: `False`
- `run_main_once` calls allowed: `1`
- Retry, continuation or parameter change: forbidden
- Histories: `6`
- Formations: `38`
- Function cases: `8`
- Operations/events: `183/366`
- Retrieval and masked signal probes: separate typed roots
- Signal and direct baseline: eight separate call pairs
- Compact receipts and `ParentSetV1`: S2-IU qualified
- Evaluation plan: independent verifier source, sealed before the run
- Main gate before run: `False`

Expected statuses:

1. `c01 CONSISTENT`
2. `c02 CONFLICT`
3. `c03 CONFLICT`
4. `c04 SINGLE_SOURCE`
5. `c05 SINGLE_SOURCE`
6. `c06 NO_CONTEXT`
7. `c07 NO_APPLICABLE_CONTEXT`
8. `c08 NO_APPLICABLE_CONTEXT`

Functional interpretation is permitted only after the one independent read-only
verification returns `RECORDING_COMPLETE`. The run cannot establish automatic
selection, ranking, merging, context application or MCM-specific physics.
