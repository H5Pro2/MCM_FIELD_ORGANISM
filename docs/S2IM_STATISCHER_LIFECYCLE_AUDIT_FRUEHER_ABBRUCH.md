# S2-IM: Statischer Lifecycle-Audit des fruehen Abbruchs

## Status

`S2IM_STATIC_LIFECYCLE_AUDIT_COMPLETE_CORRECTION_REQUIRED`

S2-IM verfolgt ausschliesslich den in S2-IL fehlgeschlagenen Test 21 und
bindet die kleinste zulaessige Lifecycle-Korrektur. Es wurden keine
Produktiv- oder Testdateien geaendert, keine Module importiert, keine Tests
ausgefuehrt und keine Lauf- oder Memory-Funktion aufgerufen.

Der reale Fuenf-Status-Funktionslauf bleibt gesperrt. S2-IL bleibt
`QUALIFICATION_FAILED_FAILURE_ARTIFACT_PROVENANCE`.

## Exakte Ist-Spur von Test 21

Der relevante Test ruft nach Materialisierung von Plan und Registry auf:

```text
AppendOnlyRunRecorder.reserve(...)
reserved.fail("IG-E002", "ie-op-002")
verify_run_read_only(...)
```

Die aktuelle Implementierung durchlaeuft dabei diese Schritte:

| Schritt | Ist-Zustand |
| --- | --- |
| 1 | `reserve()` validiert den absoluten Ausgabepfad. |
| 2 | Das finale Laufverzeichnis wird exklusiv angelegt. |
| 3 | Die Unterverzeichnisse und das Journal werden angelegt. |
| 4 | `ie-op-001 RUN_PREPARE` schreibt START und RESULT. |
| 5 | `reservation.json` wird als Artefakt von `ie-op-001` publiziert. |
| 6 | Der Recorder steht auf `ACTIVE`; die aktuelle Operation ist `ie-op-002 SOURCE_MANIFEST`. |
| 7 | Test 21 loest `fail(..., "ie-op-002")` aus. |
| 8 | `ie-op-002` erhaelt START und ein fehlgeschlagenes RESULT, aber kein `manifest.json`. |
| 9 | Zwei Fehlerabschlussoperationen erzeugen `failure/receipt.json` und `terminal/failure/NOT_EVALUABLE`. |
| 10 | Der Verifikator findet `reservation.json`, aber kein `manifest.json`. |

Der Abbruch liegt damit **nach** der aktuell als erfolgreich behandelten
Reservierung und **vor** der Manifestpublikation. Er ist kein
Vorreservierungsfehler.

Der aktuelle Verifikator klassifiziert den Pfad terminal als
`NOT_EVALUABLE`, fuegt aber korrekt den Fehler
`reservation or manifest is unreadable` hinzu. Genau diese zusaetzliche
Fehlermeldung hat Test 21 gestoppt.

## Zusaetzliche reale Eintrittsstelle

Der Hauptlaeufer ruft nach Rueckgabe von `reserve()` zunaechst `_runtime()`
und erst danach `_execute()` auf. Das Manifest wird am Anfang von
`_execute()` als `ie-op-002` geschrieben. Ein Runtimefehler kann somit
aktuell dieselbe ungueltige Zwischenphase treffen:

```text
reservation vorhanden
+ Zustand ACTIVE
+ manifest fehlt
```

Ein bloss toleranterer Verifikator oder ein nachtraeglich erzeugtes Manifest
waere deshalb methodisch falsch.

## Verbindliche Lifecycle-Grenze

Die Korrektur muss exakt zwei Startausgaenge besitzen.

### 1. Vor atomarem Reservierungsabschluss

```text
UNRESERVED -> START_REJECTED
```

`START_REJECTED` gilt, wenn irgendein Teil der Bootstrap-Vorbereitung oder
der gemeinsamen Publikation von Reservierung und Manifest scheitert.

Verbindlich:

- kein durch diesen Startversuch neu publiziertes finales Laufverzeichnis;
- kein regulaeres Laufjournal;
- kein `ReservationReceipt` im finalen Pfad;
- kein `SourceManifestReceipt` im finalen Pfad;
- kein `NOT_EVALUABLE` und kein `COMPLETE`;
- kein erneuter Verbrauch derselben Run-ID;
- nur ein begrenzter unveraenderlicher In-Memory-Befund.

Die bisherige Bezeichnung `START_BLOCKED` wird fuer diese Grenze durch
`START_REJECTED` ersetzt. Ein eventuell technisch zur Vorbereitung
verwendeter Stagingpfad ist kein Laufpfad und darf vom Laufverifikator nicht
als Lauf akzeptiert werden.

### 2. Nach atomarem Reservierungsabschluss

```text
UNRESERVED
-> BOOTSTRAP_STAGED
-> ACTIVE
```

`ACTIVE` darf erst nach gemeinsamer und vollstaendiger Publikation von
folgenden Elementen sichtbar werden:

1. `ie-op-001` START;
2. `reservation.json`;
3. `ie-op-001` RESULT;
4. `ie-op-002` START;
5. `manifest.json`;
6. `ie-op-002` RESULT.

Der Recorder darf erst mit `next_operation_index = 3`, vier Ereignissen und
den beiden vorhandenen Artefaktdigests an den Runner zurueckgegeben werden.
Damit ist `ie-op-003` die erste regulaere Operation, die nach erfolgreicher
Reservierung fehlschlagen darf.

Jeder Fehler ab `ie-op-003` fuehrt ueber den vorhandenen Fehlerabschluss zu:

```text
ACTIVE/EXECUTION_SEALED/EVALUATING/COMPLETING
-> FAILING
-> NOT_EVALUABLE
```

Ein gueltiger `NOT_EVALUABLE`-Pfad enthaelt daher zwingend eine lesbare,
kanonische und gegenseitig gebundene Reservierung und ein Manifest.

## Atomare Publikationsgrenze

Die Bootstrap-Artefakte und ihre Ereignisse werden vor der Sichtbarkeit des
finalen Laufpfads vollstaendig materialisiert. Die zulaessige enge
Implementierungsform lautet:

```text
output_root/.s2im-bootstrap/<run_id>.<plan-prefix>.pending
  reservation.json
  manifest.json
  journal/operations.jsonl

-- exklusive Publikation ohne Ueberschreiben -->

output_root/<run_id>/
```

Der Stagingname wird nur aus validierter Run-ID und Plan-Digest abgeleitet.
Er enthaelt keine Fall-, Ziel- oder Ergebnisinformation. Erst die exklusive
Publikation auf `output_root/<run_id>` bestaetigt die Reservierung. Scheitert
ein vorheriger Schritt, entsteht `START_REJECTED`; ein Stagingrest ist kein
Lauf und darf weder fortgesetzt noch verifiziert werden.

Diese Grenze verhindert eine nachtraegliche Rekonstruktion. Ein fehlendes
Manifest kann nach dem Wechsel zu `ACTIVE` nicht nachgeliefert werden.

## Gebundene Datenformen

### `StartRejectedV1`

Reiner In-Memory-Befund, maximal `768` kanonische ASCII-Bytes:

```text
schema                  = s2im.start-rejected.v1
status                  = START_REJECTED
run_id                  = validierte Run-ID
owner_id                = Owner aus ExecutionPlan
plan_digest             = Digest des vorab validierten ExecutionPlan
target_path_role        = RUN_DIRECTORY
target_preexisted       = boolescher Preflightbefund
publication_performed   = false
error_code              = registrierter Start-/Publikationsfehler
reservation_digest      = null
event_count             = 0
artifact_count          = 0
start_rejected_digest   = Digest aller vorstehenden Felder
```

Der Befund besitzt keinen von diesem Versuch autorisierten Laufpfad und ist
kein Bestandteil eines Laufbudgets. Bei einer bereits vorhandenen
Zielverzeichniskollision bleibt dieses fremde oder fruehere Verzeichnis
unangetastet und wird nicht als Ergebnis des neuen Startversuchs gelesen.

### `ReservationReceiptV1`

Pfad: `reservation.json`

Operation: `ie-op-001 RUN_PREPARE`

Artefaktgrenze: `1.536` Byte

Der bestehende Reservation-Core bleibt erhalten:

```text
schema
run_id
owner_id
plan_digest
registry_bundle_digest
state = ACTIVE
```

`reservation_digest` ist SHA-256 ueber exakt diesen Core ohne
Selbst-Digest. Die gespeicherte Huelle bindet zusaetzlich:

```text
operation_id = ie-op-001
owner_id
reservation_digest
start_event_digest
artifact.result = Reservation-Core + reservation_digest
```

### `SourceManifestReceiptV1`

Pfad: `manifest.json`

Operation: `ie-op-002 SOURCE_MANIFEST`

Artefaktgrenze: `3.584` Byte

Das Manifest bindet mindestens und ohne Auswertungsziel:

```text
schema = s2ig.source-manifest.v1
execution_plan = vollstaendiger ExecutionPlan-Payload
registry_bundle_digest
execution_fixture_digest
context_role = CONTEXT_RETRIEVAL_PROBE
signal_role = MASKED_SIGNAL_PROBE
evaluation_plan_digest = null
```

Die gespeicherte Huelle bindet `ie-op-002`, denselben Owner und
Reservierungsdigest, den START-Eventdigest und den Manifest-Payload. Der
START von `ie-op-002` bindet den Artefaktdigest von `ie-op-001` als einzigen
internen Elternbeleg.

### Gueltiger frueher Fehlerabschluss

Nach bestaetigtem Bootstrap bleibt die vorhandene Form erhalten:

- fehlgeschlagene Operation: ein START-/RESULT-Paar, kein Ergebnisartefakt;
- `failure/receipt.json`: maximal `1.024` Byte;
- `terminal/failure/NOT_EVALUABLE`: maximal `1.024` Byte;
- alle Ereignisse: jeweils maximal `1.536` Byte;
- Owner und Reservierungsdigest identisch mit Bootstrap;
- `partial_state_digest` bindet mindestens die bestaetigten Digests von
  `ie-op-001`, `ie-op-002` und den letzten gueltigen Eventdigest.

## Digestreihenfolge

Die verbindliche Reihenfolge ist azyklisch:

```text
ExecutionPlan
-> plan_digest
-> Reservation-Core
-> reservation_digest
-> ie-op-001 START
-> ReservationReceipt artifact_digest
-> ie-op-001 RESULT
-> ie-op-002 START
-> SourceManifestReceipt artifact_digest
-> ie-op-002 RESULT
-> atomarer ACTIVE-Commit
-> spaetere Operation oder Fehlerabschluss
```

Kein Bootstrap-Digest haengt von einem spaeteren Fehler-, Terminal- oder
Evaluationsergebnis ab.

## Pfad- und Ownerbindung

| Rolle | Pfad | Owner | Zugriff |
| --- | --- | --- | --- |
| Bootstrap-Staging | `.s2im-bootstrap/<run_id>.<plan-prefix>.pending` | ExecutionPlan-Owner | exklusiv, niemals Lauflesepfad |
| Finaler Lauf | `<output_root>/<run_id>` | ExecutionPlan-Owner | exklusive einmalige Publikation |
| Reservierung | `reservation.json` | derselbe Owner | create-exclusive |
| Manifest | `manifest.json` | derselbe Owner | create-exclusive |
| Journal | `journal/operations.jsonl` | derselbe Owner | append-only |
| Fehlerbeleg | `failure/receipt.json` | derselbe Owner | create-exclusive |
| Fehlerterminal | `terminal/failure/NOT_EVALUABLE` | derselbe Owner | create-exclusive-terminal |
| Erfolgsterminal | `terminal/complete/COMPLETE` | derselbe Owner | create-exclusive-terminal |

Owner, Run-ID, Plan-Digest und Registry-Digest werden vor der
Bootstrap-Publikation gebunden. Kein Wert wird aus einem spaeteren Artefakt
rekonstruiert.

## Groessen- und Ereignisgrenzen

Die bestehende Registry und die globalen Budgets bleiben unveraendert.

Atomarer Bootstrap-Worst-Case:

```text
4 Ereignisse * 1.536
+ ReservationReceipt 1.536
+ SourceManifestReceipt 3.584
= 11.264 Byte
```

Kleinster gueltiger post-reservation Fehlerpfad bei `ie-op-003`:

```text
Bootstrap                         11.264
+ fehlerhaftes START/RESULT        3.072
+ vier Fehlerabschlussereignisse   6.144
+ zwei Fehlerartefakte             2.048
= 22.528 Byte
```

Dieser Pfad besitzt zehn Ereignisse. Er liegt innerhalb der bestehenden
Fehlerpfadgrenzen. Das maximale Gesamtbudget aendert sich nicht, weil dessen
Maximum weiterhin aus einem spaeteren Registryfehler stammt.

`START_REJECTED` erzeugt null Laufereignisse und null Laufartefaktbytes.

## Verifikatorentscheidung

Der read-only Verifikator muss zwei typisierte Eingangsformen unterscheiden:

### `StartRejectedV1`

- Form und Digest gueltig;
- kein finaler Laufpfad wurde durch diesen Startversuch publiziert;
- ein bereits vor dem Versuch vorhandener Zielpfad bleibt fremd und wird
  nicht als Lauf dieses Befunds verifiziert;
- null Ereignisse und null Artefakte;
- Ergebnis `START_REJECTED`;
- niemals `NOT_EVALUABLE` oder `RECORDING_COMPLETE`.

### Finales Laufverzeichnis

- `reservation.json` und `manifest.json` werden zuerst vollstaendig geprueft;
- beide muessen denselben Owner, Plan- und Reservierungsbezug besitzen;
- ein gueltiger Fehlerabschluss ergibt `NOT_EVALUABLE` ohne
  Bootstrap-Fehler;
- fehlt einer der Bootstrap-Belege in einem sichtbaren finalen Laufpfad,
  bleibt der Pfad `NOT_EVALUABLE` mit
  `LIFECYCLE_BOOTSTRAP_INCOMPLETE`; er darf nicht als gueltiger
  Fehlerabschluss abgenommen werden;
- ein `COMPLETE`-Marker ist bei weniger als 183 Operationen und 366
  Ereignissen immer ungueltig;
- `COMPLETE` und `NOT_EVALUABLE` bleiben gegenseitig exklusiv.

## Gebundene Korrektur

Eine spaetere Implementierung darf nur:

1. die Bootstrap-Publikation von `ie-op-001` und `ie-op-002` vor die
   Rueckgabe eines aktiven Recorders ziehen;
2. den Runner erst danach Runtime- oder andere fehlbare Laufarbeit beginnen
   lassen;
3. den Vorreservierungsstatus als `START_REJECTED` materialisieren;
4. den Verifikator um die getrennte Lifecycle-Abnahme erweitern;
5. Test 21 auf einen Fehler ab `ie-op-003` mit vorhandener Reservierung und
   vorhandenem Manifest umstellen;
6. einen getrennten Vorreservierungstest fuer `START_REJECTED` ohne finalen
   Laufpfad hinzufuegen.

Unzulaessig sind:

- nachtraegliches Erzeugen eines Manifests;
- Akzeptieren eines manifestlosen `NOT_EVALUABLE` als fehlerfrei;
- Aenderung von ParentSetV1, Signallogik, Registryzahl `183/366`,
  Memory-Zustaenden, Funktionsgeschichten oder Erfolgskriterien;
- Freigabe des realen Fuenf-Status-Laufs.

## Erhaltene 28 Pruefbereiche

Die in S2-IL bestandenen Bereiche bleiben quell- und vertragsseitig
unveraendert:

- 14 S2-ID-Status-, Symmetrie- und Fehlerpruefungen;
- sechs bereits bestandene Laufhuellenpruefungen;
- acht ParentSetV1-Pruefungen einschliesslich aller 76 Mehr-Eltern-
  Operationen und `ie-op-171 = 814` Byte.

S2-IM ist ausschliesslich ein Lifecycle-Befund. Er ist kein negativer
Memory-Befund und qualifiziert noch keine Implementierung.

## Naechste Grenze

Erst eine ausdruecklich freigegebene enge Lifecycle-Implementierung darf die
gebundene Korrektur umsetzen. Danach ist eine neue gemeinsame Qualifikation
unter neuer ID erforderlich. Bis zu deren vollstaendigem Bestehen bleibt der
reale Fuenf-Status-Funktionslauf gesperrt.
