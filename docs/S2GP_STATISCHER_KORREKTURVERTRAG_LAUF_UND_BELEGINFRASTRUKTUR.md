# S2-GP: Statischer Korrekturvertrag fuer Lauf- und Beleginfrastruktur

## Auftrag und Grenze

S2-GP schliesst ausschliesslich die im S2-GO-Audit festgestellten Blocker
`GO-B01` bis `GO-B06`. Der Funktionsvertrag aus S2-GJ, die
rezeptorrealistischen Bilder aus S2-GL, die Probenrollen aus S2-GN sowie
S2-GK, Schwellen, Speicherkerne und Erfolgskriterien bleiben unveraendert.

S2-GP erlaubt keine Implementierung, keine Imports von Projektmodulen, keine
Tests und keine Rezeptor-, Speicher-, Projektions-, Verbraucher-, Runner-
oder Dateiausfuehrung.

Technischer Ausgangsstand:

`b5ed539e8ff5e3144995c63119fc403a2da23cb0`

## GO-B01: Literale Operationsregistries

Die Erfolgsregistry liegt vollstaendig und unveraenderlich in:

`docs/S2GP_OPERATION_REGISTRY.csv`

SHA-256:

`126bb311b01e3075ae68cf0e017f547103d3e4a1b068021670196d9b4338dcc5`

Sie enthaelt exakt `op-0001` bis `op-0139`. Jede Zeile bindet:

- Operations-ID und Ordinalzahl;
- neutrale History oder Laufrolle;
- konkrete Quellordinalzahl;
- Operationsklasse;
- erwartete Elternreceipts;
- genau einen Nachfolger oder `END`;
- genau eine Ressourcenrolle.

Die bedingte Fehlerabschlussregistry liegt getrennt in:

`docs/S2GP_FAILURE_OPERATION_REGISTRY.csv`

SHA-256:

`23e49213b0ab94654ac4019bb25282c1bec0c47681ad9594e9e8c786a45ac8be`

Sie enthaelt ausschliesslich `err-0001` bis `err-0003`. Fehleroperationen
ersetzen keine Erfolgsoperation und duerfen nur nach dem ersten technischen
Fehler beginnen.

Es gelten verbindlich:

1. Eine Operation darf nur ausgefuehrt werden, wenn ihre vollstaendige
   Registryzeile im versiegelten `ExecutionPlan` digestgebunden ist.
2. Operations-ID, History, Quellordinal, Klasse, Eltern, Nachfolger und
   Ressourcenrolle muessen der Zeile exakt entsprechen.
3. Es gibt keine dynamisch erzeugten, impliziten oder unregistrierten
   Operationen.
4. Hilfsarbeit gehoert ausschliesslich zur literal benannten Ressourcenrolle.
5. Ein unbekannter Nachfolger, eine zweite Verwendung oder eine vertauschte
   Registryzeile stoppt vor dem Funktionsaufruf fail-closed.

### Korrigierte Erfolgsklassen

| Operationsklasse | Anzahl |
| --- | ---: |
| `RUN_PREPARE` | 1 |
| `FORMATION_RECEPTOR_ANALYSIS` | 52 |
| `COMPOSITE_FORMATION` | 52 |
| `CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS` | 4 |
| `COMPOSITE_READ_ONLY_PROBE` | 4 |
| `CONSUMER_RECEPTOR_ANALYSIS` | 1 |
| `MASKED_PROBE_BIND` | 1 |
| `S2GC_PROJECTION` | 4 |
| `S2GI_PROJECTION` | 4 |
| `ARM_EXECUTION` | 7 |
| `EXECUTION_EVIDENCE_SEAL` | 1 |
| `EVALUATION_RUN_BIND` | 1 |
| `PURE_EVALUATION` | 4 |
| `FINAL_EVIDENCE_PUBLISH` | 1 |
| `TERMINAL_PUBLISH` | 1 |
| `COMPLETION_MARKER_PUBLISH` | 1 |
| **gesamt** | **139** |

Jede Erfolgsoperation besitzt genau ein `START`- und ein `RESULT`-Ereignis.
Der korrigierte Erfolgsumfang lautet deshalb:

```text
139 Operationen
278 Ereignisse
```

Die frueheren Umfaenge `136/272` und `131/262` sind fuer diesen Lauf
ersetzt.

## GO-B02: Abschlussreihenfolge

Der Erfolgsabschluss besteht aus drei getrennten Operationen:

```text
op-0137 FINAL_EVIDENCE_PUBLISH
op-0138 TERMINAL_PUBLISH
op-0139 COMPLETION_MARKER_PUBLISH
```

Die Reihenfolge ist unveraenderlich:

```text
FINAL_EVIDENCE_PUBLISH_START
-> FinalEvidencePackage
-> FINAL_EVIDENCE_PUBLISH_RESULT

TERMINAL_PUBLISH_START
-> TerminalFinding
-> TERMINAL_PUBLISH_RESULT

COMPLETION_MARKER_PUBLISH_START
-> CompletionMarker
-> COMPLETION_MARKER_PUBLISH_RESULT
```

Das jeweilige `OperationResult.output_receipt_digest` bindet den Digest des
innerhalb der Operation erzeugten Artefakts. Kein Artefakt enthaelt den
Resultdigest seiner eigenen Publikationsoperation.

### Korrigierte Abschlussformen

`FinalEvidencePackage`:

```text
schema
run_id
owner_id
reservation_receipt_digest
execution_evidence_digest
evaluation_run_binding_digest
evaluation_receipt_digests
complete_function_counts
final_evidence_digest
```

`TerminalFinding`:

```text
schema
run_id
owner_id
reservation_receipt_digest
status = RECORDING_COMPLETE
final_evidence_digest
recorded_success_operation_count = 139
recorded_success_event_count = 278
terminal_digest
```

`CompletionMarker`:

```text
schema
run_id
owner_id
reservation_receipt_digest
terminal_digest
final_evidence_digest
marker_role = COMPLETE
marker_digest
```

Terminal und Marker enthalten keinen `final_operation_result_digest` und
keinen anderen zukuenftigen Digest.

Erst ein gueltiges `COMPLETION_MARKER_PUBLISH_RESULT`, das den
`marker_digest` als Ausgabe bindet, bestaetigt den Erfolgspfad. Ein vorhandener
Marker ohne dieses Resultat gilt nicht als Abschluss.

## GO-B03: Pfade, Reservierung und Owner

### Neutrales Laufverzeichnis

Der spaetere Lauf darf nur ein neues Verzeichnis unter dieser festen Rolle
reservieren:

`workspace/reports/s2gj_masked_context/<run_id>/`

`run_id` muss dem neutralen Muster
`s2gj-run-[0-9]{8}-[0-9]{2}` entsprechen. Fallrollen, Bildrollen,
Sollentscheidungen und Ergebniswoerter sind im Pfad unzulaessig.

`RUN_PREPARE` fuehrt vor jedem Funktionsaufruf eine atomar exklusive
Reservierung durch. Existiert irgendein Zielpfad bereits, endet der Start
fail-closed. Fortsetzen, Ueberschreiben, Reparieren und Wiederverwenden sind
gesperrt.

`ExecutionPlan` und `EvaluationPlanSeal` liegen vor `RUN_PREPARE` bereits als
autorisierte, unveraenderliche kanonische Bytes mit bekannten Digests vor.
Sie liegen zu diesem Zeitpunkt noch nicht im Zielverzeichnis. Erst nach der
erfolgreichen exklusiven Reservierung publiziert `RUN_PREPARE` beide
byteidentisch in ihre festen Pfadrollen. Diese Publikation ist Bestandteil
von `op-0001` und keine implizite Voroperation.

### Feste Pfadrollen

| Pfadrolle | kanonischer relativer Pfad |
| --- | --- |
| Reservierung | `reservation.json` |
| Manifest und ExecutionPlan | `manifest.json` |
| EvaluationPlanSeal | `evaluation/plan-seal.json` |
| Ereignisjournal | `journal/operations.jsonl` |
| Funktionsreceipts | `receipts/op-<nnnn>.json` |
| ExecutionEvidencePackage | `evidence/execution.json` |
| EvaluationRunBinding | `evaluation/run-binding.json` |
| EvaluationReceipts | `evaluation/e<nn>.json` |
| FinalEvidencePackage | `evidence/final.json` |
| TerminalFinding | `terminal.json` |
| CompletionMarker | `COMPLETE` |
| RunFailureReceipt | `failure/run-failure.json` |
| FailureTerminalFinding | `failure/terminal.json` |
| FailureClosureMarker | `NOT_EVALUABLE` |

`manifest.json` ist der kanonische `ExecutionPlan`; es entsteht kein
zweites Manifest.

### ReservationReceipt

```text
schema
run_id
root_path_role
root_path_digest
execution_plan_digest
evaluation_plan_seal_digest
authorization_digest
owner_id
reservation_nonce
reserved_empty = true
reservation_digest
```

`owner_id` wird ausschliesslich aus Run-ID, Autorisierung,
ExecutionPlan-Digest und Reservierungsnonce abgeleitet. Der Owner wird nicht
aus einem Bild, Fall, Ergebnis oder Zielwert gewonnen.

`RUN_PREPARE_START` bindet `run_id`, den bereits autorisierten `owner_id`,
Zielpfadrolle, Reservierungsnonce und beide Plandigests. Es kann den erst in
dieser Operation erzeugten `reservation_digest` noch nicht enthalten.
`RUN_PREPARE_RESULT` bindet den ausgegebenen `ReservationReceipt`. Ab
`op-0002` bindet jedes START-, RESULT-, Receipt-, Evidenz-, Terminal- und
Markerartefakt `run_id`, `owner_id` und `reservation_digest`. Diese Bindung
bleibt bis `op-0139` unveraendert. Ein abweichender Owner oder eine fremde
Reservierung stoppt vor einer Ausgabe.

## GO-B04: Kanonischer Fehlerabschluss

Der Fehlerpfad verwendet ausschliesslich die getrennte Registry
`err-0001..err-0003`:

```text
FAILURE_EVIDENCE_PUBLISH
-> FAILURE_TERMINAL_PUBLISH
-> FAILURE_CLOSURE_MARKER_PUBLISH
```

### RunFailureReceipt

```text
schema
failure_id
run_id
owner_id
reservation_receipt_digest
failed_operation_id
failed_operation_class
failed_phase
neutral_error_code
last_valid_event_digest
partial_state_digest
partial_artifact_digests
status = NOT_EVALUABLE
failure_message_id
failure_digest
```

`failure_id` besitzt das neutrale Muster
`failure-[0-9]{4}`. `failure_message_id` verweist nur auf einen
vorregistrierten technischen Nachrichtentext. Freitext, Fallnamen,
Bildrollen, Zielwerte und Sollentscheidungen sind gesperrt.

`FailureTerminalFinding` bindet den `failure_digest`, den letzten bestaetigten
Eventdigest, den Teilstandsdigest, Owner und `NOT_EVALUABLE`.
`FailureClosureMarker` bindet ausschliesslich diesen Fehlerterminaldigest
und die Rolle `NOT_EVALUABLE`.

Scheitert auch eine Fehlerabschlussoperation, entsteht kein Ersatzabschluss.
Das vorhandene Teilverzeichnis bleibt allein durch den fehlenden gueltigen
`COMPLETION_MARKER_PUBLISH_RESULT` nicht auswertbar. Es gibt keinen Retry,
keine Teilfortsetzung und keine neue Berechtigung.

## GO-B05: Vollstaendige Budgets

### Funktionale Budgets

Alle funktionalen S2-GN-Budgets bleiben unveraendert:

- 57 Rezeptoranalysen und 1.641.600 analysierte Rohbytes;
- 52 Composite-Bildungen;
- vier Composite-read-only Proben;
- vier S2-GC- und vier S2-GI-Projektionen;
- sieben budgetgleiche Armresultate;
- vier reine Auswertungen.

Das hier korrigierte Aufzeichnungsbudget ist davon getrennt.

### Erfolgspfad

| Artefakt | Anzahl | Maximum je Artefakt | Maximum |
| --- | ---: | ---: | ---: |
| START/RESULT | 278 | 4.096 | 1.138.688 |
| Rezeptorreceipt | 57 | 4.096 | 233.472 |
| Formationreceipt | 52 | 4.096 | 212.992 |
| Kontext-read-only Receipt | 4 | 16.384 | 65.536 |
| S2-GC-/S2-GI-Receipt | 8 | 4.096 | 32.768 |
| MaskedProbeReceipt | 1 | 4.096 | 4.096 |
| Armreceipt | 7 | 8.192 | 57.344 |
| EvaluationReceipt | 4 | 8.192 | 32.768 |
| ExecutionPlan/Manifest | 1 | 16.384 | 16.384 |
| EvaluationPlanSeal | 1 | 8.192 | 8.192 |
| ReservationReceipt mit Owner | 1 | 4.096 | 4.096 |
| ExecutionEvidencePackage | 1 | 131.072 | 131.072 |
| EvaluationRunBinding | 1 | 8.192 | 8.192 |
| FinalEvidencePackage | 1 | 65.536 | 65.536 |
| TerminalFinding | 1 | 4.096 | 4.096 |
| CompletionMarker | 1 | 2.048 | 2.048 |
| **Erfolgsmaximum** |  |  | **2.017.280 Bytes** |

Das Ereignisjournal ist durch die 278 START-/RESULT-Artefakte vollstaendig
gezaehlt. Manifest, Reservierung und Owner sind explizit enthalten.

### Maximaler Fehlerpfad

Der groesste typisierte Fehlerpfad liegt nach Erzeugung des letzten
Erfolgsartefakts, aber vor bestaetigtem Abschluss der letzten
Publikationsoperation. Er darf deshalb konservativ alle Erfolgsartefakte,
sechs zusaetzliche Fehlerabschlussereignisse und folgende Artefakte enthalten:

| zusaetzliches Fehlerartefakt | Anzahl | Maximum |
| --- | ---: | ---: |
| RunFailureReceipt | 1 | 8.192 |
| FailureTerminalFinding | 1 | 4.096 |
| FailureClosureMarker | 1 | 2.048 |
| sechs Fehler-START/RESULT | 6 | 24.576 |

Damit gilt exakt:

```text
2.017.280
+ 8.192
+ 4.096
+ 2.048
+ 24.576
= 2.056.192 Bytes
```

Die verbindliche Gesamtbytegrenze ist das Maximum beider vollstaendig
typisierten Pfade:

`MAX_RECORDING_BYTES = 2.056.192`

Nicht verwendete Fehlerartefakte duerfen nicht als Erfolgspadding geschrieben
werden. Jede Byteueberschreitung stoppt vor Publikation des betroffenen
Artefakts fail-closed.

## GO-B06: Zwei Evaluationszeitpunkte

### Zeitpunkt 1: Vorabversiegelung

Vor `RUN_PREPARE` werden ausschliesslich folgende unveraenderliche Regeln im
`EvaluationPlanSeal` versiegelt:

- getrennte Fallzuordnung;
- Zielwertfixture;
- Entscheidungskriterien;
- Auswerterquelldigest;
- Evaluationsressourcenbudget.

Der Seal wird vor dem Lauf festgelegt, ist aber kein Elternartefakt von
Rezeptor-, Speicher-, Kontext-, Masken-, Arm- oder
`ExecutionEvidencePackage`-Artefakten. Der Ausfuehrungspfad darf seinen
Payload nicht lesen.

### Zeitpunkt 2: Laufbindung nach Ausfuehrung

Erst nach einem vollstaendigen `ExecutionEvidencePackage` fuehrt
`op-0132 EVALUATION_RUN_BIND` beide Wurzeln zusammen:

```text
EvaluationRunBinding
  run_id
  owner_id
  reservation_receipt_digest
  execution_evidence_digest
  evaluation_plan_seal_digest
  evaluator_source_digest
  evaluation_budget_digest
  binding_digest
```

Die Operation prueft nur Identitaet, Vollstaendigkeit und Berechtigung. Sie
wertet keine Armresultate aus. Erst ihr gueltiges RESULT autorisiert
`op-0133..op-0136 PURE_EVALUATION`.

Damit gelten gleichzeitig:

- Soll- und Entscheidungsregeln entstehen nicht aus Ergebnissen;
- sie beeinflussen den Funktionspfad nicht;
- ihre konkrete Laufbindung entsteht erst nach abgeschlossener
  ExecutionEvidence;
- Zielwerte erreichen ausschliesslich den reinen Auswerter;
- eine fehlende oder fremde Laufbindung endet `NOT_EVALUABLE`.

## Vorwaertsgerichteter Gesamtgraph

```text
ExecutionPlan + RunAuthorization
-> ReservationReceipt
-> Funktionsoperationen
-> ExecutionEvidencePackage

EvaluationPlanSeal                    [separate vorab versiegelte Wurzel]
ExecutionEvidencePackage + EvaluationPlanSeal
-> EvaluationRunBinding
-> EvaluationReceipts

ExecutionEvidencePackage + EvaluationRunBinding + EvaluationReceipts
-> FinalEvidencePackage
-> FINAL_EVIDENCE_PUBLISH_RESULT
-> TerminalFinding
-> TERMINAL_PUBLISH_RESULT
-> CompletionMarker
-> COMPLETION_MARKER_PUBLISH_RESULT
```

Der Fehlergraph zweigt nur vom ersten technischen Fehler beziehungsweise
letzten gueltigen Event ab:

```text
failed operation + last valid event + partial state
-> RunFailureReceipt
-> FailureTerminalFinding
-> FailureClosureMarker
```

Kein Artefakt enthaelt seinen eigenen Digest oder einen Digest eines
Nachfahren. Registry-, Plan-, Pfad-, Owner-, Fehler- und Evaluationskanten
sind vorwaertsgerichtet.

## Falsifikation und Stopp

Eine spaetere Implementierung bleibt gesperrt bei:

- einer fehlenden oder abweichenden Registryzeile;
- einer Operation ausserhalb `op-0001..op-0139` oder
  `err-0001..err-0003`;
- einem Terminal oder Marker mit zukuenftigem Resultdigest;
- einer nicht exklusiven Reservierung oder fremden Ownerbindung;
- einem Pfad ausserhalb der festen Rollen;
- einer Fallrolle in technischen IDs, Pfaden, Receipts oder Fehlertexten;
- einem nicht typisierten Teilstand;
- einem Budgetwert ueber `2.056.192` Bytes;
- einer Evaluation vor gueltiger `EvaluationRunBinding`;
- einer Speicher-, Bundle- oder Kontextzustandsaenderung waehrend Probe oder
  Auswertung.

Jeder dieser Faelle ergibt `NOT_EVALUABLE`, keinen negativen
Memory-Funktionsbefund.

## Vertragsentscheidung

S2-GP schliesst `GO-B01` bis `GO-B06` auf statischer Vertragsebene.
Die Operationsanzahl ist auf `139/278` korrigiert. Erfolgs- und
Fehlerabschluss, Pfadrollen, Ownerbindung, Fehlerbelege, vollstaendige
Aufzeichnungsbudgets und beide Evaluationszeitpunkte sind eindeutig
materialisiert.

Status:

`PASS_S2GP_STATIC_RUN_AND_EVIDENCE_CORRECTION_CONTRACT_BOUND`

Fixtures, Runner, Recorder, Verifikator, Tests und Ausfuehrung bleiben
gesperrt. Vor Implementierung ist ein enger statischer
Materialisierungs-, Nichtzirkularitaets- und Budgetaudit gegen S2-GP
erforderlich.
