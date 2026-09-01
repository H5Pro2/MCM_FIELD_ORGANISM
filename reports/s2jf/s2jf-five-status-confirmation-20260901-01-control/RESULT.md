# S2-JF Five-Status Confirmation

Run ID: `s2jf-five-status-confirmation-20260901-01`

Technical status: `RECORDING_COMPLETE`

Functional status:
`S2JF_READ_ONLY_TWO_AREA_CONTEXT_STATUS_CONFIRMED_DIRECT_COMPARISON_EXPLAINS`

- `run_main_once` was called exactly once; no retry or continuation occurred.
- The run recorded all `183` operations and `366` events.
- The independent read-only verifier was called exactly once and returned no
  errors.
- Source hashes were unchanged and the main gate returned to `False`.
- All eight expected statuses matched the recorded statuses.
- Signal and independent direct baseline agreed in all eight cases.
- All status probes preserved the Memory states.

Recorded cases:

1. `c01`: `CONSISTENT`
2. `c02`: `CONFLICT`
3. `c03`: `CONFLICT`
4. `c04`: `SINGLE_SOURCE`
5. `c05`: `SINGLE_SOURCE`
6. `c06`: `NO_CONTEXT`
7. `c07`: `NO_APPLICABLE_CONTEXT`
8. `c08`: `NO_APPLICABLE_CONTEXT`

The result confirms a qualified private read-only description of real A/B
context states with receptor-faithful aggregate equality. The direct comparison
fully explains the signal function. No automatic context selection, ranking,
merging, field effect, or MCM-specific mechanism is established.

The historical S2-IV falsification and the earlier S2-JD `NOT_EVALUABLE` run
remain unchanged. This five-status verification branch is closed after S2-JF.

