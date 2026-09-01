# S2-IV Functional Run Result

Run ID: `s2iv-five-status-20260901-01`

Technical status: `RECORDING_COMPLETE`

Functional status: `S2IE_REAL_TWO_AREA_STATUS_FUNCTION_FALSIFIED`

- Exactly one `run_main_once` call; no retry or continuation.
- Exactly one independent read-only verification.
- Complete recording: `183/183` operations and `366/366` events.
- Verification errors: none.
- Gate after the run: `False`.
- Source hashes before and after: identical.
- S2-IQ remains unchanged as `NOT_EVALUABLE`.

## Functional findings

Six of eight cases matched the preregistered status:

| Case | Expected | Observed | Result |
|---|---|---|---|
| `c01` | `CONSISTENT` | `SINGLE_SOURCE` | falsified |
| `c02` | `CONFLICT` | `CONFLICT` | confirmed |
| `c03` | `CONFLICT` | `CONFLICT` | confirmed |
| `c04` | `SINGLE_SOURCE` | `SINGLE_SOURCE` | confirmed |
| `c05` | `SINGLE_SOURCE` | `NO_APPLICABLE_CONTEXT` | falsified |
| `c06` | `NO_CONTEXT` | `NO_CONTEXT` | confirmed |
| `c07` | `NO_APPLICABLE_CONTEXT` | `NO_APPLICABLE_CONTEXT` | confirmed |
| `c08` | `NO_APPLICABLE_CONTEXT` | `NO_APPLICABLE_CONTEXT` | confirmed |

For `c01`, both `A_RECENT` and `B_STABLE` were present, but only `A_RECENT`
was applicable. For `c05`, only `B_STABLE` was present and it was not
applicable to the signal probe.

Signal and independent direct baseline agreed in all eight cases. Every case
receipt reported identical pre/post state digests and read-only use. The run
therefore provides a valid functional falsification of the complete five-status
forecast for these bound histories, not an infrastructure failure and not a
general failure of the Memory architecture.
