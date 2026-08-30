# S2-GY: Statischer Korrekturvertrag fuer Receipt und Fehlercode

Stand: 2026-08-30

## Status und Grenze

S2-GY bindet ausschliesslich die kuenftige kompakte Aufzeichnung der 57
Rezeptoroperationen und die fehlercodegetreue Weitergabe registrierter
Recorderfehler.

```text
S2GY_STATIC_CORRECTION_CONTRACT_BOUND
IMPLEMENTATION_NOT_AUTHORIZED
EXECUTION_NOT_AUTHORIZED
```

S2-GW bleibt dauerhaft `NOT_EVALUABLE`. Seine Artefakte werden weder
veraendert noch vervollstaendigt. Speicherkerne, Rezeptoranalyse,
Kontextverbraucher, Direktbaseline, Auswerter, Fixtures, Schwellen und
Erfolgskriterien bleiben unveraendert.

## Kanonische Receiptform

Der innere Datentraeger heisst `CompactReceptorReceiptV1`. Seine kanonische
Kodierung bleibt ASCII-JSON mit sortierten Schluesseln, kompakten Separatoren
und genau einem abschliessenden Zeilenumbruch.

Er enthaelt exakt folgende Felder:

| Gruppe | Felder |
| --- | --- |
| Schema | `schema` |
| Operation | `operation_id`, `operation_index`, `operation_class` |
| neutrale Quelle | `source_role`, `source_id`, `history_id`, `source_ordinal` |
| Lauf und Code | `execution_plan_digest`, `manifest_artifact_digest`, `registry_bundle_digest` |
| Konfiguration und Fixtures | `fixture_set_digest`, `coordinator_config_digest`, `visual_fixture_id`, `auditory_fixture_id` |
| Dimensionen | `auditory_dimension = 8`, `visual_dimension = 18`, `av_dimension = 26` |
| Anatomie | `auditory_geometry_id`, `visual_geometry_id`, `auditory_snapshot_id`, `visual_snapshot_id` |
| Zeit | `auditory_source_clock_id`, `visual_source_clock_id`, `field_clock_id`, `source_window_start_tick`, `source_window_end_tick`, `field_window_start_tick`, `field_window_end_tick` |
| Nutzdatenbelege | `raw_image_sha256`, `raw_payload_retained = false`, `auditory_values_digest`, `visual_values_digest`, `av_projection_digest` |
| Provenienz | `auditory_input_projection_digest`, `visual_input_projection_digest`, `auditory_timed_frame_provenance_digest`, `visual_timed_frame_provenance_digest`, `envelope_digest`, `tspm_source_digest`, `bound_source_digest`, `source_digest` |

Andere Felder sind unzulaessig. Insbesondere enthaelt das Receipt keine
vollstaendigen Envelope-, Stream-, Timed-Frame-, Receptor-, Coordinator- oder
TSPM-Objekte, keine Carrierliste und keine Wertefolge.

Die bestehende aeussere Recorderhuelle bleibt erhalten:

```text
schema
operation_id
owner_id
reservation_digest
start_event_digest
artifact = {"result": CompactReceptorReceiptV1}
```

`start_event_digest` ist der direkte und einzige START-Elternbezug der
publizierten Artefakthuelle. Der SHA-256 der vollstaendigen Huelle ist der
`receptor_receipt_digest`; er wird nicht selbstreferenziell in die Huelle
geschrieben.

## Digestableitung

Alle Digests verwenden die bereits gebundene kanonische SHA-256-Funktion.
Es werden keine Wahrnehmungswerte neu berechnet.

| Receiptfeld | Verbindliche Quelle |
| --- | --- |
| `raw_image_sha256` | vorhandener `_BoundSource.raw_sha256` |
| `auditory_values_digest` | SHA-256 der kanonischen Liste aus den bereits validierten `bound.auditory_values` |
| `visual_values_digest` | SHA-256 der kanonischen Liste aus den bereits validierten `bound.visual_values` |
| `av_projection_digest` | vorhandener `bound.values_digest` |
| `auditory_input_projection_digest` | vorhandener Digest der auditiven PPB-1-Eingangsprojektion |
| `visual_input_projection_digest` | vorhandener Digest der visuellen PPB-1-Eingangsprojektion |
| `auditory_timed_frame_provenance_digest` | vorhandener auditiver Timed-Frame-Digest |
| `visual_timed_frame_provenance_digest` | vorhandener visueller Timed-Frame-Digest |
| `envelope_digest` | vorhandener `envelope.envelope_digest` |
| `tspm_source_digest` | `exposure_digest` bei `FORMATION`, sonst `probe_digest` |
| `bound_source_digest` | `bound.input_digest` bei `FORMATION`, sonst `bound.probe_digest` |
| `source_digest` | vorhandener `_BoundSource.source_digest` |

`execution_plan_digest` bindet das unveraenderliche Manifest und damit die
Quellcodedigests. `manifest_artifact_digest` bindet dessen tatsaechlich
publizierte Datei. `registry_bundle_digest` bindet Operation, Pfadrolle und
4.096-Byte-Grenze. `fixture_set_digest` sowie die beiden Fixture-IDs binden
die Eingaben. `coordinator_config_digest` bindet die gemeinsam verwendete
Speicherkonfiguration.

## In-Memory- und Nachfolgerbindung

Die Kompaktierung betrifft nur den Aufzeichnungsgegenstand. Der von
`_analyze` erzeugte vollstaendige `_BoundSource` bleibt unveraendert im
Arbeitsspeicher und wird identisch an die nachfolgende Formation, Probe oder
Maskenbindung weitergereicht. Er darf weder aus dem Receipt rekonstruiert noch
durch dieses ersetzt werden.

Die kuenftige private Receptor-Aufzeichnung liefert intern genau:

```text
RecordedReceptorSource(
    source = unveraenderter _BoundSource,
    receptor_receipt_digest = SHA-256 der publizierten Artefakthuelle,
    result_event_digest = SHA-256 des zugehoerigen RESULT-Ereignisses,
)
```

Dieser fluechtige Traeger ist kein zusaetzlicher Speicherbestand und wird
nicht selbst aufgezeichnet.

Die unmittelbar nachfolgende Operation muss in ihrem START-Payload den
`receptor_receipt_digest` und den vorhandenen `source_digest` binden:

- jede `COMPOSITE_FORMATION` bindet das unmittelbar vorherige
  Formations-ReceptorReceipt;
- jede `COMPOSITE_READ_ONLY_PROBE` bindet das zugehoerige
  Kontextabruf-ReceptorReceipt;
- `MASKED_PROBE_BIND` bindet das Verbraucher-ReceptorReceipt.

Der Registry-Elternbezug `result:op-....` bleibt bestehen. Receipt-Digest,
vorheriges RESULT-Ereignis und Registry-Elternoperation muessen auf dieselbe
Rezeptoroperation zeigen. Fremde, veraltete, vertauschte oder fehlende
Bindungen stoppen vor dem Nachfolger fail-closed.

## Groessen- und Budgetbindung

Die vollstaendige Artefakthuelle wurde fuer alle 52 Formations-, vier
Kontextabruf- und eine Verbraucheroperation mit den literalen S2-GT-IDs
statisch materialisiert:

| Groesse | Minimum | Maximum |
| --- | ---: | ---: |
| `CompactReceptorReceiptV1` | 2.446 Bytes | 2.464 Bytes |
| vollstaendige Artefakthuelle | 2.747 Bytes | 2.765 Bytes |

Das Maximum liegt 1.331 Bytes unter der unveraenderten Einzelgrenze von
4.096 Bytes. Verbindlich gilt fuer jede der 57 Operationen:

```text
canonical_artifact_bytes < 4096
output_max_bytes = 4096
```

Die bisherigen Budgets bleiben unveraendert:

```text
57 ReceptorReceipts:          233472 Bytes
MAX_SUCCESS_PATH_BYTES:      2009088 Bytes
MAX_FAILURE_PATH_BYTES:      2045952 Bytes
MAX_RUN_PATH_BYTES:          2045952 Bytes
```

Eine Implementierung ist ungueltig, wenn sie fuer eine der 57 Huellen die
Grenze erreicht oder ueberschreitet. Eine Grenz- oder Budgeterhoehung ist
nicht Teil dieses Vertrags.

## Fehlercodegetreue Weitergabe

Der aeussere Runner unterscheidet kuenftig zwei Fehlerklassen.

### Registrierter Recorderfehler

Bei `S2GTRecordingError` wird `.code` unveraendert an `recorder.fail`
uebergeben, wenn alle Bedingungen gelten:

1. der Code existiert exakt einmal in der Error-Code-Registry;
2. der aktuelle Recorderzustand liegt in `allowed_phase`;
3. die aktuelle Operation ist die offene beziehungsweise naechste gebundene
   Registryoperation;
4. ihr `failure_successor` stimmt mit dem registrierten Fehlernachfolger
   ueberein.

Damit bleibt eine Ressourcenverletzung `E008`. Weder ein generischer Handler
noch der Fehlerabschluss darf sie zu `E009` umklassifizieren.

### Nicht klassifizierte Ausnahme

`E009` ist ausschliesslich zulaessig, wenn die gefangene Ausnahme kein
registrierter und fuer Operation sowie Phase zulaessiger
`S2GTRecordingError` ist. Ein unbekannter, nicht registrierter oder in der
aktuellen Phase unzulaessiger Code darf nicht als scheinbar gueltiger
Originalcode publiziert werden; er wird neutral als `E009` geschlossen.

Scheitert der Fehlerabschluss selbst, darf kein zweiter Code den ersten
bereits gueltig klassifizierten Fehler ersetzen. Der Lauf bleibt dann
unvollstaendig und damit `NOT_EVALUABLE`.

## Neutraler Fehlerbeleg

Der Fehlerabschluss bindet mindestens:

```text
error_code
failed_operation_id
failed_operation_index
failed_operation_class
failed_phase
failure_path_id
owner_id
reservation_digest
last_valid_event_digest
partial_state_digest
artifact_published = false
status = NOT_EVALUABLE
```

Fehlermeldungen werden ausschliesslich ueber die feste Registry-ID und den
festen neutralen ASCII-Text bestimmt. Der dynamische Ausnahmeinhalt, Fixture-
oder Fallnamen, Zielwerte und Evaluationsdaten gelangen nicht in Journal,
Receipt oder Terminalbeleg.

## Fail-Closed-Regeln

Vollstaendig abzulehnen sind insbesondere:

- ein nicht exakt typisierter oder unvollstaendiger kompakter Datentraeger;
- ein Digest, der nicht aus der gebundenen In-Memory-Quelle stammt;
- Dimensionen ungleich `8/18/26`;
- eine nicht passende Operations-, Manifest-, Registry-, Fixture- oder
  Konfigurationsbindung;
- ein fehlender direkter START-Elternbezug;
- ein Nachfolger ohne passendes ReceptorReceipt;
- vollstaendige oder teilweise Serialisierung der gesperrten Quellobjekte;
- eine Huelle mit mindestens 4.096 Bytes;
- Umklassifizierung eines zulaessigen registrierten Recorderfehlers;
- dynamischer Fehlertext im persistenten Beleg;
- Teilpublikation oder Fortsetzung nach einem Fehlerabschluss.

Es darf weder ein Receipt noch ein Teilzustand des nachfolgenden
Speicherschritts sichtbar werden, wenn eine dieser Regeln verletzt ist.

## Naechster Schritt

S2-GY autorisiert keine Implementierung und keine Ausfuehrung. Als naechster
Schritt ist ein separater rein statischer Materialisierbarkeitsaudit
erforderlich. Er muss insbesondere die Felder gegen die konkreten Datentypen,
alle 57 Groessen, die drei Nachfolgerrollen, den azyklischen Digestgraphen und
die E008/E009-Entscheidungsreihenfolge bestaetigen.

Erst nach bestandenem Audit duerfen die kompakte Projektion und die
Fehlerweitergabe eng implementiert werden. Danach folgt eine neutrale
Qualifikation unter eigener ID. Ein neuer Hauptlauf bleibt separat gesperrt.
