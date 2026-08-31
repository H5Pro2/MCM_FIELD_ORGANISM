# S2-IR ID inventory

Qualification ID: `s2ir-identifier-regression-20260901-01`

## Bound form

All generated invocation and owner identifiers use the unchanged validator form
`[a-z][a-z0-9-]{7,95}`. Dots, aliases, fallback parsing, and validator relaxation
are absent.

## Formation identities

The runner derives three typed identities for every actual formation step:

- `s2ig-formation-<history>-<ordinal>-owner`
- `s2ig-formation-<history>-<ordinal>-authorization`
- `s2ig-formation-<history>-<ordinal>-consumption`

The complete source ranges are:

| History | Ordinals | Formations | Generated IDs |
| --- | --- | ---: | ---: |
| `h-c` | `01..04` | 4 | 12 |
| `h-x0` | `01..05` | 5 | 15 |
| `h-x1` | `01..05` | 5 | 15 |
| `h-sa` | `01` | 1 | 3 |
| `h-sb` | `01..13` | 13 | 39 |
| `h-n` | `01..10` | 10 | 30 |
| Total | | 38 | 114 |

The history and ordinal remain separate typed fields in
`_FormationRuntimeIdentifiers`. An ordinal outside the literal history is rejected.

## Function-case identities

For each case `c01..c08`, the runner derives exactly:

- `s2ig-case-<case>-signal-invocation`
- `s2ig-case-<case>-baseline-invocation`
- `s2ig-case-<case>-dual-owner`
- `s2ig-case-<case>-signal-owner`
- `s2ig-case-<case>-baseline-owner`

This yields 40 IDs. The case remains a separate typed field in
`_CaseRuntimeIdentifiers`; unknown cases are rejected.

## Totals

- Generated formation invocation/owner identities: 114
- Generated function-case invocation/owner identities: 40
- Total generated strict identities: 154
- Duplicate identities: 0
- Dot-containing identities: 0
- Registered operation identities: 183 unique and validator-conformant
- Registered START/RESULT events: 366, unchanged

Tests 01 through 05 established these properties before the recording-size failure
in test 06.
