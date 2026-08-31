# S2-IF - Statischer Korrekturvertrag der getrennten Probenrollen

## Status

`S2IF_STATIC_DUAL_PROBE_SOURCE_CORRECTION_BOUND_IMPLEMENTATION_LOCKED`

S2-IF korrigiert ausschliesslich die Quellenueberbindung zwischen dem
vollstaendigen Kontextabruf und der spaeteren maskierten Signalpruefung. Die
S2-IC-Statuslogik, ihre fuenf Statuswerte, Direktbaseline, Ledgerformeln und
S2-ID-Qualifikation bleiben unveraendert.

Es wurden keine Module implementiert oder importiert, keine Tests ausgefuehrt
und keine Rezeptor-, Speicher-, Projektions- oder Signalfunktion aufgerufen.

## Zwei getrennte Datenrollen

### `ContextRetrievalProbe`

Die unveraenderliche Form enthaelt exakt:

```text
schema
case_plan_digest
role = CONTEXT_RETRIEVAL_PROBE
probe_id
source_id
source_digest
receptor_receipt_digest
config_digest
auditory_values_digest
visual_values_digest
av_values_digest
function_probe_digest
value_dimension = 26
window_start_tick
window_end_tick
context_retrieval_probe_digest
```

`function_probe_digest` ist der native Digest der vollstaendigen S2-FS-
Probe. Ausschliesslich dieser Digest darf als `probe_digest` in den daraus
entstehenden S2-FS-, S2-GC- und S2-GI-Befunden erscheinen.
`context_retrieval_probe_digest` ist dagegen der Digest der typisierten
S2-IF-Rollenhuelle. Beide sind explizit und duerfen nicht durch den jeweils
anderen ersetzt werden.

Die Retrieval-Probe ist ausschliesslich Elternquelle fuer:

```text
S2-FS-read-only Finding
-> S2-GC-Bundle
-> S2-GI-A/B-Kandidatenbefunde
```

Sie ist keine Elternquelle der sichtbaren Anwendbarkeitspruefung oder des
Maskenergaenzungsvergleichs.

### `MaskedSignalProbe`

Die unveraenderliche Form enthaelt exakt:

```text
schema
case_plan_digest
role = MASKED_SIGNAL_PROBE
probe_id
source_id
source_digest
receptor_receipt_digest
config_digest
visual_values_digest
visible_values_digest
mask_digest
masked_visual_probe_digest
visible_positions
masked_positions
value_dimension = 18
window_start_tick
window_end_tick
masked_signal_probe_digest
```

`masked_visual_probe_digest` ist der native Digest des qualifizierten
`MaskedVisualProbe`-Objekts. `masked_signal_probe_digest` bindet die typisierte
S2-IF-Rollenhuelle.

Die Signalprobe ist ausschliesslich Elternquelle fuer:

```text
A-/B-Anwendbarkeitsbefunde
-> MaskedSupplementComparison
-> TwoAreaConflictSignalResult
```

Sie darf weder einen A-/B-Kandidaten erzeugen noch eine erneute Speicherprobe
ausloesen.

## Keine Probeableitung und keine Digestgleichheit

Verboten sind:

- `context_retrieval_probe_digest == masked_signal_probe_digest` als
  Gueltigkeitsbedingung;
- `function_probe_digest == masked_visual_probe_digest` als
  Gueltigkeitsbedingung;
- Erzeugung einer Probe aus Finding, Kandidat, Ergebnis oder Zielwert der
  anderen;
- nachtraegliche Rekonstruktion einer Probe aus S2-GC-, S2-GI- oder
  S2-IC-Belegen;
- Verwendung der Kontextabrufprobe fuer die sichtbare Konfliktentscheidung;
- Verwendung der Signalprobe fuer Kandidatensuche oder Speicherabruf.

Identische Digests sind nicht pauschal verboten, falls zwei unabhaengig
gebildete Probeobjekte zufaellig bytegleich sind. Eine solche Gleichheit hat
jedoch keinerlei Autorisierungs- oder Funktionswirkung und darf nie verlangt
oder aus einem Ergebnis abgeleitet werden.

## Gemeinsame vorgebildete Fallplanwurzel

Die einzige gemeinsame Zugehoerigkeit beider Rollen ist ein vor jeder
Probeoperation gebildeter `S2IFCaseProbePlan` mit exakt diesen Feldern:

```text
schema
plan_id
history_id
context_fixture_id
signal_fixture_id
config_digest
registry_digest
context_role = CONTEXT_RETRIEVAL_PROBE
signal_role = MASKED_SIGNAL_PROBE
context_operation_id
signal_operation_id
context_value_dimension = 26
signal_value_dimension = 18
visible_positions
masked_positions
functional_budget_digest
case_plan_digest
```

Der Fallplan bindet nur Quellen, Rollen, Operationen und Budgets. Er enthaelt
keinen Sollstatus, Zielwert, Gewinner, Ergebnis- oder Evaluationsdigest.
`ContextRetrievalProbe` und `MaskedSignalProbe` entstehen als unabhaengige
Geschwister aus dieser bereits vorhandenen Wurzel.

## Getrennte native Relationen

Vor jeder Signalausfuehrung muessen exakt gelten:

```text
two_area_bundle.probe_digest
    == context_retrieval_probe.function_probe_digest

signal_input.probe_digest
    == masked_signal_probe.masked_visual_probe_digest

signal_input.bundle_digest
    == two_area_bundle.bundle_digest

context_retrieval_probe.case_plan_digest
    == masked_signal_probe.case_plan_digest
```

Ausdruecklich nicht gefordert wird:

```text
two_area_bundle.probe_digest == signal_input.probe_digest
```

Damit bleiben Abruf und Signalpruefung getrennte Vorgange, waehrend das
Signal weiterhin ein vollstaendig gebundenes A/B-Bundle gegen genau eine
gebundene maskierte Probe auswertet.

## Atomare Dual-Probe-Bindung

`S2IFDualProbeCaseBinding` enthaelt exakt:

```text
schema
case_plan_digest
context_retrieval_probe_digest
context_function_probe_digest
masked_signal_probe_digest
masked_visual_probe_digest
context_source_digest
signal_source_digest
two_area_bundle_digest
bundle_context_probe_digest
signal_input_digest
baseline_input_digest
source_ledger_digest
dual_probe_binding_digest
```

Die Form wird erst erzeugt, nachdem beide Probehuellen, das vollstaendige
A/B-Bundle und beide ownerfreien Arminputs validiert sind. Sie bindet keine
Armresultate und keine Evaluation.

## Ein atomarer Fallowner

Je Fall existiert genau ein `S2IFDualProbeCaseOwner`. Signal und Baseline
behalten zusaetzlich ihre jeweils qualifizierten internen S2-IC-Einmalowner;
diese sind Kindautorisierungen und ersetzen den Fallowner nicht.

Der unveraenderliche Fallowner-Vorzustand enthaelt:

```text
schema
owner_id
case_plan_digest
dual_probe_binding_digest
context_retrieval_probe_digest
masked_signal_probe_digest
two_area_bundle_digest
signal_input_digest
baseline_input_digest
state = READY
owner_prestate_digest
```

Der einzige Uebergang lautet:

```text
READY -> CONSUMED | FAILED
```

Der Nachzustand enthaelt:

```text
schema
owner_id
case_plan_digest
dual_probe_binding_digest
context_retrieval_probe_digest
masked_signal_probe_digest
prior_owner_digest
signal_result_digest
baseline_result_digest
terminal_pair_digest
state = CONSUMED | FAILED
owner_poststate_digest
```

Bei Erfolg werden Signal- und Baselinebefund zuerst lokal vollstaendig
validiert. Danach entstehen `terminal_pair_digest`, Owner-Nachzustand und
Fallbeleg atomar. Vor diesem Commit ist kein Armresultat als Fallbefund
sichtbar. Bei Fehler entsteht kein regulaerer Fallbeleg.

Wiederverwendung, Teilcommit, Retry und ein zweiter Owneruebergang sind
verboten.

## Neu geordneter Fallblock

S2-IF erzeugt keine neue Operation. Der siebenstufige S2-IE-Fallblock wird
lediglich neu geordnet:

```text
1 SIGNAL_PROBE_RECEPTOR
2 MASKED_SIGNAL_PROBE_PROJECT
3 DUAL_PROBE_AND_ARM_INPUTS_BIND
4 SIGNAL_INVOKE
5 BASELINE_INVOKE
6 DUAL_PROBE_CASE_OWNER_COMMIT
7 CASE_EVIDENCE_SEAL
```

Operation 3 bildet beide ownerfreien Arminputs, beide internen S2-IC-Owner
und den Fallowner, bevor ein Arm aufgerufen wird. Die fruehere getrennte
`BASELINE_INPUT_BIND`-Stufe wird nicht zusaetzlich ausgefuehrt, sondern geht
atomar in Operation 3 auf. Operation 6 nimmt beide lokalen Armresultate ab.

Die S2-IE-Gesamtgrenzen bleiben daher exakt:

```text
183 Erfolgsoperationen
366 START-/RESULT-Ereignisse
185 Operationen / 370 Ereignisse im maximalen Fehlerpfad
```

## Quellenledger

`S2IFDualProbeSourceLedger` enthaelt exakt:

```text
case_plan_validation_count              = 1
typed_probe_validation_count            = 2
source_binding_validation_count         = 2
receptor_receipt_validation_count       = 2
configuration_binding_validation_count  = 2
context_native_probe_relation_count      = 1
signal_native_probe_relation_count       = 1
bundle_context_probe_relation_count      = 1
arm_input_relation_count                 = 2
context_value_reference_count           = 26
signal_position_validation_count        = 18
digest_validation_count                 = 39
owner_transition_count                  = 1
new_digest_operation_count              = 8
storage_or_learning_call_count           = 0
ledger_digest
```

Die acht neuen Digests sind Rollenhuelle der Retrieval-Probe, Rollenhuelle
der Signalprobe, Dual-Probe-Bindung, Quellenledger, Owner-Vorzustand,
terminaler Ergebnispaarbeleg, Owner-Nachzustand und Fallbeleg. Native Probe-,
S2-IC-Input-, Resultat- und Receipt-Digests verbleiben in ihren jeweiligen
qualifizierten Ledgers und werden nicht als neue S2-IF-Arbeit doppelt
gezaehlt.

Ueber acht S2-IE-Faelle entstehen damit exakt:

```text
8 Fallplanvalidierungen
16 typisierte Probevalidierungen
16 Quellenbindungen
16 ReceptorReceipt-Pruefungen
16 Konfigurationsbindungen
8 Kontextprobe-, 8 Signalprobe- und 8 Bundle-Kontextrelationen
16 Arminputrelationen
208 Kontextwertreferenzen
144 Signalpositionsvalidierungen
312 Digestvalidierungen
8 Owneruebergaenge
64 neue Digestoperationen
0 Speicher-/Lernaufrufe
```

Das S2-IC-Funktionsledger aus S2-IE bleibt unveraendert und wird getrennt
berichtet.

## Kanonische Artefaktgroessen

Die vollstaendigen ASCII-Huellen wurden statisch mit 96-Zeichen-IDs,
64-Zeichen-Digests, maximalen Tickwerten und vollstaendigen Positionstupeln
berechnet:

| Form | Bytes | Grenze | Reserve |
| --- | ---: | ---: | ---: |
| `S2IFCaseProbePlan` | 1145 | 2048 | 903 |
| `ContextRetrievalProbe` | 1186 | 1792 | 606 |
| `MaskedSignalProbe` | 1264 | 1792 | 528 |
| `S2IFDualProbeCaseBinding` | 1259 | 2048 | 789 |
| `S2IFDualProbeSourceLedger` | 654 | 1536 | 882 |
| Fallowner-Vorzustand | 913 | 1792 | 879 |
| Fallowner-Nachzustand | 1005 | 1792 | 787 |
| `S2IFCaseEvidence` | 2090 | 3584 | 1494 |
| Fehlerursache | 809 | 1536 | 727 |
| ErrorReceipt | 660 | 1536 | 876 |

Alle Zahlen enthalten den kanonischen Zeilenabschluss. Keine Form erreicht
4095 Byte. Die bestehenden S2-IE-, S2-IC-, S2-FS-, S2-GC- und S2-GI-Grenzen
werden weder erhoeht noch durch eingebettete Vollobjekte umgangen.

## Fallbeleg

`S2IFCaseEvidence` enthaelt exakt:

```text
schema
case_plan_digest
context_retrieval_probe_digest
context_function_probe_digest
masked_signal_probe_digest
masked_visual_probe_digest
dual_probe_binding_digest
source_ledger_digest
owner_prestate_digest
owner_poststate_digest
two_area_bundle_digest
bundle_context_probe_digest
signal_input_digest
signal_result_digest
signal_receipt_digest
baseline_input_digest
baseline_result_digest
baseline_receipt_digest
composite_prestate_digest
composite_poststate_digest
signal_ledger_digest
baseline_ledger_digest
case_evidence_digest
```

Der Fallbeleg enthaelt keinen Sollstatus. Die getrennte
`EvaluationRunBinding` verbindet diesen Beleg erst nach vollstaendig
versiegelter Ausfuehrung mit dem unabhaengigen Evaluationsplan.

## Fehlerregistry

| Code | Message-ID | Ursache |
| --- | --- | --- |
| `S2IF-E001` | `TYPE_OR_SCHEMA_INVALID` | Typ oder Schema verletzt |
| `S2IF-E002` | `SOURCE_OR_DIGEST_INVALID` | Quelle oder Digest verletzt |
| `S2IF-E003` | `CASE_PLAN_INVALID` | vorgebildete Fallplanwurzel verletzt |
| `S2IF-E004` | `PROBE_ROLE_INVALID` | Retrieval- oder Signalrolle verletzt |
| `S2IF-E005` | `OWNER_INVALID` | Ownerbindung oder Zustand verletzt |
| `S2IF-E006` | `READ_ONLY_VIOLATION` | Memory-Vor-/Nachzustand unterscheidet sich |
| `S2IF-E007` | `RESOURCE_BOUND_EXCEEDED` | Ledger- oder Groessengrenze verletzt |
| `S2IF-E008` | `ATOMICITY_OR_REUSE_VIOLATION` | Teilcommit oder Wiederverwendung |

Fehlertexte sind feste neutrale ASCII-Message-IDs. Ein Fehler darf weder
Sollstatus noch Zielwerte oder dynamische Kandidateninhalte enthalten.

## Digestgraph

```text
ExecutionPlan
-> S2IFCaseProbePlan

CaseProbePlan + Retrievalquelle
-> ContextRetrievalProbe
-> S2-FS-read-only
-> S2-GC
-> S2-GI-Bundle

CaseProbePlan + unabhaengige Signalquelle
-> MaskedSignalProbe

ContextRetrievalProbe + MaskedSignalProbe + S2-GI-Bundle
    + beide ownerfreien Arminputs + Quellenledger
-> DualProbeCaseBinding
-> Fallowner READY

Signalinput + eigener S2-IC-Owner
-> Signalresultat

Baselineinput + eigener S2-IC-Owner
-> Baselineresultat

beide Resultate
-> terminaler Paarbeleg
-> Fallowner CONSUMED
-> S2IFCaseEvidence

unabhaengiger EvaluationPlanSeal + vollstaendige Ausfuehrungsevidenz
-> EvaluationRunBinding
```

Beide Probehuellen sind Geschwister und keine Eltern voneinander. Kein Digest
bindet sich selbst, einen spaeteren Digest oder einen Evaluationswert.

## Fail-Closed und Freigabegrenze

Fail-closed sind insbesondere:

- fehlende, fremde, vertauschte oder nachtraeglich erzeugte Probehuelle;
- Verwendung des Retrieval-Digests als maskierter Probedigest oder umgekehrt;
- ein Bundle, dessen nativer Probedigest nicht zur Retrieval-Probe gehoert;
- ein S2-IC-Input, dessen nativer Probedigest nicht zur Signalprobe gehoert;
- voneinander abweichende Fallplandigests;
- Owner ohne beide getrennte Probendigestbindungen;
- Teilveroeffentlichung eines Arms, Wiederverwendung oder Budgetbruch;
- Evaluationsdaten im Ausfuehrungsgraphen.

S2-IF ist statisch gebunden. Noch gesperrt bleiben Codeaenderung,
Implementierung, Tests und Ausfuehrung. Als naechster Schritt ist der
vollstaendige statische Wiederholungsaudit des S2-IE-Plans gegen diese
Korrektur erforderlich.
