# S1-TA: Letzter statischer Realpreflight des Baseline-Referenzatlas-Einmallaufs

## Status und Grenze

S1-TA prueft den in S1-SZ synthetisch abgenommenen passiven
Produktionspfad gegen die tatsaechlich vorhandenen lokalen Quellen und
Eingaben. Es wurde kein Test wiederholt, kein Comparator aufgerufen, keine
Laufdatei angelegt und kein Modellproducer verwendet.

Der Preflight begann auf dem sauberen und mit dem Remote synchronen Branch
`codex/forschungsstand-ec98`:

```text
Ausgangscommit = 1317b03d21426def4bb6c297a5823ee7aa9600a1
Ahead/behind   = 0/0
```

## Aktuelles Comparator-Quellinventar

Das transitive AST-Inventar wurde im selben Preflight zweimal neu
berechnet. Beide Werte sind identisch:

```text
source_file_count       = 96
source_inventory_digest = e1e4765a6d6322d5d480f60515385b552e088e2b2ab30869f88a5efcdf2b361d
```

Direkte Wurzeln und Paket-Bootstrap:

```text
mcm_field_organism/__init__.py
  bb9d968aafe91b4c909abcf30e59b0cc0695fb0d815f32e2014972270327c9da
mcm_field_organism/four_node_baseline_reference_single_run.py
  01b50106c1bf07bb179229f727e255fbdc85d5887a281257c4835e7bd944228a
mcm_field_organism/four_node_baseline_reference_artifact.py
  41ded589b8547f024953ec233e4ce71a0e2cc376188b69dadbf9762285c26933
mcm_field_organism/four_node_baseline_reference_input.py
  b04d58f71d2e595f1b745dd3523f88db214d693cd48c9cc7d8a43555a8914629
mcm_field_organism/four_node_baseline_reference_comparator.py
  1e77bac366eedaad168d5496bd1324dff320ae40ed5530baa293101f5e5a9f03
```

Der Runner besitzt exakt eine lexikalische Aufrufstelle fuer
`compare_four_node_baseline_reference` und keine Modellproducer-
Aufrufstelle.

## Historische S1-SS-Provenienz

Das im realen S1-SS-Artefakt gebundene historische Produktionsinventar
wurde aus den aktuellen unveraenderten Quellen erneut rekonstruiert:

```text
historical_source_file_count       = 93
historical_source_inventory_digest = 196d5589d278903c18b4bac2f272debe24d8a91f57a999a1efbade560d101c61
```

Damit bleibt die historische Matrixquelle von der neuen
Comparatorquellprovenienz getrennt und jeweils vollstaendig pruefbar.

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

Manifest und Registrierung wurden gemeinsam validiert, das Fixture wurde
kanonisch rekonstruiert und erneut validiert. Die passive Eingabe umfasst
exakt 14 Profile mit jeweils 40 Checkpoints. Es wurde dabei noch kein
Kontrast und kein Paar berechnet.

## Ausfuehrungsidentitaet und Laufzeit

```text
schema_id       = mcm.s1sx.baseline-reference-atlas-artifact.v1
source_contract = S1-SX
execution_id    = mcm.s1tb.baseline-reference-atlas.once.v1
authorization   = S1-TB_REAL_BASELINE_REFERENCE_ATLAS_ONCE
authorization_sha256
  97605b3350c2e368b63820ab37b3d4c9f6aed9c84b44431c605f7ebfddb8d0cd

python_implementation    = CPython
python_major_minor_micro = 3.14.4
platform_system          = Windows
platform_machine         = AMD64
```

## Pfadpreflight

`reports` ist ein reales Verzeichnis und kein Link. Alle vier festen
Laufpfade fehlen:

```text
reports/s1tb_baseline_reference_atlas_once_v1.json
reports/s1tb_baseline_reference_atlas_once_v1.attempt.json
reports/s1tb_baseline_reference_atlas_once_v1.lock
reports/.s1tb_baseline_reference_atlas_once_v1.json.staging
```

## Gebundener Einmalbefehl und Budget

Nur dieser spaetere Prozessweg ist zulaessig:

```text
python -B -m mcm_field_organism.four_node_baseline_reference_single_run --authorization S1-TB_REAL_BASELINE_REFERENCE_ATLAS_ONCE
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
S1_TA_STATIC_REAL_PREFLIGHT_PASSED
SOURCE_INPUT_PROVENANCE_PATH_RUNTIME_COMMAND_AND_BUDGET_BOUND
NO_TEST_NO_COMPARATOR_NO_RUN_FILE_NO_RESULT_DECISION
```

Es liegt kein methodischer Grund fuer eine Richtungsanderung vor. Der
einzige naechste Schritt ist S1-TB als genau ein realer, unveraenderter
passiver Einmallauf mit der oben gebundenen Autorisierung. S1-TB darf
keinen Modellproducer aufrufen und keine funktionale Interpretation
vornehmen. Bei gestartetem Fehler bleiben Versuchsnachweis und Sperre
bestehen; es gibt keine Reparatur oder Wiederholung ohne neue fachliche
Entscheidung.
