# S2-IR identifier regression finding

Run ID: `s2ir-identifier-regression-20260901-01`

Status: `QUALIFICATION_FAILED_RECORDING_BOUND`

## Result

The single authorized invocation executed eight tests. Seven passed and one ended
with an error. The process exit code is `1`.

Confirmed before the failure:

- all 154 generated invocation and owner IDs match
  `[a-z][a-z0-9-]{7,95}`;
- all generated IDs are unique and contain no dot;
- all 183 registered operation IDs are valid and unique;
- all eight signal and direct-baseline call sites accept the corrected IDs;
- signal and baseline agree for the neutral inputs;
- their bundle inputs remain read-only;
- the main execution gate remains `False`.

## Blocking finding

The neutral recorder regression reached `ie-op-117`
(`DUAL_PROBE_AND_ARM_INPUTS_BIND`) and failed while publishing its artifact:

`IG-E008: registered resource limit exceeded`

The operation retains its existing 2,048-byte receipt limit. No limit, receipt
projection, registry row, validator, or test was changed after this result. The run
was not repeated.

S2-IR is therefore not qualified. The next permissible technical question is the
canonical size and redundancy of the `ie-op-117` receipt after the strict-ID
migration. This is an evidence-envelope issue, not a negative signal or Memory
finding.

## Integrity

- Source hashes before and after the test invocation are identical.
- Full unittest output and exit code are stored beside this report.
- S2-IQ remains permanently `NOT_EVALUABLE` and was not modified or reinterpreted.
- No Memory history, main run, API, snapshot, field path, or bootstrap file was used.
