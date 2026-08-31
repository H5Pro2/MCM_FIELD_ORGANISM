# S2-IQ Precheck

- Run ID: `s2iq-five-status-20260901-01`
- Owner ID: `s2iq-run-owner-20260901-01`
- Result root: `reports/s2iq/runs`
- Result directory existed before run: `False`
- Main calls allowed: `1`
- Retry or continuation: forbidden
- Histories: `6`
- Formations: `38`
- Function cases: `8`
- Operations/events: `183/366`
- Retrieval and masked signal probes: separate typed roots
- Signal and direct baseline: separate calls
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

Functional interpretation is permitted only after one independent read-only
verification returns `RECORDING_COMPLETE`. This run cannot establish automatic
selection, ranking, merging, context application or MCM-specific physics.
