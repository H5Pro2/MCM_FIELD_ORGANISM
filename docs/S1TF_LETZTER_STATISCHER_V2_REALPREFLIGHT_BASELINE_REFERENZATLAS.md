# S1-TF: Letzter statischer v2-Realpreflight des Baseline-Referenzatlas

## Status und Grenze

S1-TF prueft den in S1-TE synthetisch abgenommenen korrigierten v2-Pfad
gegen die tatsaechlichen lokalen Quellen und Eingaben. Es wurde kein Test
wiederholt, kein Comparator aufgerufen, keine S1-TG-Laufdatei angelegt und
kein Modellproducer verwendet.

Der Preflight begann auf dem sauberen und synchronen Branch
`codex/forschungsstand-ec98`:

```text
Ausgangscommit = f8082bd3baca626a2c8279a169d95ac534901132
Ahead/behind   = 0/0
```

## Comparator-Quellinventar v2

Das transitive AST-Inventar wurde zweimal neu berechnet. Beide Werte sind
identisch:

```text
source_file_count       = 96
source_inventory_digest = c202cd042cc20ce2efedb55d7dada447c211050538ab5c67a67f4649bd30a620
```

Direkte Wurzeln und Paket-Bootstrap:

```text
mcm_field_organism/__init__.py
  bb9d968aafe91b4c909abcf30e59b0cc0695fb0d815f32e2014972270327c9da
mcm_field_organism/four_node_baseline_reference_single_run.py
  e2532aa42e00815c7ad8972c37a2d42e8c0967bb4a6cd9d6fe888c1773c8e4e1
mcm_field_organism/four_node_baseline_reference_artifact.py
  f98a5a39862a9817bf22f3b6b5c7ffb306bf139b3950603c8affe8fc3db589d1
mcm_field_organism/four_node_baseline_reference_input.py
  8c10678f72d64f25bc10c1d2ef453c669cae807756dfd41aaa75ce9cb7304bb0
mcm_field_organism/four_node_baseline_reference_comparator.py
  10b3c92b35e6199e4c7e4dce2a83f67aa4da6ab67050e174accdaf853232430d
```

Der Runner besitzt exakt eine Comparator-Aufrufstelle und keine
Modellproducer-Aufrufstelle.

## Historische S1-SS-Provenienz

```text
historical_source_file_count       = 93
historical_source_inventory_digest = 196d5589d278903c18b4bac2f272debe24d8a91f57a999a1efbade560d101c61
```

Die historische Matrixprovenienz bleibt von der neuen v2-Comparatorquelle
getrennt und unveraendert pruefbar.

## Eingabebytes und semantische Identitaeten

```text
reports/s1ss_four_node_matrix_once_v1.json
  file_sha256 = 3fdf622a533f0974c93da26591d8d9edccb2fa4bb1fc272f19098015a8e7e066
reports/s1rk_four_node_fresh_manifest.json
  file_sha256 = 19cc753c110b64d1d48cabe46be190a01247995053da442dd4cefcd344ea8bfc
reports/s1sd_four_node_fresh_matrix_registration.json
  file_sha256 = dc5c42d2dab2b9d3f373e5601b3d170c4f081c46df5b3eb4e8f3a242454ab663

source_artifact_digest
  69a3c11613d2d83660a870dfdb288b98b23e7af9934463d7836ccd77340618bb
matrix_result_digest
  1188e83b4ebfb8327e8fed22e85c8a17751f9b2eaf846632091ac01c1499dde5
fresh_manifest_digest
  ae7a7356a3e06776a000b6e9fafef75b717944f1d75da62d4418be98cc439c68
matrix_registration_digest
  edd3414b3dcc082c0ab7bec66f8dd278cedecd76d11e649ca7aff46a9317a4ba
exposure_fixture_digest
  ca66f3a673eaca663a0973f7e956a90f4788e6f51963b71de4952801936bac3e
axis_digest
  124ee8e19a9e3ce35816ff65370f6775131b0be413c7a2816b01605cf3d03cfd
comparator_input_digest
  085c7a2272bb521fe6b1fe07c6e180f4a9f1d20a4265533385d65e5fe59326c0
```

Die passive Rekonstruktion umfasst exakt 14 Profile mit je 40 Checkpoints.

## Nullabilitaetsachse

Der Adapter bestaetigt exakt:

```text
nullable_record_count = 14
nullable_model_count  = 14
plan_role             = C_GAP
checkpoint_role       = POST_COMPETITION
R                     = (None, None, None, None)
weitere nullable Lagen = 0
```

S und H bleiben durch die strikte Profilvalidierung numerisch. Es wurde
keine Kontrast- oder Paararithmetik ausgefuehrt.

## Erhaltene S1-TB-Belege

```text
reports/s1tb_baseline_reference_atlas_once_v1.attempt.json
  sha256 = e746f02cb0cfaa219a59ae2a1d7a8768925a52710ba0316aacd8bddd7eb795e5
reports/s1tb_baseline_reference_atlas_once_v1.lock
  sha256 = 42a66cbd8e32bfba04655617cb56f53220029f155a7b320c57239261b409600e
```

Beide Dateien sind bytegleich zum gestoppten S1-TB-Stand.

## Ausfuehrungsidentitaet und Laufzeit

```text
schema_id       = mcm.s1tc.baseline-reference-atlas-artifact.v2
source_contract = S1-TC
execution_id    = mcm.s1tg.baseline-reference-atlas.once.v2
authorization   = S1-TG_REAL_BASELINE_REFERENCE_ATLAS_ONCE_V2
authorization_sha256
  4b26b9c6cf66b18946dab58fb674889c7fa89fc1909144731378c3884d52b062

python_implementation    = CPython
python_major_minor_micro = 3.14.4
platform_system          = Windows
platform_machine         = AMD64
```

## Pfadpreflight

`reports` ist ein reales Verzeichnis und kein Link. Alle vier neuen Pfade
fehlen:

```text
reports/s1tg_baseline_reference_atlas_once_v2.json
reports/s1tg_baseline_reference_atlas_once_v2.attempt.json
reports/s1tg_baseline_reference_atlas_once_v2.lock
reports/.s1tg_baseline_reference_atlas_once_v2.json.staging
```

## Gebundener Einmalbefehl und Budget

```text
python -B -m mcm_field_organism.four_node_baseline_reference_single_run --authorization S1-TG_REAL_BASELINE_REFERENCE_ATLAS_ONCE_V2
```

```text
3 Eingabedateien
1 passive Adapterrekonstruktion
14 vollstaendige Profile
1 Comparatoraufruf
322 Rohkontraste
91 Profilpaare
0 Modellproducer
0 Feldschritte
0 automatische Wiederholungen
```

## Preflightentscheidung

```text
S1_TF_STATIC_V2_REAL_PREFLIGHT_PASSED
SOURCE_INPUT_NULLABILITY_OLD_BELEGE_NEW_PATH_RUNTIME_COMMAND_AND_BUDGET_BOUND
NO_TEST_NO_COMPARATOR_NO_RUN_FILE_NO_RESULT_DECISION
```

Es liegt kein methodischer Grund fuer eine Richtungsanderung vor. Der
einzige naechste Schritt ist S1-TG als genau ein realer, unveraenderter
passiver v2-Einmallauf mit der oben gebundenen Autorisierung. Bei einem
gestarteten Fehler bleiben neue Versuchsnachweise bestehen; Retry und
Reparatur sind erneut gesperrt.
