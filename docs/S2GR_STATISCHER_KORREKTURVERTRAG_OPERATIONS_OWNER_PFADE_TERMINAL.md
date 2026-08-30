# S2-GR: Statischer Korrekturvertrag fuer operationsgenaue Laufgrenzen

## Auftrag und Grenze

S2-GR schliesst ausschliesslich die Blocker `GQ-B01` bis `GQ-B06`.
Der S2-GJ-Funktionsvertrag, S2-GK, Bilder, Schwellen, Speicherkerne,
Probenrollen und Erfolgskriterien bleiben unveraendert.

S2-GR erlaubt keine Implementierung, keine Tests, keine Imports von
Projektmodulen und keine Rezeptor-, Speicher-, Projektions-, Verbraucher-,
Runner- oder Dateiausfuehrung.

Technischer Ausgangsstand:

`b0892afd6d7130d6e7548ec04fe47a9ccda820e5`

## Verbindliche Vertragsartefakte

| Artefakt | SHA-256 |
| --- | --- |
| `docs/S2GR_OPERATION_REGISTRY.csv` | `8b900da51f6a8921c5231679570f0aa3e188d56b9bd5507f989038a354787d05` |
| `docs/S2GR_FAILURE_OPERATION_REGISTRY.csv` | `f6d201e3c1f5bd91f244a065ef8e97129f39a829c3c50b74b0a697460793c721` |
| `docs/S2GR_ERROR_CODE_REGISTRY.csv` | `a6db907bf9065fd6a7afcf631441c5eda5b8993db01972bb533a8cefa5ac2e09` |
| `docs/S2GR_FAILURE_PATH_BUDGET_REGISTRY.csv` | `fcebc195aeb3ebc51879d9b5eb3657fe59e3f9df6339892ffff1375325597024` |

Diese vier Dateien sind statische Vertragsdaten und kein Runnercode.

## GQ-B01: Operationsgenaue Registry

Die neue Erfolgsregistry enthaelt weiterhin exakt `op-0001..op-0139`.
Jede Zeile bindet nun zusaetzlich:

- `path_role`;
- `owner_id`;
- `reservation_digest`;
- `access_mode`;
- `artifact_type`;
- `target_path`;
- `failure_successor`;
- erforderlichen Vorzustand;
- gueltigen Erfolgsnachzustand;
- maximales Ausgabevolumen.

Alle Zielpfade sind relativ zum exklusiv reservierten neutralen
Laufverzeichnis. `APPEND_JOURNAL` bezeichnet immer genau:

`journal/operations.jsonl`

`CREATE_EXCLUSIVE` erlaubt keine vorhandene Zieldatei, kein Ueberschreiben
und keine Fortsetzung. `READ_BOUND` erlaubt nur die in
`parent_receipts` benannten Eltern. Ein nicht registrierter Lese- oder
Schreibzugriff ist eine Methodenverletzung.

### Owner und Reservierung

Der `run-owner-id` stammt ausschliesslich aus der vorab autorisierten
Run-ID und Run-Autorisierung. Er ist nicht von Bild, History, Fall,
Zielwert oder Ergebnis abgeleitet.

`op-0001` beginnt mit:

```text
owner_id = run-owner-id
reservation_digest = none-unreserved
required_state = UNRESERVED
```

Nach atomar bestaetigter Reservierung entsteht
`run-reservation-digest`. Ab diesem Zeitpunkt bindet jede Erfolgs- und
Fehleroperation exakt denselben Owner und Reservierungsdigest.

Die Registrywerte `owner_id`, `reservation_digest`, `path_role`,
`artifact_type` und `target_path` muessen vor jedem START gegen die
versiegelte Registryzeile geprueft werden. Eine Abweichung stoppt vor dem
fachlichen Aufruf.

## GQ-B02: Vorreservierungsfehler und Fehlerkanten

### Vor der Reservierung

Scheitert `RUN_PREPARE` vor atomar bestaetigter Reservierung, entsteht nur
der begrenzte In-Memory-Status:

`START_BLOCKED`

Dafuer gelten:

- kein Laufverzeichnis;
- kein START- oder RESULT-Ereignis;
- kein `ReservationReceipt`;
- kein `NOT_EVALUABLE`;
- kein Fehler- oder Laufartefakt;
- kein Retry unter derselben Run-ID.

`START_BLOCKED` ist kein Laufzustand und kein fachlicher Befund. Sein
In-Memory-Datensatz ist auf Run-ID, technische Fehlercode-ID und Status
begrenzt und wird nicht als Laufbudget gezaehlt.

### Nach der Reservierung

Sobald die Reservierung bestaetigt ist, gilt `ACTIVE`. Ein weiterer Fehler
in `op-0001` folgt der literal gebundenen Kante
`post-reservation:err-0001`.

Jede Operation `op-0002..op-0139` bindet
`failure_successor=err-0001`. Der Fehleruebergang uebernimmt
ausschliesslich:

- fehlgeschlagene Operations-ID und Phase;
- letzten gueltigen Eventdigest;
- Owner und Reservierungsdigest;
- Digests bereits bestaetigter Praefixartefakte;
- passenden Fehlercode aus der Fehlercode-Registry.

Der Ausgabekandidat der fehlgeschlagenen Operation bleibt privat und wird
nicht im registrierten Zielpfad publiziert. Der Fehlerpfad enthaelt daher nur
das tatsaechlich bestaetigte Erfolgspraefix, das fehlgeschlagene
START-/RESULT-Paar und `err-0001..err-0003`.

Scheitert eine Fehlerabschlussoperation selbst, fuehrt ihr
`failure_successor` zu `HARD_STOP_UNCONFIRMED`. Es gibt keinen Retry und
keine Ersatzpublikation. Das fehlende gueltige Terminalartefakt macht den
Lauf fail-closed nicht auswertbar.

## GQ-B03: Vollstaendige Evaluationstrennung

`EvaluationPlanSeal`, seine Autorisierung und sein Quellpfad sind entfernt
aus:

- `RUN_PREPARE`;
- `ReservationReceipt`;
- `ExecutionPlan`;
- Manifest;
- Ownerableitung;
- Reservierungsdigest;
- allen Operationen `op-0001..op-0131`;
- dem `ExecutionEvidencePackage`.

Die Eltern von `op-0001` lauten nur:

```text
execution-plan + run-authorization
```

Der `EvaluationPlanSeal` bleibt eine externe, unabhaengig versiegelte
read-only Wurzel. Er wird nicht in das Laufverzeichnis kopiert und nicht als
per-run Aufzeichnungsartefakt gezaehlt.

Erst `op-0132 EVALUATION_RUN_BIND` darf lesen:

```text
result:op-0131
+ external-evaluation-plan-seal
```

Die Operation akzeptiert nur:

1. ein vollstaendiges `ExecutionEvidencePackage` mit Zustand
   `EXECUTION_SEALED`;
2. den vor dem Lauf unveraenderten Seal;
3. dessen getrennte Autorisierung;
4. die vorab gebundene Auswerterquelle und das Evaluationsbudget.

Das Ergebnis `EvaluationRunBinding` ist der erste gemeinsame Nachfahre
beider Wurzeln. Vor `op-0132` kann kein Sollwert, keine Fallzuordnung und
keine Entscheidungsregel einen Ausfuehrungsschritt beeinflussen.

## GQ-B04: Terminale Zustandsmaschine

Die einzige zulaessige Zustandsmaschine lautet:

```text
UNRESERVED -> ACTIVE
ACTIVE -> EXECUTION_SEALED -> EVALUATING -> COMPLETING -> COMPLETE

ACTIVE
EXECUTION_SEALED
EVALUATING
COMPLETING
  -> FAILING -> NOT_EVALUABLE
```

Die Zustandsbindungen stehen literal in Erfolgs- und Fehlerregistry.

### Erfolgsweg

- `op-0001 RESULT` erzeugt `ACTIVE`.
- `op-0131 RESULT` erzeugt `EXECUTION_SEALED`.
- `op-0132 RESULT` erzeugt `EVALUATING`.
- `op-0136 RESULT` erzeugt `COMPLETING`.
- `op-0139 RESULT` erzeugt `COMPLETE`.

`op-0138` publiziert nur einen `CompletionCandidate` unter
`evidence/completion-candidate.json`. Dieser ist kein terminaler Status und
kein Abschlussmarker.

Erst `op-0139` darf den Erfolgspfad
`terminal/complete/COMPLETE` exklusiv anlegen.

### Fehlerweg

Der erste technische Fehler nach Reservierung wechselt atomar von einem der
vier nichtterminalen Laufzustaende nach `FAILING`. Danach sind nur noch
`err-0001..err-0003` zulaessig.

Erst `err-0003 RESULT` erzeugt `NOT_EVALUABLE` und legt exklusiv an:

`terminal/failure/NOT_EVALUABLE`

### Exklusivitaet

`CREATE_EXCLUSIVE_TERMINAL` prueft vor Publikation, dass weder der eigene
noch der alternative Terminalpfad existiert. Es darf genau einer der beiden
Pfade entstehen:

```text
terminal/complete/COMPLETE
oder
terminal/failure/NOT_EVALUABLE
```

Nach `COMPLETE` oder `NOT_EVALUABLE` ist jede weitere Erfolgs-, Fehler-,
Evaluations- oder Markeroperation unzulaessig.

Nach dem Wechsel zu `FAILING` sind insbesondere `EVALUATION_RUN_BIND`,
`PURE_EVALUATION`, `FINAL_EVIDENCE_PUBLISH`, `TERMINAL_PUBLISH` und
`COMPLETION_MARKER_PUBLISH` gesperrt.

## GQ-B05: Pfadgueltige Budgets

### Erfolgspfad

Der externe `EvaluationPlanSeal` wird nicht kopiert und ist kein
per-run Artefakt. Gegenueber S2-GP entfallen deshalb 8.192 Bytes.

| Position | Maximum |
| --- | ---: |
| 278 START-/RESULT-Ereignisse | 1.138.688 |
| 57 Rezeptorreceipts | 233.472 |
| 52 Formationreceipts | 212.992 |
| 4 Kontext-read-only Receipts | 65.536 |
| 8 S2-GC-/S2-GI-Receipts | 32.768 |
| MaskedProbeReceipt | 4.096 |
| 7 Armreceipts | 57.344 |
| 4 EvaluationReceipts | 32.768 |
| ExecutionPlan/Manifest | 16.384 |
| ReservationReceipt | 4.096 |
| ExecutionEvidencePackage | 131.072 |
| EvaluationRunBinding | 8.192 |
| FinalEvidencePackage | 65.536 |
| CompletionCandidate | 4.096 |
| CompletionMarker | 2.048 |
| **Erfolgsmaximum** | **2.009.088 Bytes** |

Die Summe entspricht exakt den `output_max_bytes` aller 139
Registryoperationen plus den 278 Eventobergrenzen.

### Fehlerpfade

`docs/S2GR_FAILURE_PATH_BUDGET_REGISTRY.csv` bindet einzeln:

- `fp-0000`: Vorreservierungsstopp ohne Laufartefakt;
- `fp-0001`: Fehler in `op-0001` nach bestaetigter Reservierung;
- `fp-0002..fp-0139`: Fehler in der jeweiligen registrierten Operation.

Fuer `op-0002..op-0139` gilt:

```text
bestaetigte Ausgaben und Events der Operationen vor dem Fehler
+ START/RESULT des fehlgeschlagenen Aufrufs
+ 6 Events der drei Fehlerabschlussoperationen
+ 8.192 Bytes RunFailureReceipt
+ 4.096 Bytes FailureTerminalFinding
+ 2.048 Bytes FailureClosureMarker
```

Der Ausgabekandidat der fehlgeschlagenen Operation wird nicht publiziert und
nicht als Artefakt gezaehlt.

Der groesste zulaessige Fehlerpfad ist `fp-0139`:

```text
1.998.848 Bytes bestaetigtes Praefix bis op-0138
+ 8.192 Bytes fehlgeschlagenes START/RESULT von op-0139
+ 24.576 Bytes Fehleroperationsereignisse
+ 14.336 Bytes Fehlerartefakte
= 2.045.952 Bytes
```

Damit gilt:

```text
MAX_SUCCESS_PATH_BYTES = 2.009.088
MAX_FAILURE_PATH_BYTES = 2.045.952
MAX_RUN_PATH_BYTES     = 2.045.952
```

Die Obergrenze ist das Maximum zulaessiger Einzelpfade, nicht deren Summe.
Kein Fehlerpfad enthaelt den `CompletionMarker`. Kein Erfolgspfad enthaelt
Fehlerartefakte.

### Fehlerabschlussoperationen

Jede Fehleroperation besitzt ein eigenes START-/RESULT-Paar und genau ein
Ausgabeartefakt:

| Operation | Ausgabe | Maximum |
| --- | --- | ---: |
| `err-0001` | RunFailureReceipt | 8.192 |
| `err-0002` | FailureTerminalFinding | 4.096 |
| `err-0003` | FailureClosureMarker | 2.048 |

Mit sechs Ereignissen betraegt der vollstaendige Fehlerabschluss:

`38.912 Bytes`

## GQ-B06: Literale Fehlercode- und Nachrichtenregistry

`docs/S2GR_ERROR_CODE_REGISTRY.csv` enthaelt exakt 16 zulaessige Codes.
Jede Zeile bindet:

- Fehlercode;
- neutrale Message-ID;
- festen ASCII-Nachrichtentext;
- maximale Nachrichtengroesse;
- erlaubte Phase;
- Fehlernachfolger.

Dynamische Fehlermeldungen sind gesperrt. `RunFailureReceipt` speichert nur
den registrierten Code und die registrierte Message-ID. Der Text darf nur
byteidentisch aus der Registry aufgeloest werden.

Kein Text enthaelt History-, Bild-, Arm-, Fall-, Zielwert- oder
Evaluationsinhalt. Variablenwerte stehen ausschliesslich in typisierten
neutralen Digest- und ID-Feldern des Fehlerbelegs.

`E001` ist ausschliesslich fuer den In-Memory-Status `START_BLOCKED`
zulaessig. `E002..E016` fuehren nach bestaetigter Reservierung
ausschliesslich zu `err-0001`.

## Vorwaertsgerichteter Gesamtgraph

```text
ExecutionPlan + RunAuthorization
-> ReservationReceipt
-> op-0002..op-0130
-> ExecutionEvidencePackage

External EvaluationPlanSeal           [keine fruehe Kante]
ExecutionEvidencePackage + External EvaluationPlanSeal
-> EvaluationRunBinding
-> EvaluationReceipts
-> FinalEvidencePackage
-> CompletionCandidate
-> CompletionMarker
-> COMPLETE
```

Fehlerzweig:

```text
bestaetigtes Erfolgspraefix
+ fehlgeschlagene Operation
-> FAILING
-> RunFailureReceipt
-> FailureTerminalFinding
-> FailureClosureMarker
-> NOT_EVALUABLE
```

Der Fehlerzweig besitzt keine Kante zurueck in den Erfolgsgraphen. Der
Erfolgsgraph besitzt nach `COMPLETE` keine ausgehende Kante.

## Falsifikation und Stopp

S2-GR ist verletzt bei:

- einer fehlenden oder abweichenden Registryzeile;
- einer dynamischen Operation oder Fehlernachricht;
- einem nicht registrierten Pfad, Artefakttyp oder Zugriff;
- einem Owner- oder Reservierungswechsel;
- einem Evaluationseinfluss vor `op-0132`;
- einem Start ausserhalb des erforderlichen Zustands;
- gleichzeitigem Erfolgs- und Fehlerterminalpfad;
- einem Fehlerpfad ausserhalb seiner Budgetzeile;
- einer Bytezahl ueber `2.045.952`;
- einer Operation nach terminalem Zustand.

Jede Verletzung vor Reservierung ergibt nur `START_BLOCKED`. Jede Verletzung
nach Reservierung ergibt, soweit der gebundene Fehlerabschluss selbst
publizierbar bleibt, `NOT_EVALUABLE`. Sie erzeugt keinen negativen
Memory-Funktionsbefund.

## Vertragsentscheidung

S2-GR schliesst `GQ-B01` bis `GQ-B06` auf statischer Vertragsebene.
Operationsgenaue Pfad-, Owner-, Reservierungs-, Zugriffs-, Artefakt- und
Fehlerkanten, die Evaluationstrennung, terminale Exklusivitaet sowie getrennte
Pfadbudgets sind materialisiert.

Status:

`PASS_S2GR_STATIC_OPERATION_PATH_OWNER_AND_TERMINAL_CORRECTION_BOUND`

Fixtures, Runner, Recorder, Verifikator, Tests und Ausfuehrung bleiben
gesperrt. Vor Implementierung ist ein separater statischer
Materialisierungs-, Nichtzirkularitaets- und Budgetaudit erforderlich.
