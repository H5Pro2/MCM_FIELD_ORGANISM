# S2-IQ Functional Run Result

Status: `NOT_EVALUABLE`

- Run ID: `s2iq-five-status-20260901-01`
- `run_main_once` calls: `1`
- Retry or continuation: `0`
- Read-only verifier calls: `1`
- Control exit code: `0`
- Recorded operations/events: `117/238`
- Recorded bytes: `295158`
- Verifier errors: none
- Failure operation: `ie-op-117`
- Failure class: `DUAL_PROBE_AND_ARM_INPUTS_BIND`
- Recorded failure code: `IG-E009`
- Terminal state: `NOT_EVALUABLE`
- Gate after run: `False`
- Source hashes before/after: identical
- Control output SHA-256: `c1d438ac8c2a454320021e96af7a673fe5bc9372574aa845ae16c2c9c99327eb`
- Run inventory: `119` files
- Run inventory SHA-256: `8b3be947c62925a3608ceadb03c523a71970c76caf1a609b99f20a730936a60b`

## Static Cause Localization

The run completed all six history initializations, all 38 formations and the
six read-only A/B projections. It stopped while preparing the first functional
case, before `ie-op-117` could publish an artifact.

The first reached signal input uses invocation ID `s2ig.c01.signal`. The current
S2-IC contract requires `^[a-z][a-z0-9-]{7,95}$`; dots are invalid. Construction
therefore fails before signal or baseline invocation. Later dotted owner IDs in
the same runner block would require the same adapter review, but were not
reached and are not reported as executed failures.

This is a runner identifier-adapter defect, not a memory or five-status function
finding. No case status was evaluated, no functional interpretation is allowed,
and this run must not be repaired, continued or reclassified.
