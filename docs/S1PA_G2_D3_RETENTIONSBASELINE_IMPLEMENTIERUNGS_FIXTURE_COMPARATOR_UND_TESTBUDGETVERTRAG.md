# S1-PA G2/D3 Retentionsbaseline: Implementierungs-, Fixture-, Comparator- und Testbudgetvertrag

## Status

S1-PA bindet ausschliesslich Dateigrenzen, erlaubte Abhaengigkeiten,
kanonische Baselinefixtures, externe Fehlermutationen, Comparatorrollen,
defensive Gates und ein endliches Einmaltestbudget fuer die spaetere
Umsetzung von S1-OY/S1-OZ. Der Schritt implementiert nichts und fuehrt keinen
Test aus.

Entscheidung:

```text
G2_D3_RETENTION_BASELINE_COMPARATOR_IMPLEMENTATION_FIXTURES_AND_SINGLE_TEST_BUDGET_BOUND
```

## Gebundene Dateigrenze

S1-PB darf genau vier neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/g2_d3_matched_retention_baseline.py` | reine Konfigurations-/Zustandsvalidierung und Baselineauswertung |
| `mcm_field_organism/g2_d3_checkpoint_baseline_comparison.py` | nachgelagerter passiver Kandidat-Baseline-Comparator |
| `tests/g2_d3_s1pb_retention_baseline_fixtures.py` | kanonische Gueltig- und Fehlerfixtures |
| `tests/test_g2_d3_s1pb_retention_baseline_closure.py` | fokussierte technische Abnahme |

Bestehende Produktions-, Fixture-, Test- und Paketdateien bleiben
unveraendert. Insbesondere werden `mcm_field_organism/__init__.py`, der
S1-OW-Kandidatenoperator und alle Feld-, Runtime-, Transfer-, Runner- und
Medienmodule nicht bearbeitet.

Nach dem einmaligen Test duerfen nur `AKTUELLER_FORSCHUNGSWEG.md`,
`README.md` und `docs/AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md` um das
tatsaechliche Ergebnis ergaenzt werden.

## Eingefrorene Regressionsgrundlage

Vor S1-PB gelten exakt:

```text
mcm_field_organism/g2_d3_two_step_composition.py
= b364ae91ff91d45db32edc2081a9782869c46a82495e3cedcf8ffc21d555991f

mcm_field_organism/g2_d3_two_step_o3_checkpoints.py
= effc8812845273bacc52eef23a0ba20feefc743b3b630c44f04488e860a10011

tests/g2_d3_s1os_fixtures.py
= 58cd3e4505657fc6b964cb0dbc370d22e94261e626e67f652d43670e22f79a41

tests/test_g2_d3_s1os_two_step_composition.py
= f96527e4d7611a47c5e5cf1c083ed9d3db59ead3564ea6e2e0a81c379b4cbae6

tests/g2_d3_s1ow_o3_checkpoint_fixtures.py
= 673460adb87719668908ab8f2e58fb7fcafc8a5f8d3c47e4a450ae56233b4358

tests/test_g2_d3_s1ow_o3_checkpoints.py
= 96ca1e0f7c0a7e0f32a0e13ea5eb98418f8d0ee94c625b6e2a1f275823b2305a
```

Alle sechs Dateien muessen nach S1-PB byteidentisch dieselben Digests
tragen. Die 14 S1-OS- und 16 S1-OW-Tests werden unveraendert im gemeinsamen
Einmallauf erneut ausgefuehrt.

## Import- und Informationsgrenze

### Baselineoperator

`g2_d3_matched_retention_baseline.py` darf nur importieren:

- Python-Standardbibliothek fuer unveraenderliche Datentypen, endliche
  Zahlenpruefung und kanonisches JSON-Lesen;
- den Registrytyp der bestehenden Zweischrittkomposition ausschliesslich
  fuer die aeussere Provenienzpruefung;
- `canonical_json_bytes` und `sha256_hex` aus dem KFS-1-Validator.

Das Modul darf weder `g2_d3_two_step_o3_checkpoints` noch einen anderen
Kandidaten-, D3-, O3-, Projektions-, Commit-, Feld- oder Runtimeoperator
importieren. Sein privater Updatekern erhaelt nur aktuellen
`retained_capacity`, die gebundene Retentionsfraktion und den identischen
Fortsetzungstoken.

Der aeussere Provenienzvalidator darf aus den Chainrecords ausschliesslich
`chain_role`, `first_boundary_input_digest` und
`second_boundary_input_digest` lesen. Initial-, Zwischen-, Final-, Kontakt-
und Anatomyfelder der Kompositionsregistry sind fuer den gesamten
Baselineoperator gesperrt.

### Comparator

`g2_d3_checkpoint_baseline_comparison.py` darf ausschliesslich die
oeffentlichen Resultat-/Receipttypen und Vertragsdigests aus dem bestehenden
S1-OW-Kandidatenmodul und dem neuen Baslinemodul sowie die kanonischen
Digesthelfer importieren.

Der Comparator darf keine Kandidaten- oder Baselineauswertung starten. Er
nimmt nur zwei bereits vollstaendige Resultate entgegen und besitzt keinen
Zugriff auf private Traces oder Zustandsrohbytes.

## Gebundene Baselineoberflaeche

Das Baslinemodul darf genau bereitstellen:

```text
build_g2_d3_matched_retention_baseline_registry()
-> G2D3MatchedRetentionBaselineRegistry

evaluate_g2_d3_matched_retention_baseline(
    first_boundary_input_digest,
    second_boundary_input_digest,
    initial_state_raw_bytes,
    continuation_event_raw_bytes,
    configuration_raw_bytes,
    baseline_registry,
    sequence_registry,
) -> G2D3MatchedRetentionBaselineResult
```

Zulaessig sind ausserdem nur die in S1-OY gebundenen Konstanten und
unveraenderlichen Registry-, Zustands-, Resultat- und Receipttypen. Private
Parser, Validatoren, Zustandsbuilder, Updatekern und Trace fehlen in
`__all__`.

Die beiden Provenienzeingaben muessen exakt 64-stellige kleingeschriebene
SHA-256-Strings sein. Zustand, Ereignis und Konfiguration muessen exakt
`bytes` sein. Beide Registries muessen exakt ihren gebundenen Typen und
Inhalten entsprechen. Falsche API-Typen scheitern vor einem Resultat.

`G2D3MatchedRetentionBaselineResult` enthaelt genau:

```text
checkpoint_values: tuple[float, float, float] | not_computable
receipt: G2D3MatchedRetentionBaselineReceipt
```

Der Baselinebeleg bindet exakt:

```text
receipt_schema_id
receipt_schema_version
baseline_class_id
first_boundary_input_digest
second_boundary_input_digest
chain_role
initial_state_input_bytes_digest
configuration_input_bytes_digest
continuation_event_input_bytes_digest
cp0_state_input_bytes_digest
cp0_state_record_digest
cp0_value
cp1_state_input_bytes_digest
cp1_state_record_digest
cp1_value
cp2_state_input_bytes_digest
cp2_state_record_digest
cp2_value
delta_cp1_cp0
delta_cp2_cp1
delta_cp2_cp0
comparison_digest
baseline_status
validation_status
completed_checks
failure_reasons
accepted_composition_contract_digest
accepted_event_contract_digest
accepted_state_anatomy_contract_digest
accepted_equation_contract_digest
accepted_configuration_identity_digest
baseline_contract_digest
baseline_receipt_digest
```

Bei einem Fehler stehen alle CP-Werte, Komponenten, Zustandsdigests und der
Vergleichsdigest auf `not_computable`. Eingabedigests, Kettenprovenienz,
Completed-Checks und genau ein Fehlercode bleiben passiv sichtbar.

## Gebundene Comparatoroberflaeche

```text
build_g2_d3_checkpoint_baseline_comparison_registry()
-> G2D3CheckpointBaselineComparisonRegistry

compare_g2_d3_candidate_and_retention_baseline(
    candidate_result,
    baseline_result,
    comparison_registry,
) -> G2D3CheckpointBaselineComparisonResult
```

Der Comparator bindet:

```text
comparison receipt schema
= g2_d3_checkpoint_baseline_comparison_receipt/s1pa.v1

closure statuses
= BASELINE_CLOSED_CURRENT_CHECKPOINT_VECTOR | not_computable

comparison contract digest
= 7b3818ca3e9ce2b2b1502399e52d69ca25a02247cca43f06b883633a61d28f0d

closure contract digest
= ac13a848fab0e766b4c02568d4c20aa93915cf0f34dce68ac682969f1fcb376c
```

Ergebnisfelder:

```text
closure_status
residual_checkpoint_values: tuple[float, float, float] | not_computable
residual_directed_components: tuple[float, float, float] | not_computable
receipt
```

Der passive Vergleichsbeleg enthaelt nur Kandidaten-/Baselinebelegdigests,
Kettenprovenienz, beide vollstaendigen Wert-/Komponentenvektoren,
Nullresiduen, Closure-Payloaddigest, Status, Completed-Checks,
Einzelfehlercode, Vertragsdigests und seinen Eigendigest. Rohbytes,
verschachtelte Belege und private Traces sind verboten.

Exakte Vergleichsbelegfelder:

```text
receipt_schema_id
receipt_schema_version
candidate_chain_role
baseline_chain_role
candidate_checkpoint_receipt_digest
baseline_receipt_digest
candidate_checkpoint_values
baseline_checkpoint_values
candidate_directed_components
baseline_directed_components
candidate_comparison_digest
baseline_comparison_digest
residual_checkpoint_values
residual_directed_components
closure_payload_digest
closure_status
validation_status
completed_checks
failure_reasons
accepted_candidate_checkpoint_contract_digest
accepted_baseline_contract_digest
comparison_contract_digest
closure_contract_digest
comparison_receipt_digest
```

Comparatorphasen:

```text
api_intake
candidate_validation
baseline_validation
chain_provenance_gate
checkpoint_identity_gate
residual_evaluation
persistence_guard
comparison_receipt
```

Comparatorcodes:

```text
PA_CANDIDATE_RESULT_INVALID
PA_BASELINE_RESULT_INVALID
PA_CHAIN_PROVENANCE_MISMATCH
PA_CHECKPOINT_IDENTITY_MISMATCH
PA_RESIDUAL_IDENTITY_MISMATCH
```

Der erste Fehler beendet alle nachgelagerten Phasen. Pro ungueltigem
Vergleich ist genau ein Code erlaubt.

## Kanonische gueltige Fixtures

Die Fixturedatei bindet bytegenau:

```text
configuration input digest
= 12e6d381c0dcc0f170c39453bde291152bc55499e0292edacb2d0a09c27e1d93

initial CP0 state input digest
= f67406ef5f4da6ecd3775ab8c12139dbee607dd33b0c89e14842774c48d0ffd2

fresh continuation event input digest
= dbffc12bef77155c2271d3990ebe1b8ae4d481ce6155bf8716b1f6e19128b30f
```

Zwei Gueltigfixtures verwenden dieselben drei Byteobjekte:

| Fixture | erster Provenienzdigest | zweiter Provenienzdigest | Rolle |
|---|---|---|---|
| `PA_V_XXX` | `c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c` | `6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a` | `OP_CHAIN_XXX` |
| `PA_V_YYY` | `2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b` | `dc772636ed23e9cf9a904fd9943a7a1bcfacafe08aed9e60a65ac93f3d266d32` | `OP_CHAIN_YYY` |

Beide muessen exakt die drei in S1-OZ gebundenen State-Record- und
State-Inputdigests, Werte, Komponenten und denselben
`5c8d3b60...e8a86a5`-Vergleichsdigest liefern. Nur ihre vollstaendigen
Baselinebelegdigests unterscheiden sich.

## Externe Baselinefehlermutationen

### Unbekannte Provenienzkette

`PA_I_PROVENANCE_CROSS` kombiniert den ersten XXX- mit dem zweiten
YYY-Digest. Alle Byteinputs bleiben gueltig.

```text
expected = OY_SEQUENCE_PROVENANCE_INVALID
state updates = 0
```

### Gueltig versiegelte falsche Konfiguration

`PA_I_CONFIG_RETENTION_025` aendert nur die Retentionsfraktion auf `0.25`
und berechnet den Konfigurationsrecorddigest korrekt neu.

```text
configuration record digest
= 0462044471e26a7fe6975e7c8a0be49cef6ae80c0f2bb3f18785cb8949a7e7d5
configuration input digest
= a72ed7075acd3bc2937bbf12dd5ca209e7d9df6ecc126dc5df6763228b5e6543
expected = OY_CONFIGURATION_INVALID
state updates = 0
```

Der Operator darf den Wert nicht auf `0.5` korrigieren.

### Gueltig versiegelter negativer Startzustand

```text
fixture = PA_I_STATE_NEGATIVE
state record digest
= 294ed5b040da553b7aa045c0f7ca8b96f2d8249edc9fa9e231f9a3ef9275cd46
state input digest
= 3181d6b69b8b3f572f300c75c330603dd619d7e3ad33f9b1ba4935f658283c61
expected = OY_INITIAL_STATE_INVALID
state updates = 0
```

### Boolwert als Startzustand

```text
fixture = PA_I_STATE_BOOL
state record digest
= a3026e15bd60eef5b4cab645daf79d647be6543141933796e59262394feed8ba
state input digest
= 327d58f0ba6cd60e8d54a27b15fd51010a886efe2001a9eb6d8c7df2d0feb334
expected = OY_INITIAL_STATE_INVALID
state updates = 0
```

### Falsche Ereignisversion

`PA_I_EVENT_VERSION` aendert nur `event_schema_version` auf `changed`.

```text
event input digest
= ad08cd7ae7f8575dda4142147aa6239ecd10a4f4415f5eb4a68dda0eed37ed35
expected = OY_EVENT1_INVALID
state updates = 0
```

Jeder Fehler liefert den vollstaendig unterdrueckten Wert-/Komponentenvektor
und genau einen Code.

## Defensive Baselinecodes

Mit exakten Abhaengigkeiten sind folgende Codes nicht durch weitere externe
Fixtures erreichbar:

```text
OY_CP0_READOUT_FAILED
OY_UPDATE1_FAILED
OY_CP1_READOUT_FAILED
OY_EVENT2_INVALID
OY_UPDATE2_FAILED
OY_CP2_READOUT_FAILED
OY_COMPONENT_EVALUATION_FAILED
```

Sie bleiben als direkte Fail-Closed-Gates registriert. Monkeypatching,
gefaelschte interne Zustandsobjekte, Dependency-Ersatz und Produktionshooks
nur zur Codeerzeugung sind verboten. Die Abnahme prueft diese Gates statisch.

## Comparatorfaelle

### Gueltige Schliessung

Fuer XXX und YYY werden jeweils unabhaengig ein gueltiges S1-OW-Kandidaten-
und ein gueltiges Baselineresultat erzeugt und danach genau einmal
verglichen. Erwartet werden Nullresiduen, Closure-Payloaddigest
`bce12955...d5f2af15` und
`BASELINE_CLOSED_CURRENT_CHECKPOINT_VECTOR`.

### Reale ungueltige Eingaben

- Ein echtes S1-OW-Resultat aus `OR_I_FORMATION_DISABLED` liefert
  `PA_CANDIDATE_RESULT_INVALID`.
- Ein echtes Baselineresultat aus `PA_I_PROVENANCE_CROSS` liefert
  `PA_BASELINE_RESULT_INVALID`.
- Ein gueltiger XXX-Kandidat gegen eine gueltige YYY-Baseline liefert
  `PA_CHAIN_PROVENANCE_MISMATCH`.

In allen drei Faellen bleiben Closurestatus und Residuen `not_computable`.

Defensiv registriert bleiben:

```text
PA_CHECKPOINT_IDENTITY_MISMATCH
PA_RESIDUAL_IDENTITY_MISMATCH
```

Sie erhalten keine Fake-Fixtures.

## Fokussierte Testmatrix

Das neue Testmodul enthaelt genau 18 Tests:

| Test-ID | Abnahme |
|---|---|
| `T01` | alle sechs eingefrorenen Regressionsdateien und alle Fixturedigests stimmen |
| `T02` | Baseline- und Comparatorregistries binden Schemata, Phasen, Codes und Vertragsdigests exakt |
| `T03` | XXX liefert exakt CP0/CP1/CP2, Zustandsdigests, Werte und Komponenten |
| `T04` | YYY liefert bitidentische Zustandsfolge und Sachwerte, aber getrennte Provenienz |
| `T05` | der private Updatekern ist stationaer, tokenidentisch und wird exakt zweimal angewendet |
| `T06` | Baselinebeleg und Eigendigest sind passiv geschlossen und enthalten keine Rohbytes |
| `T07` | gekreuzte Provenienz stoppt vor Zustandsvalidierung und Update |
| `T08` | die gueltig versiegelte `0.25`-Konfiguration wird nicht repariert |
| `T09` | negativer und boolescher Startzustand scheitern vor CP0 und Update |
| `T10` | falsche Ereignisversion stoppt vor Update 1 und publiziert keinen CP0-Teilwert |
| `T11` | alle externen Fehler besitzen genau einen Code und vollstaendige Wertunterdrueckung |
| `T12` | gleiche Inputs liefern bitgleiche Resultate; Inputs und Registries bleiben unveraendert |
| `T13` | falsche API-Typen, fremde Registries und Kandidatenbelege als Baselineeingang scheitern vor Resultat |
| `T14` | alle elf OY-Codes sind registriert; sieben defensive Gates besitzen keine Fake-Fixtures |
| `T15` | XXX-Kandidat und XXX-Baseline liefern exakt die gebundene atomare Schliessung |
| `T16` | YYY-Kandidat und YYY-Baseline liefern dieselbe Schliessung mit getrennter Provenienz |
| `T17` | ungueltiger Kandidat, ungueltige Baseline und gekreuzte gueltige Ketten scheitern im Comparator einzeln und ohne Residuum |
| `T18` | Import-, `__all__`-, AST-, I/O-, Persistenz-, Feld-, Runtime-, Runner-, Medien- und Netzwerkgrenzen sind geschlossen |

Die Tests verwenden nur `unittest` und Python-Standardbibliothek. Fixtures,
Digests, Erwartungen und Testzahl werden nach einem Ergebnis nicht
angepasst.

## Endliches S1-PB-Ausfuehrungsbudget

S1-PB darf genau einmal ausfuehren:

```text
python -m unittest \
  tests.test_g2_d3_s1os_two_step_composition \
  tests.test_g2_d3_s1ow_o3_checkpoints \
  tests.test_g2_d3_s1pb_retention_baseline_closure
```

Die Abnahme muss exakt 48 Tests entdecken: 14 unveraenderte S1-OS-Tests, 16
unveraenderte S1-OW-Tests und 18 neue S1-PB-Tests.

Innerhalb dieses einen Laufs gelten maximal:

```text
compose_g2_d3_two_step_continuation:                 35 Aufrufe
evaluate_g2_d3_two_step_o3_checkpoints:              40 Aufrufe
evaluate_g2_d3_matched_retention_baseline:           40 Aufrufe
compare_g2_d3_candidate_and_retention_baseline:      12 Aufrufe
_execute_g2_d3_two_step:                            100 Aufrufe
evaluate_g2_d3_local_admissible_engagement:         160 Aufrufe
private retention state updates:                     60 Aufrufe
MCM-Feldschritte:                                      0
Runtime-/Speicherpublikationen:                        0
Transfer-/Runner-/Medien-/Netzwerkaufrufe:             0
Dateischreibzugriffe der Operatoren:                    0
read-only Quelltextzugriffe:                   maximal 12
```

Bei einem Fehler wird der kombinierte Test nicht erneut ausgefuehrt. Die
Implementierung wird gegen den unveraenderten Vertrag korrigiert, ohne
Fixtures, Parameter, Digests, Erwartungen, Testzahl oder Budgets
umzudeuten.

## Aussagegrenze

S1-PA bindet nur die spaetere technische Implementierung und einmalige
Abnahme der engen Retentionsbaseline. Es gibt noch keinen Baselineoperator,
Comparator, Testlauf oder Schliessungsbefund.

Der Schritt belegt keine eigene Substratfunktion und keine hypothetische
MCM-Memory-Funktion.

## Naechster erlaubter Schritt

S1-PB darf ausschliesslich die vier gebundenen Dateien implementieren, den
kombinierten 48-Test-Lauf genau einmal innerhalb des Budgets ausfuehren und
danach nur das tatsaechliche Ergebnis in den drei Statusdokumenten
festhalten.

Feld-, Runtime-, Transfer-, Runner- und Medienpfade sowie jede weitergehende
Funktionsentscheidung bleiben gesperrt.
