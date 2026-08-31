# S2-IP Qualification Result

Status: `S2IP_JOINT_QUALIFICATION_VALID`

- Qualification ID: `s2ip-joint-qualification-20260901-01`
- Invocation count: `1`
- Command: `python -m unittest tests.test_s2ip_joint_qualification -v`
- Executed test bodies: `34`
- Passed: `34`
- Failures: `0`
- Errors: `0`
- Exit code: `0`
- Terminal output: `OK`
- Output SHA-256: `ed6c2b34a8343f3cf5890681d4f7dc0f4c0e19055f9b382fc87151ca97c227e8`
- Source hashes before/after: identical
- Main gate after execution: `False`

## Confirmed Scope

- All 14 current S2-ID status, symmetry and error checks passed.
- The corrected post-bootstrap failure test addressed `ie-op-003` exactly once.
- The obsolete inherited `ie-op-002` test was absent from active discovery.
- All 76 multi-parent operations and ParentSetV1 fail-closed checks passed.
- Bootstrap partial failures remained `START_REJECTED` without an active run.
- Complete bootstrap publication produced both files and four chained events before `ACTIVE`.
- The first active failure produced `NOT_EVALUABLE` with complete bootstrap evidence.
- Registry `183/366`, limits `11264/22528`, append-only behavior and terminal exclusivity passed.

S2-IO remains historically unchanged and unqualified. S2-IP qualifies only the current signal logic and private run shell. No real history, memory-state function or five-status functional run was executed; that run still requires separate authorization.
