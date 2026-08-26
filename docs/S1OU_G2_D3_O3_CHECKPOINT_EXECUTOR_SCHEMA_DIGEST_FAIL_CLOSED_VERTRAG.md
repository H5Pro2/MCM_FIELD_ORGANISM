# S1-OU G2/D3 O3-Checkpoint-Executor: Schema-, Digest- und Fail-Closed-Vertrag

## Status

S1-OU bindet ausschliesslich den gemeinsamen privaten Executorvertrag, die
unveraenderte bestehende Kompositionsoberflaeche sowie API, Registry,
Vertragsdigests, Phasen, Fehlercodes und passive Belegrollen fuer den
S1-OT-O3-Checkpointpfad. Der Schritt implementiert und fuehrt nichts aus.

Entscheidung:

```text
G2_D3_SHARED_PRIVATE_TWO_STEP_EXECUTOR_AND_O3_CHECKPOINT_SCHEMA_DIGEST_FAIL_CLOSED_BOUND
```

## Bestehende Oberflaeche bleibt unveraendert

Die akzeptierte Funktion behaelt exakt Signatur und Rueckgabetyp:

```text
compose_g2_d3_two_step_continuation(...)
-> G2D3TwoStepCompositionResult
```

Sie muss nach einer spaeteren Refaktorierung fuer alle S1-OS-Fixtures dieselben
Finalbytes, Receiptfelder, Status, Fehlercodes, Completed-Checks und
kanonischen Receiptdigests erzeugen.

Vor Refaktorierung gebundene Quelldigests:

```text
mcm_field_organism/g2_d3_two_step_composition.py
= dc316c48043fd0bd3b4fac3f80971c73b68c065e08c850b3a9126942bfb338ea

tests/test_g2_d3_s1os_two_step_composition.py
= f96527e4d7611a47c5e5cf1c083ed9d3db59ead3564ea6e2e0a81c379b4cbae6
```

Der bestehende S1-OS-Test bleibt byteidentisch. Eine Aenderung seiner
Fixtures oder Erwartungen zur Anpassung an den Refaktor ist verboten.

## Gemeinsamer privater Executor

Das bestehende Kompositionsmodul darf spaeter genau einen privaten Executor
erhalten:

```text
_execute_g2_d3_two_step(...)
-> _G2D3TwoStepExecutionTrace
```

Die private unveraenderliche Trace darf innerhalb des Pakets genau tragen:

```text
composition_result
validated_initial_d3_raw_bytes | not_computable
committed_intermediate_d3_raw_bytes | not_computable
committed_final_d3_raw_bytes | not_computable
```

Bei einem ungueltigen Kompositionsresultat sind alle drei Checkpointbytes in
der Trace `not_computable`. Ein CP0- oder CP1-Teilzustand wird auch intern
nicht als erfolgreiche Trace ausgegeben.

Der Executor ist nicht in `__all__`, besitzt keine oeffentliche Builder- oder
Callbackoberflaeche und wird nicht serialisiert. Nur zwei paketinterne
Aufrufer sind erlaubt:

```text
compose_g2_d3_two_step_continuation
evaluate_g2_d3_two_step_o3_checkpoints
```

Beide rufen ihn pro oeffentlichem Aufruf exakt einmal auf. Es gibt keine
zweite Sequenzimplementierung.

## Neue Checkpoint-API

Eine spaetere Implementierung darf genau bereitstellen:

```text
build_g2_d3_two_step_o3_checkpoint_registry()
-> G2D3TwoStepO3CheckpointRegistry

evaluate_g2_d3_two_step_o3_checkpoints(
    first_boundary_raw_bytes,
    second_boundary_raw_bytes,
    initial_d3_raw_bytes,
    formation_enabled,
    checkpoint_registry,
    sequence_registry,
    target_commit_registry,
    amount_registry,
    boundary_registry,
    d3_registry,
) -> G2D3TwoStepO3CheckpointResult
```

Die drei Byteeingaben muessen exakt `bytes`, der Schalter exakt `bool` und
alle Registries Instanzen ihrer vorregistrierten Klassen sein. Falsche Typen
oder Registries scheitern vor einem Resultat.

Sequenzbeleg, D3-Zwischenbytes, Finalbytes, O3-Beleg, Zielbytes,
Checkpointrolle und erwartete Werte sind keine Eingaben.

## Vertragsdigests

Neue ASCII-Vertragsidentitaet und SHA-256-Digest:

```text
g2.d3.two-step-o3-checkpoints.contract.s1ou.v1
-> 582e0fa653c8843cb56e848abc1ea34b1e97b455f8b0a130f22678afb555191f
```

Die Registry akzeptiert zusaetzlich exakt:

```text
two-step composition contract
= e68646a2d4a605ecdd36125dcd5f97cd849091d5af1bbcf1f587b1c01e1c2e06

O3 admissibility operator contract
= 6f63fcf075a95b6e22ff9cbad9d1326d99478900f6ae613e4cd95da7eacbc756

projector contract
= c761d3f5b2dc486ca6cb9389d305e9b2ec8d847812bac72e40d89995a66f6e2b

commit contract
= 4cae38e9c7986ff6099cfd8c2c742a2c11465bb61a9885441a403fab9b5859b5

amount operator contract
= 396bd7b9fde4b7ee3b268e1d53245fd2a950cf4d8d9464f084d9b498c17de83b

boundary validator contract
= 7a84b6f6dee9ba8f6e7f5cce9ee7655a63104cda669aabe35101072036fdebd0

D3 validator contract
= b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c
```

## Registryform

`G2D3TwoStepO3CheckpointRegistry` ist unveraenderlich und bindet genau:

```text
receipt_schema_id
receipt_schema_version
checkpoint_class_id
checkpoint_roles
checkpoint_statuses
checkpoint_phases
failure_codes
checkpoint_records
accepted_composition_contract_digest
accepted_o3_operator_contract_digest
accepted_projector_contract_digest
accepted_commit_contract_digest
accepted_amount_operator_contract_digest
accepted_boundary_validator_contract_digest
accepted_d3_validator_contract_digest
checkpoint_contract_digest
```

Feste Werte:

```text
receipt_schema_id = g2_d3_two_step_o3_checkpoint_receipt
receipt_schema_version = s1ou.v1
checkpoint_class_id = G2_D3_TWO_STEP_THREE_READ_ONLY_O3_CHECKPOINTS
checkpoint_roles = (CP0_INITIAL, CP1_INTERMEDIATE, CP2_FINAL)
checkpoint_statuses = (THREE_CHECKPOINTS_EVALUATED, not_computable)
```

## Drei Checkpointrecords

Die Registry bindet exakt:

| Rolle | D3-Inputdigest | Anatomierecorddigest | O3-Wert |
|---|---|---|---:|
| `CP0_INITIAL` | `d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7` | `1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f` | `0.5` |
| `CP1_INTERMEDIATE` | `2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8` | `d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c` | `0.25` |
| `CP2_FINAL` | `a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab` | `efba6284b3e56cfe2041465eb8acc76b00de34ee8303f6a2caa20b2a3fc66681` | `0.125` |

Jeder Record traegt ausserdem seine feste Position `0`, `1` oder `2`. Die
Position ordnet nur den ausgefuehrten Commitzustand im Ausgabevektor; sie
darf keinen O3-Sachwert erzeugen.

## Ergebnis und passiver Beleg

Das unveraenderliche Ergebnis enthaelt genau:

```text
checkpoint_values: tuple[float, float, float] | not_computable
receipt: G2D3TwoStepO3CheckpointReceipt
```

Der passive Beleg bindet ausschliesslich:

```text
receipt_schema_id
receipt_schema_version
checkpoint_class_id
first_boundary_input_bytes_digest
second_boundary_input_bytes_digest
initial_d3_input_bytes_digest
formation_enabled
chain_role
composition_receipt_digest
cp0_d3_input_bytes_digest
cp0_anatomy_record_digest
cp0_o3_receipt_digest
cp0_value
cp1_d3_input_bytes_digest
cp1_anatomy_record_digest
cp1_o3_receipt_digest
cp1_value
cp2_d3_input_bytes_digest
cp2_anatomy_record_digest
cp2_o3_receipt_digest
cp2_value
delta_cp1_cp0
delta_cp2_cp1
delta_cp2_cp0
comparison_digest
checkpoint_status
validation_status
completed_checks
failure_reasons
accepted_composition_contract_digest
accepted_o3_operator_contract_digest
accepted_projector_contract_digest
accepted_commit_contract_digest
accepted_amount_operator_contract_digest
accepted_boundary_validator_contract_digest
accepted_d3_validator_contract_digest
checkpoint_contract_digest
checkpoint_receipt_digest
```

Der Beleg enthaelt keine Rohbytes, keine private Trace und keine
verschachtelten Belegobjekte. Sein eigener Digest wird ueber die kanonische
Payload ohne `checkpoint_receipt_digest` berechnet. Er ist kein Folgeeingang.

Bei Erfolg gilt exakt:

```text
checkpoint_values = (0.5, 0.25, 0.125)
delta_cp1_cp0 = -0.25
delta_cp2_cp1 = -0.125
delta_cp2_cp0 = -0.375
checkpoint_status = THREE_CHECKPOINTS_EVALUATED
validation_status = valid
failure_reasons = ()
```

Der orientierungsunabhaengige Vergleichsdigest wird ausschliesslich aus
folgender kanonischer Payload gebildet:

```json
{"checkpoint_values":[0.5,0.25,0.125],"directed_components":[-0.25,-0.125,-0.375]}
```

```text
comparison_digest
= 5c8d3b60bbc205594974f632a878472bf628426dc914af72514cf7b42e8a86a5
```

XXX und YYY muessen denselben Vergleichsdigest, aber wegen unterschiedlicher
Sequenzprovenienz verschiedene vollstaendige Checkpointbelegdigests tragen.

## Gebundene Phasen

```text
api_intake
two_step_execution
composition_validation
cp0_evaluation
cp1_evaluation
cp2_evaluation
checkpoint_identity_gate
component_evaluation
persistence_guard
checkpoint_receipt
```

Der erste Fehler beendet alle nachgelagerten Phasen. O3 wird erst aufgerufen,
wenn eine vollstaendig erfolgreiche private Trace mit allen drei
Checkpointbytes vorliegt.

## Fehlercodes

Die Registry bindet exakt:

```text
OU_TWO_STEP_EXECUTION_FAILED
OU_COMPOSITION_IDENTITY_MISMATCH
OU_CP0_EVALUATION_FAILED
OU_CP1_EVALUATION_FAILED
OU_CP2_EVALUATION_FAILED
OU_CHECKPOINT_IDENTITY_MISMATCH
OU_COMPONENT_IDENTITY_MISMATCH
```

Pro ungueltigem Beleg ist exakt ein Code erlaubt.

### Sequenzfehler

Ein ungueltiges S1-OS-Kompositionsresultat liefert
`OU_TWO_STEP_EXECUTION_FAILED`. Alle drei O3-Aufrufzahlen bleiben null. Der
interne S1-OS-Einzelcode wird nicht als neuer fachlicher Checkpointcode
umgedeutet; nur seine passive Receipt-Digest darf im Checkpointbeleg gebunden
werden.

### Kompositionsidentitaet

Ein gueltiges Kompositionsresultat muss Chainrolle, Finaldigest und
Finalrecorddigest des akzeptierten S1-OS-Records tragen. Andernfalls gilt
`OU_COMPOSITION_IDENTITY_MISMATCH` und O3 bleibt unaufgerufen.

### O3-Einzelfehler

CP0, CP1 und CP2 werden in dieser Reihenfolge je einmal mit dem bestehenden
O3-Operator ausgewertet. Ein ungueltiger O3-Beleg liefert den jeweiligen
Einzelcode. Trotz bereits intern berechneter frueherer Werte werden im
oeffentlichen Resultat und Beleg alle drei Werte sowie alle Komponenten
`not_computable`.

### Identitaets- und Komponentengate

Nach drei gueltigen O3-Belegen muessen D3-Digests, Recorddigests und Werte
exakt den Registryrecords entsprechen. Andernfalls gilt
`OU_CHECKPOINT_IDENTITY_MISMATCH`.

Erst danach werden die drei gerichteten Komponenten exakt berechnet und
gegen ihre Registrywerte sowie den Vergleichsdigest geprueft. Eine
Abweichung liefert `OU_COMPONENT_IDENTITY_MISMATCH` und keinen Vektor.

## Aufruf- und Persistenzgrenze

Pro gueltigem Checkpointaufruf gilt maximal:

```text
private two-step executor calls = 1
public compose calls = 0
O3 calls = 3
```

Der private Executor verwendet intern weiterhin die bereits gebundenen
Projektions-, Commit- und Validatoraufrufe. Der Checkpointpfad startet keine
zweite Komposition zur Kontrolle.

Checkpointbytes werden nicht in Resultat, Beleg, Cache, globale Variable,
Datei oder Runtime geschrieben. O3 mutiert weder Trace noch D3.

## Gegenbaseline- und Aussagegrenze

S1-OU bindet nur Schema und technische Provenienz einer konstruktiven
O3-Zulassungsfolge. Eine angepasste zustandsbehaftete Baseline kann denselben
Vektor erzeugen und bleibt fuer jede spaetere Funktionsentscheidung
zwingend.

Es gibt noch keinen Checkpointoperator und keinen neuen Lauf. Es gibt keine
tatsaechliche Aufnahme, keine Feldrueckwirkung, keine Funktionsabgrenzung und
keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OV darf ausschliesslich die Refaktorierungsdateien, unveraenderten
S1-OS-Regressionstest, zwei gueltige Checkpointchains, externe
Sequenzfehlermutationen, defensive Gates und ein endliches Einmaltestbudget
binden.

S1-OV darf keine Produktions- oder Testimplementierung, keinen Testlauf,
keine Runtimepublikation und keinen Feld-, Transfer-, Runner- oder
Medienpfad ausfuehren.
