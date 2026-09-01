# S2-JD Five-Status Confirmation

Run ID: `s2jd-five-status-confirmation-20260901-01`

Technical result: `NOT_EVALUABLE`

- `run_main_once` was called exactly once.
- The run recorded all `183` operations and `366` events.
- The independent read-only verifier was called exactly once.
- The main gate was `False` after the call.
- Bound source hashes were unchanged before and after the run.
- No retry, continuation, parameter change, or post-run functional evaluation occurred.

The verifier rejected the compact arm source relation for all eight signal and
eight direct-baseline operations (`ie-op-118/119` through `ie-op-167/168`). The
runner prospectively recorded the qualified aggregate visibility binding digest
in each START input, while the verifier still required the previous exact START
input shape. This is an execution-evidence projection mismatch. It is not a
negative finding about the five context statuses or the Memory architecture.

Because verification did not return `RECORDING_COMPLETE`, the stored functional
findings are not interpreted. The historical S2-IV falsification remains
unchanged.

