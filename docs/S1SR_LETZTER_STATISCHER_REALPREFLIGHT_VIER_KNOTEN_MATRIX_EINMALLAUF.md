# S1-SR: Letzter statischer Realpreflight des Vier-Knoten-Matrix-Einmallaufs

## Status und Grenze

S1-SR prueft den in S1-SQ synthetisch abgenommenen Produktionspfad gegen
die tatsaechlich vorhandenen lokalen Quellen und Eingaben. Es wurde kein
Test wiederholt, keine Laufdatei angelegt, kein Producer aufgerufen und
keine reale Matrix gestartet.

Der Preflight wurde auf dem sauberen und mit dem Remote synchronen Branch
`codex/forschungsstand-ec98` durchgefuehrt. Gebundene Ausgangscommits:

```text
Implementierung: 193b3620d6fc0e36c8e3e23885db1417f4567c8b
Abnahme:         ddd022d1a7eafbe7700b322ea592029e672f6a83
Ahead/behind:    0/0
```

## Produktionsquellen

Das AST-Inventar wurde im selben Preflight zweimal vollstaendig neu
berechnet. Beide Werte sind identisch:

```text
source_file_count        = 93
source_inventory_digest  = 196d5589d278903c18b4bac2f272debe24d8a91f57a999a1efbade560d101c61
```

Die direkten Ausfuehrungsrollen und der Paket-Bootstrap besitzen diese
Byte-Digests:

```text
mcm_field_organism/__init__.py
  bb9d968aafe91b4c909abcf30e59b0cc0695fb0d815f32e2014972270327c9da
mcm_field_organism/four_node_matrix_single_run.py
  9a0dd6c0d041752bddac6ce186bd57530f86e9ca737de3cf4016cd983d8270d8
mcm_field_organism/four_node_matrix_artifact.py
  b8ca95abf3723317c0d6f68f26e0df174d26f8f2a02ee6af20d371864842fb43
mcm_field_organism/four_node_matrix_lifecycle.py
  3f8da7351eae470b34990f22bb8707c913372e7948a575a06227537f6dae8268
```

Der Aggregatdigest bindet die sortierte Pfad-/Byte-Digestliste aller 93
transitiv erreichbaren lokalen Produktionsdateien. Unaufloesbare oder
dynamische lokale Importkanten wurden nicht gefunden. Der Runner besitzt
genau eine lexikalische Aufrufstelle fuer `execute_four_node_matrix`.

## Eingabedateien und semantische Identitaeten

```text
reports/s1rk_four_node_fresh_manifest.json
  file_sha256 = 19cc753c110b64d1d48cabe46be190a01247995053da442dd4cefcd344ea8bfc

reports/s1sd_four_node_fresh_matrix_registration.json
  file_sha256 = dc5c42d2dab2b9d3f373e5601b3d170c4f081c46df5b3eb4e8f3a242454ab663

fresh_manifest_digest
  ae7a7356a3e06776a000b6e9fafef75b717944f1d75da62d4418be98cc439c68
matrix_registration_digest
  edd3414b3dcc082c0ab7bec66f8dd278cedecd76d11e649ca7aff46a9317a4ba
exposure_fixture_digest
  ca66f3a673eaca663a0973f7e956a90f4788e6f51963b71de4952801936bac3e
axis_digest
  124ee8e19a9e3ce35816ff65370f6775131b0be413c7a2816b01605cf3d03cfd
```

Manifest und Registrierung wurden streng geparst und gemeinsam validiert.
Das Fixture wurde daraus neu aufgebaut und gegen die Registrierung
validiert. Die feste Achse umfasst 17 Plaene und 14 Modellrollen.

## Ausfuehrungsidentitaet

```text
schema_id       = mcm.s1so.four-node-matrix-artifact.v1
source_contract = S1-SO
execution_id    = mcm.s1ss.four-node-matrix.once.v1
canonicalizer   = compact-json-ascii-sort-keys-no-nan-sha256-v1
authorization   = S1-SS_REAL_FOUR_NODE_MATRIX_ONCE
authorization_sha256
  2a25f08d83f30cb239ffb05fa166bdee01736e5cd883fcb0404a87a289017798
```

Gebundene Laufzeitidentitaet des Preflights:

```text
python_implementation       = CPython
python_major_minor_micro    = 3.14.4
platform_system             = Windows
platform_machine            = AMD64
```

## Pfadpreflight

`reports` ist ein reales Verzeichnis und kein Symlink. Alle vier festen
Laufpfade fehlen:

```text
reports/s1ss_four_node_matrix_once_v1.json
reports/s1ss_four_node_matrix_once_v1.attempt.json
reports/s1ss_four_node_matrix_once_v1.lock
reports/.s1ss_four_node_matrix_once_v1.json.staging
```

Die in S1-SQ abgenommene Hardlinkpublikation lief in temporaeren
Testverzeichnissen auf demselben lokalen Laufwerk. Im Projektverzeichnis
wurde fuer S1-SR keine Probe- oder Stagingdatei erzeugt.

## Gebundener Einmalbefehl und Budget

Nur dieser spaetere Prozessweg ist zulaessig:

```text
python -B -m mcm_field_organism.four_node_matrix_single_run --authorization S1-SS_REAL_FOUR_NODE_MATRIX_ONCE
```

Der Runner akzeptiert keine Rollen-, Plan-, Refinement-, Pfad-, Retry-,
Parallel- oder Comparatoroption. Sein einziges reales Gesamtbudget ist:

```text
238 Matrixzellen
1778 Modellintervalle
238 zeitlose Alignoperationen
560 passive Checkpoints
1 Matrixproducer-Aufruf
0 Comparatoraufrufe
0 automatische Wiederholungen
```

## Preflightentscheidung

```text
S1_SR_STATIC_REAL_PREFLIGHT_PASSED
SOURCE_INPUT_FIXTURE_AXIS_PATH_AND_COMMAND_IDENTITIES_BOUND
NO_TEST_NO_PRODUCER_NO_REAL_MATRIX_NO_RESULT_DECISION
```

Es liegt kein methodischer Grund fuer eine Richtungsanderung vor. Der
einzige naechste Schritt ist S1-SS als genau ein realer, unveraenderter
Einmallauf mit der oben gebundenen Autorisierung. S1-SS darf keine
Comparatorauswertung oder funktionale Interpretation enthalten. Bei einem
gestarteten Fehler bleiben Sperre und Versuchsnachweis bestehen; es gibt
keine Reparatur, Wiederholung oder Fortsetzung ohne neue fachliche
Entscheidung.
