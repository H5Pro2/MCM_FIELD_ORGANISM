# S2-GN: Korrekturvertrag fuer Probenrollen, Provenienz und Laufanatomie

## Auftrag und Grenze

S2-GN schliesst ausschliesslich die statischen Blocker `GM-B01` bis `GM-B05`.
Der Vertrag trennt Kontextabruf und Kontextverbrauch, neutralisiert die
Speicherprovenienz und bindet die noch fehlenden Lauf- und Digestformen.

S2-GN erlaubt keine Implementierung, keinen Import neuer Projektmodule, keine
Tests und keine Rezeptor-, Speicher-, Kontext- oder Runnerausfuehrung.
S2-GK, B4, TSPM-1, PPB-1, die 25 S2-GL-Bilder, alle Schwellen und die
S2-GJ-Erfolgskriterien bleiben unveraendert.

Technischer Ausgangsstand:

`dd783118ea2b8a624f17826fa462da3d49f34808`

## Verbindliche Rollentrennung

### Vollstaendige Kontextabrufproben

Jede der vier frischen Bildungsgeschichten erhaelt nach Schritt 13 genau eine
eigene volle read-only Speicherprobe:

| neutrale History | Bildungsschritte 1..13 | volle Kontextabrufprobe |
| --- | --- | --- |
| `h01` | `J1-T` viermal, danach `D1..D9` | `J1-T/Q0` |
| `h02` | `J1-F` viermal, danach `D1..D9` | `J1-F/Q0` |
| `h03` | `J1-C` viermal, danach `D1..D9` | `J1-C/Q0` |
| `h04` | `A1..A13` jeweils einmal | `J1-T/Q0` |

Die Vollproben dienen ausschliesslich dazu, aus dem jeweiligen bereits
gebildeten Speicherzustand einen read-only S2-FS-Befund und daraus S2-GC-
sowie S2-GI-Bundles zu erzeugen. Sie duerfen weder S2-GK noch den Auswerter
erreichen.

Der Auswerter darf auch kein Vollprobenreceipt oder dessen Payload erhalten.
Ein ExecutionEvidence-Digest darf spaeter nur als Provenienzreferenz an das
EvaluationReceipt angehaengt werden; der reine Auswerter selbst verarbeitet
ausschliesslich die erforderlichen Armreceipts und die getrennte
Zielwertfixture.

Die Historytabelle besitzt keine Funktionsrolle. Erst eine getrennte
Auswerterfixture ordnet spaeter zu:

```text
h01 -> K_CORRECT
h02 -> K_FOREIGN
h03 -> K_CONFLICT
h04 -> K_ABSENT
```

Diese Zuordnung ist kein Bestandteil von Rezeptor-, Speicher-, Bundle- oder
Verbrauchereingaben.

### Gemeinsame maskierte Verbraucherprobe

Nach Abschluss aller vier Kontextabrufe wird genau ein weiteres, unabhaengiges
`J1-T/Q0`-Bild real durch den visuellen Rezeptor analysiert. Aus diesem
Rezeptorbeleg wird eine private Teilprobe gebildet:

```text
VISIBLE = (0, 2, 4, 6, 8, 10, 12, 14, 16)
MASKED  = (1, 3, 5, 7, 9, 11, 13, 15, 17)
Marker  = None
```

Alle sieben S2-GJ-Arme erhalten exakt denselben Maskenprobenbeleg. Die vier
Vollproben sind keine Eltern dieses Belegs. Der Maskenmarker wird erst nach
der realen Rezeptoranalyse eingesetzt und erreicht weder Rezeptor noch
Speicher.

Der S2-GK-Verbraucher erhaelt damit nur:

1. die gemeinsame maskierte aktuelle Probe;
2. genau ein bereits bereitgestelltes A/B-Bundle;
3. die literal benannte Rolle `B_STABLE`.

Er waehlt keinen Kontext aus der Teilwahrnehmung aus.

## Korrektur der Schwellenbeziehung

Die Bilder und Schwellen bleiben unveraendert. Die zuvor widerspruechliche
Forderung, `J1-T` und `J1-C` muessten ueber jede Matchgrenze getrennt sein,
wird fuer diese Aufgabe ersetzt durch eine exakte Rollenbindung:

- `h01`, `h02` und `h03` werden jeweils mit ihrer eigenen Vollprobe im
  Abstand `0` abgerufen;
- `h04` besitzt keinen stabilen Kandidaten und bleibt bei der `J1-T`-Vollprobe
  `ABSENT_VALID`;
- erst der Verbraucher vergleicht die sichtbaren Werte der gemeinsamen
  maskierten `J1-T`-Probe exakt mit dem bereits bereitgestellten Kandidaten;
- `J1-C` widerspricht dabei sichtbar, ohne dass eine Matchschwelle angepasst
  oder eine automatische Kontextauswahl eingefuehrt wird;
- `J1-F` bleibt auf den sichtbaren Positionen ununterscheidbar und darf daher
  technisch zu einer Fremdvervollstaendigung fuehren.

Alle D-/A-Abstaende aus S2-GL bleiben verbindlich. Kein Distraktor oder
`K_ABSENT`-Schritt darf einen unbeabsichtigten Fast- oder Slow-Match erzeugen.

## Neutrale technische Provenienz

In allen Artefakten vor der reinen Auswertung sind ausschliesslich folgende
neutralen Rollen zulaessig:

```text
History:       h01, h02, h03, h04
Operation:     op-0001 bis op-0136
Kontextbundle: c01, c02, c03, c04
Arm:           a01 bis a07
Auswertung:    e01 bis e04
```

Vor der Auswertung gesperrt sind insbesondere die Zeichenketten:

```text
CORRECT
FOREIGN
CONFLICT
ABSENT
GJ-01 bis GJ-07
Erfolg, Sollstatus oder erwartetes Ergebnis
```

Bild-IDs wie `J1-T`, `D1` oder `A1` bezeichnen ausschliesslich literal
gebundene Quellbytes. Sie sind keine Sollentscheidung. Distanz, Slotwahl,
Support und Abruf duerfen nur aus den AV-Werten und unveraenderten
Speicherregeln entstehen.

Die neutrale Quellen-ID lautet:

```text
s2gn.h<nn>.source.<mmm>
```

Sie bindet nur Historynummer, lokale Quellenordinalzahl, Zeitfenster,
Bilddigest, auditive Maske und Konfiguration. Die semantische Fallzuordnung
liegt ausschliesslich in der getrennten Auswerterfixture.

## Zwei getrennte Planwurzeln

Damit Sollwerte keine frueheren Artefakte beeinflussen, besitzt der spaetere
Lauf zwei voneinander unabhaengige, vorab versiegelte Wurzeln.

### `ExecutionPlan`

Unveraenderliche Felder:

```text
schema
run_id
source_inventory_digest
configuration_digest
fixture_set_digest
history_plan_digest
operation_plan_digest
resource_budget_digest
allowed_entrypoint_digest
execution_plan_digest
```

Der ExecutionPlan enthaelt neutrale Histories, Quellen, Zeitfenster,
Operationen und Budgets. Er enthaelt keine Fallzuordnung, Zielwertfixture,
Erfolgserwartung oder Evaluatorentscheidung.

### `EvaluationPlanSeal`

Unveraenderliche Felder:

```text
schema
evaluation_plan_id
case_mapping_digest
target_fixture_digest
decision_rules_digest
evaluator_source_digest
evaluation_plan_digest
seal_digest
```

Der versiegelte Evaluationsplan wird vor dem Lauf digestgebunden, ist aber
kein Elternartefakt von ExecutionPlan, Rezeptorbelegen, Speicherzustaenden,
Kontextbundles oder Armreceipts. Er wird erst nach Abschluss aller sieben
Armresultate zusammen mit dem reinen Auswerter geoeffnet.

Beide Wurzeln treffen erstmals im `EvaluationReceipt` zusammen. Damit bleibt
die Vorregistrierung erhalten, ohne Sollwerte in den Funktionspfad zu geben.

## Vollstaendige Operationsanatomie

### Top-Level-Operationen

Die unabhaengige Verbraucherprobe und die expliziten Laufgrenzen korrigieren
den S2-GL-Umfang von `131/262` auf:

| Operationsklasse | Anzahl |
| --- | ---: |
| `RUN_PREPARE` | `1` |
| `FORMATION_RECEPTOR_ANALYSIS` | `52` |
| `COMPOSITE_FORMATION` | `52` |
| `CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS` | `4` |
| `COMPOSITE_READ_ONLY_PROBE` | `4` |
| `CONSUMER_RECEPTOR_ANALYSIS` | `1` |
| `MASKED_PROBE_BIND` | `1` |
| `S2GC_PROJECTION` | `4` |
| `S2GI_PROJECTION` | `4` |
| `ARM_EXECUTION` | `7` |
| `EXECUTION_EVIDENCE_SEAL` | `1` |
| `PURE_EVALUATION` | `4` |
| `RUN_FINALIZE` | `1` |
| **gesamt** | **`136`** |

Jede Operation besitzt genau ein `START`- und ein `RESULT`-Ereignis. Der
neue vollstaendige Umfang lautet daher:

```text
136 Operationen
272 START-/RESULT-Ereignisse
```

`131/262` ist hiermit ersetzt und darf fuer S2-GN nicht weiterverwendet
werden.

### Gebundene Hilfsarbeit je Operationsklasse

Keine der folgenden Arbeiten erzeugt ein zusaetzliches Top-Level-Ereignis.
Sie ist atomarer Bestandteil genau einer benannten Operation:

| Top-Level-Operation | gebundene Hilfsarbeit |
| --- | --- |
| `RUN_PREPARE` | Quellinventar, Konfiguration, vier frische Vorzustaende, ExecutionPlan-Pruefung, Einmalgate |
| `FORMATION_RECEPTOR_ANALYSIS` | Bildkonstruktion, Rohbytedigest, Rezeptoranalyse, Rezeptorzustandsbeleg |
| `COMPOSITE_FORMATION` | Zeit-/Envelopebindung, S2-FS-Eingang, Owner/Autorisierung, atomarer Schritt, Receiptpruefung |
| `CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS` | kontextspezifisches Vollbild, Rohbytedigest, volle Rezeptorquelle |
| `COMPOSITE_READ_ONLY_PROBE` | Probenhuelle, native read-only Probe, Fast-/Slow-Trennung, Zustandsunveraendertheit |
| `CONSUMER_RECEPTOR_ANALYSIS` | unabhaengiges `J1-T`-Bild, Rezeptorbeleg, keine Speicherbindung |
| `MASKED_PROBE_BIND` | neun sichtbare Werte, neun Marker, Herkunfts- und Maskendigest |
| `S2GC_PROJECTION` | Projektionsbindung, `NOT_REQUESTED`-Sequenzevidenz, Drei-Rollen-Bundle |
| `S2GI_PROJECTION` | reine A/B-Schattenprojektion und Ledgerpruefung |
| `ARM_EXECUTION` | S2-GK-Kontextbindung oder Direktbaselinebindung, read-only Aufruf, Armreceipt |
| `EXECUTION_EVIDENCE_SEAL` | Vollstaendigkeitspruefung aller Armreceipts und unveraenderliches ExecutionEvidencePackage |
| `PURE_EVALUATION` | Oeffnen des EvaluationPlanSeal, Zielfixture, reine Fallauswertung, EvaluationReceipt |
| `RUN_FINALIZE` | FinalEvidence, Terminalbefund, Abschlussmarker, atomare Publikationspruefung |

Jede spaetere Implementierung muss diese Zuordnung literal abbilden. Eine
Hilfsarbeit ausserhalb ihrer Operationsklasse oder ein zusaetzliches
unprotokolliertes Projektfunktionsereignis macht den Lauf `NOT_EVALUABLE`.

## Konkrete unveraenderliche Datenformen

### `OperationStart`

```text
schema
run_id
operation_id
operation_index
operation_class
execution_plan_digest
previous_event_digest
input_receipt_digests
source_digest
start_digest
```

### `OperationResult`

```text
schema
run_id
operation_id
operation_index
operation_class
execution_plan_digest
start_digest
previous_event_digest
status
output_receipt_digest
resource_ledger_digest
error_code
result_digest
```

`OperationResult.previous_event_digest` ist der zugehoerige `start_digest`.
Der naechste START verweist auf den vorherigen `result_digest`. Kein Ereignis
verweist auf ein spaeteres Artefakt.

### `MaskedProbeReceipt`

```text
schema
consumer_receptor_result_digest
consumer_receptor_source_digest
visual_geometry_id
visible_positions
masked_positions
visible_values_digest
mask_marker_role
masked_probe_digest
receipt_digest
```

Der Beleg enthaelt keine maskierten Zielwerte und keinen Kontextabrufdigest.

### `ArmReceipt`

```text
schema
arm_id
method
masked_probe_receipt_digest
context_projection_digest oder None
context_prestate_digest oder None
context_poststate_digest oder None
result_digest
resource_ledger_digest
receipt_digest
```

Ein Armreceipt enthaelt keine Fallrolle, kein Ziel und keine Sollentscheidung.

### `EvaluationReceipt`

```text
schema
evaluation_id
execution_evidence_digest
evaluation_plan_seal_digest
consumed_arm_receipt_digests
evaluation_result_digest
receipt_digest
```

### `ExecutionEvidencePackage`

```text
schema
run_id
execution_plan_digest
final_pre_evaluation_event_digest
receptor_receipt_digests
formation_receipt_digests
context_read_receipt_digests
projection_receipt_digests
masked_probe_receipt_digest
arm_receipt_digests
operation_counts
resource_totals_digest
execution_evidence_digest
```

### `FinalEvidencePackage`

```text
schema
run_id
execution_evidence_digest
evaluation_plan_seal_digest
evaluation_receipt_digests
finalize_start_digest
complete_counts
final_evidence_digest
```

### `TerminalFinding`

```text
schema
run_id
status
final_evidence_digest
final_operation_result_digest
recorded_operation_count
recorded_event_count
error_code oder None
terminal_digest
```

Zulaessige Statuswerte sind `RECORDING_COMPLETE` und `NOT_EVALUABLE`.
Ein fachlich falsches Ergebnis bleibt bei vollstaendiger Aufzeichnung
`RECORDING_COMPLETE`; die fachliche Entscheidung steht nur in den getrennten
EvaluationReceipts.

### `CompletionMarker`

```text
schema
run_id
terminal_digest
final_evidence_digest
final_operation_result_digest
marker_digest
```

Der Marker besitzt keine Memory- oder Erfolgsentscheidung. Er belegt nur den
vollstaendigen Abschluss der Aufzeichnung.

## Vorwaertsgerichteter Digestgraph

Der Graph besitzt ausschliesslich folgende Richtung:

```text
Bildbytes
-> Rezeptorreceipt
-> Formationreceipt
-> Composite-Zustand
-> Kontext-read-only Receipt
-> S2-GC-Bundle
-> S2-GI-Projektion

unabhaengige Verbraucherbildbytes
-> Verbraucher-Rezeptorreceipt
-> MaskedProbeReceipt

S2-GI-Projektion + MaskedProbeReceipt
-> ArmReceipt
-> ExecutionEvidencePackage
-> EXECUTION_EVIDENCE_SEAL_RESULT

EvaluationPlanSeal + erforderliche ArmReceipts
-> reines EvaluationResult

EvaluationResult + ExecutionEvidence-Digest
-> EvaluationReceipt
-> FinalEvidencePackage
-> RUN_FINALIZE_RESULT
-> TerminalFinding
-> CompletionMarker
```

Ein Ergebnis-, Terminal- oder Markerdigest darf in keiner frueheren Form
stehen. Der EvaluationPlanSeal darf erst ab `PURE_EVALUATION` konsumiert
werden. Ein Receipt darf niemals seinen eigenen Digest oder den Digest eines
Nachfahren in seinem Payload fuehren.

## Korrigierte Ressourcen- und Vergleichsbudgets

### Rezeptor und Speicher

Die unabhaengige Verbraucherprobe erhoeht nur den Rezeptorumfang:

```text
57 reale Bildanalysen
57 * 28.800 = 1.641.600 analysierte Rohbytes
57 * 26 = 1.482 gebundene AV-Werte
```

Rohbilder werden nicht im Speicherzustand gehalten. Die 52 Composite-
Bildungen und vier Composite-read-only Proben bleiben unveraendert:

| Rolle | Write-Woerter | Distanzterme | Kontrollterme |
| --- | ---: | ---: | ---: |
| 52 Formationen | `32.084` | `24.336` | `2.808` |
| 4 read-only Proben | `56` | `1.872` | `192` |
| **gesamt** | **`32.140`** | **`26.208`** | **`3.000`** |

S2-GC-, S2-GI- und S2-GK-Ledger bleiben exakt wie in S2-GL. Die neue
Rollentrennung aendert keine Kandidaten-, Komponenten-, Werte- oder
Vergleichsgrenze.

### Verbraucher und Direktbaseline

Die sieben Armresultate behalten gemeinsam:

```text
126 Maskenvalidierungen
45 sichtbare Wertevergleiche
36 Maskenuebernahmen
6 Bereichszugriffe
5 Kandidatenreferenzen
99 Wertereferenzen
14 Digestoperationen
```

`GJ-02/GJ-03` und `GJ-04/GJ-05` erhalten jeweils denselben
MaskedProbeReceipt- und S2-GI-Projektionsdigest. Verbraucher und
Direktbaseline bleiben dadurch funktional budgetgleich.

### Aufzeichnungsartefakte

Der Lauf bindet genau:

```text
272 Ereignisartefakte
57 Rezeptorreceipts
52 Formationreceipts
4 Kontext-read-only Receipts
4 S2-GC-Projektionsreceipts
4 S2-GI-Projektionsreceipts
1 MaskedProbeReceipt
7 Armreceipts
4 EvaluationReceipts
1 ExecutionPlan
1 EvaluationPlanSeal
1 ExecutionEvidencePackage
1 FinalEvidencePackage
1 TerminalFinding
1 CompletionMarker
```

Jedes Artefakt besitzt genau einen kanonischen SHA-256-Digest. Native
Funktionsdigests und die 272 Eventdigests werden in getrennten Ledgerrollen
gezaehlt; sie duerfen nicht als kostenlose Aufzeichnungsarbeit erscheinen.

Alle Formen werden als kanonisches ASCII-JSON ohne Rohbildbytes gespeichert.
Die folgenden harten Groessenobergrenzen gelten einschliesslich Feldnamen und
Trennzeichen:

| Artefakt | Anzahl | Maximum je Artefakt |
| --- | ---: | ---: |
| START/RESULT | `272` | `4.096` Bytes |
| Rezeptorreceipt | `57` | `4.096` Bytes |
| Formationreceipt | `52` | `4.096` Bytes |
| Kontext-read-only Receipt | `4` | `16.384` Bytes |
| S2-GC-/S2-GI-Receipt | `8` | `4.096` Bytes |
| MaskedProbeReceipt | `1` | `4.096` Bytes |
| Armreceipt | `7` | `8.192` Bytes |
| EvaluationReceipt | `4` | `8.192` Bytes |
| ExecutionPlan | `1` | `16.384` Bytes |
| EvaluationPlanSeal | `1` | `8.192` Bytes |
| ExecutionEvidencePackage | `1` | `131.072` Bytes |
| FinalEvidencePackage | `1` | `65.536` Bytes |
| TerminalFinding | `1` | `4.096` Bytes |
| CompletionMarker | `1` | `2.048` Bytes |

Die maximale kanonische Aufzeichnungsmenge betraegt damit `1.980.416` Bytes.
Ein groesseres Artefakt stoppt vor seiner Publikation. Prozess-RAM und
Laufzeit werden spaeter separat gemessen und nicht mit diesem
Aufzeichnungsbudget vermischt.

## Fail-Closed-Regeln

Vor dem ersten Speicheraufruf wird gestoppt bei:

- einer Fallrolle in ExecutionPlan, History-, Quellen- oder Operations-ID;
- einer Vollprobe, die nicht zur jeweiligen neutralen History gehoert;
- einem nicht frischen History-Vorzustand;
- einem Maskenmarker im Rezeptor- oder Speichereingang;
- einem Zielwert- oder EvaluationPlan-Bezug in einem fruehen Artefakt;
- einem unbekannten, rueckwaertsgerichteten oder zyklischen Digestbezug;
- einer nicht klassifizierten Hilfsarbeit.

Waehrend einer spaeteren Ausfuehrung fuehren abweichende Operationszahlen,
fehlende Receipts, Teilaufzeichnungen oder Digestbrueche zu `NOT_EVALUABLE`.
Sie erzeugen keinen negativen Memory-Befund und erlauben keinen Retry.

## Korrekturentscheidung

S2-GN schliesst die statischen Rollenfehler und ersetzt den unvollstaendigen
S2-GL-Laufumfang. Die Kontext-Vollproben werden von der gemeinsamen
maskierten Verbraucherprobe getrennt. Neutrale technische Provenienz,
Hilfsarbeitszuordnung, unveraenderliche Artefaktformen und der
vorwaertsgerichtete Digestgraph sind gebunden.

Status:

`PASS_S2GN_STATIC_PROBE_ROLE_PROVENANCE_AND_RUN_ANATOMY_CORRECTION_BOUND`

Die Implementierung bleibt gesperrt. Vor Fixture-, Runner- oder Recordercode
ist ein enger statischer Materialisierungs-, Nichtzirkularitaets- und
Budgetaudit gegen S2-GN erforderlich.
