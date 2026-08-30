# S2-GZ: Statischer Abnahmeaudit von S2-GY

Stand: 2026-08-30

## Auditgrenze und Ergebnis

Der Audit prueft den S2-GY-Vertrag ausschliesslich gegen vorhandene
Quelltypen, die gebundenen CSV-Registries und die literalen S2-GT-Fixtures.
Es wurden keine Projektmodule importiert, keine Funktionen aufgerufen, keine
Tests ausgefuehrt und keine Laufartefakte erzeugt.

```text
S2GZ_STATIC_MATERIALIZABILITY_AUDIT_PASSED
57_OF_57_COMPACT_RECEIPTS_MATERIALIZABLE
IMPLEMENTATION_NOT_AUTHORIZED
EXECUTION_NOT_AUTHORIZED
```

S2-GW bleibt dauerhaft `NOT_EVALUABLE`. Der Audit erzeugt keinen Befund zur
Kontextfunktion.

## Feldmaterialisierung

Jedes Feld von `CompactReceptorReceiptV1` besitzt eine konkrete vorhandene
Quelle oder eine eindeutig gebundene kanonische Ableitung.

| Receiptgruppe | Konkrete Quelle | Befund |
| --- | --- | --- |
| Operation | aktuelle Zeile aus `S2GR_OPERATION_REGISTRY.csv` | vorhanden und eindeutig |
| `source_role`, `source_id`, Fixture-IDs, Zeitfenster | `_BoundSource` | direkt vorhanden |
| History und Quellordinalzahl | aktuelle Registryzeile und gebundene Historyfixture | direkt vorhanden |
| ExecutionPlan | `AppendOnlyRunRecorder.plan` | `plan_digest` vorhanden |
| publiziertes Manifest | `AppendOnlyRunRecorder.result_digests["manifest"]` | Artefaktdigest vorhanden |
| Registry | `AppendOnlyRunRecorder.registry.bundle_digest` | vorhanden |
| Fixtures | `ExecutionPlan.fixture_digest` und `_BoundSource`-Fixture-IDs | vorhanden |
| Konfiguration | `_Runtime.coordinator_config.config_digest` | vorhanden |
| Dimensionen | Coordinator-Konstanten `8`, `18`, `26` | vorhanden und fest |
| Geometrie und Snapshot | auditive und visuelle Timed-Frame-Bindings | direkt vorhanden |
| Quell- und Feldzeit | Timed Frames, Envelope und `_BoundSource` | direkt vorhanden |
| Bildbyte-Digest | `_BoundSource.raw_sha256` | direkt vorhanden |
| Rohdatenstatus | `BrowserReceptorSequenceBatch.raw_payloads_retained` | waehrend `_analyze` vorhanden und zwingend `false` |
| auditive Werte | validiertes `bound.auditory_values` | Werte-Digest kanonisch ableitbar |
| visuelle Werte | validiertes `bound.visual_values` | Werte-Digest kanonisch ableitbar |
| AV-Projektion | `bound.values_digest` | direkt vorhanden |
| Eingangsprojektionen | beide `ppb1_input_projection_digest` | direkt vorhanden |
| Timed-Frame-Provenienz | beide `timed_frame_provenance_digest` | direkt vorhanden |
| Envelope | `envelope.envelope_digest` | direkt vorhanden |
| TSPM-Quelle | `exposure_digest` oder `probe_digest` | rolleneindeutig vorhanden |
| gebundene Quelle | `input_digest` oder `probe_digest` | rolleneindeutig vorhanden |
| Runnerquelle | `_BoundSource.source_digest` | direkt vorhanden |
| START-Elternbezug | `AppendOnlyRunRecorder.pending_start` | vor `finish` eindeutig vorhanden |

Die beiden Werte-Digests werden ausschliesslich aus bereits validierten
Tupeln mit der vorhandenen kanonischen SHA-256-Regel gebildet. Sie behaupten
keine neue Provenienz und ersetzen keine Frame-, Projektions- oder
Envelope-Digests.

Der Rohdatenstatus darf nicht nachtraeglich aus einem anderen Digest
rekonstruiert werden. Er ist beim Erzeugen der Batchquelle direkt abzunehmen
und als festes `false` in die kompakte Projektionsvorlage zu uebernehmen. Ein
anderer oder fehlender Wert stoppt vor der Receiptpublikation.

## Ausschluss von Sollwerten

Kein Receiptfeld benoetigt EvaluationPlan, Zielbild, Sollentscheidung,
GJ-Fallrolle oder spaetere Auswertung. Die History-ID und Fixture-IDs sind
neutrale Quellbindungen. Sie duerfen keine Rollen wie `CORRECT`, `FOREIGN`,
`CONFLICT` oder `ABSENT` enthalten.

Die auditive und visuelle Digestableitung liest ausschliesslich die gebundene
Quelle. Die Werte duerfen weder aus `VISUAL_FIXTURES`, `AUDITORY_BITS`, einer
Solltabelle noch aus einem erwarteten Ergebnis neu aufgebaut werden.

## Statische Groessenpruefung aller 57 Faelle

Geprueft wurden die konkreten Registryoperationen:

- 52 `FORMATION_RECEPTOR_ANALYSIS` von `op-0002` bis `op-0104`;
- vier `CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS` mit `op-0106`, `op-0108`,
  `op-0110` und `op-0112`;
- eine `CONSUMER_RECEPTOR_ANALYSIS` mit `op-0114`.

Fuer jeden Fall wurden die jeweilige Operationsklasse, Operation-ID,
History, Ordinalzahl, Quell-ID, Fixture-IDs und Ticks eingesetzt. Alle
SHA-256-Felder besitzen unabhaengig vom Inhalt genau 64 ASCII-Bytes.

Die drei Groessenrollen sind strikt getrennt:

| Groessenrolle | Minimum | Maximum |
| --- | ---: | ---: |
| Receipt-Nutzpayload ohne Zeilenabschluss | 2.445 | 2.463 Bytes |
| vollstaendige Artefakthuelle ohne Zeilenabschluss | 2.746 | 2.764 Bytes |
| kanonischer Zeilenabschluss | 1 | 1 Byte |
| gespeicherte kanonische Huelle | 2.747 | 2.765 Bytes |

Verteilung der 57 gespeicherten Huellen:

| Bytes | Anzahl |
| ---: | ---: |
| 2.747 | 24 |
| 2.748 | 4 |
| 2.749 | 11 |
| 2.751 | 10 |
| 2.754 | 3 |
| 2.762 | 1 |
| 2.765 | 4 |

Die vier Maximalfaelle sind `op-0106`, `op-0108`, `op-0110` und
`op-0112`. Kein Fall ueberschreitet die in S2-GY gebundene Maximalhuelle von
2.765 Bytes. Jeder Fall bleibt strikt unter 4.096 Bytes; der kleinste
verbleibende Abstand betraegt 1.331 Bytes.

Die Summe der konkret materialisierten Huellen betraegt 156.753 Bytes. Das
bestehende Budget von 233.472 Bytes fuer 57 ReceptorReceipts laesst 76.719
Bytes Reserve. Es wird weder erhoeht noch anderweitig verwendet.

## Trennung von Quelle und Aufzeichnung

Die spaetere Implementierung muss zwei getrennte Lebensdauern besitzen:

1. `_analyze` erzeugt und validiert den vollstaendigen In-Memory-
   `_BoundSource` samt Envelope und BoundInput oder BoundProbe.
2. Eine reine Projektion liest diesen Gegenstand und die bereits gebundenen
   Laufdaten, erzeugt daraus `CompactReceptorReceiptV1` und veraendert die
   Quelle nicht.
3. Nur die kompakte Form gelangt zu `recorder.finish`.
4. Der unveraenderte `_BoundSource` bleibt lokal fuer genau den zugehoerigen
   Nachfolger erhalten.

Das Receipt darf den In-Memory-Gegenstand weder ersetzen noch spaeter wieder
herstellen. Identitaetstests muessen vor und nach der Projektion dieselbe
Objektidentitaet und dieselben Quellendigestwerte ergeben.

## Nachfolgerbindung

Der Recorder liefert nach erfolgreicher exklusiver Publikation den
Artefaktdigest und den RESULT-Ereignisdigest an den privaten Runner zurueck.
Zusammen mit dem unveraenderten `_BoundSource` bilden sie den fluechtigen
`RecordedReceptorSource`.

Die Nachfolger sind eindeutig:

| ReceptorReceipt | Erlaubter direkter Nachfolger |
| --- | --- |
| Formationsquelle | die unmittelbar folgende `COMPOSITE_FORMATION` derselben History und Ordinalzahl |
| Kontextabrufquelle | die unmittelbar folgende `COMPOSITE_READ_ONLY_PROBE` derselben History |
| Verbraucherquelle | `MASKED_PROBE_BIND` |

Der Nachfolger-START bindet gleichzeitig:

- den `receptor_receipt_digest`;
- den vorhandenen `source_digest`;
- die direkte Registry-Elternoperation `result:op-....`;
- bei Formation oder Kontextprobe den vorgesehenen Vorzustandsdigest.

Die vier Bindungen muessen auf dieselbe Quelle zeigen. Fremde, vertauschte,
veraltete oder mehrfach verwendete Receipts stoppen vor dem Funktionsaufruf.
Der Digest des Nachfolgers ist keine Eingabe des vorherigen Receipts; dadurch
entsteht keine Rueckkante.

## Azyklischer Bindungsgraph

Der vollstaendige Graph ist vorwaertsgerichtet:

```text
Quellcodedigests + Registry + Fixtures
-> ExecutionPlan und Manifest
-> START-Ereignis

validierte Rezeptorquelle + Konfiguration
-> bestehende Frame-, Envelope-, Bound- und Quelldigests

ExecutionPlan + Manifest + START + bestehende Quelldigests
-> CompactReceptorReceiptV1
-> exklusive Artefakthuelle
-> receptor_receipt_digest
-> RESULT-Ereignis
-> direkter Nachfolger-START
-> Formation, Probe oder Maskenbindung
```

Kein Receipt enthaelt seinen eigenen Digest, einen RESULT-Digest, einen
Nachfolgerdigest oder einen Evaluationsdigest. Der Graph ist damit
materialisierbar und azyklisch.

## Erfolgs- und Pfadbudgets

Die Registrygrenze jedes ReceptorReceipts bleibt 4.096 Bytes. START- und
RESULT-Ereignisse behalten ihre eigene 4.096-Byte-Grenze. Der zusaetzliche
Receipt-Digest im jeweiligen Nachfolger-START bleibt innerhalb dieser bereits
reservierten Ereignisgrenze.

Da keine Einzelgrenze steigt und die kompakte Huelle ihre vorhandene Grenze
unterschreitet, bleiben gueltig:

```text
MAX_SUCCESS_PATH_BYTES = 2009088
MAX_FAILURE_PATH_BYTES = 2045952
MAX_RUN_PATH_BYTES     = 2045952
```

Auch der erweiterte neutrale Fehlerbeleg bleibt unter den vorhandenen Grenzen
fuer `RunFailureReceipt` und Fehlerereignisse. Fehler- und Erfolgspfad bleiben
gegenseitig exklusiv; ihre Budgets werden nicht addiert.

## Vollstaendige Fehlerentscheidung

Die in dieser Freigabe vorgegebene Entscheidung ist materialisierbar und fuer
eine spaetere Implementierung verbindlich:

```text
registrierter S2GTRecordingError
+ aktuelle Phase zulaessig
+ aktuelle Operation und failure_successor passend
-> unveraenderter urspruenglicher Code

registrierter S2GTRecordingError
+ aktuelle Phase unzulaessig
-> E002

unregistrierter S2GTRecordingError
-> E009

sonstige Ausnahme
-> E009
```

`E002` ist in allen reservierten Laufphasen zugelassen. Vor erfolgreicher
Reservierung bleibt ausschliesslich der bestehende `START_BLOCKED`-Pfad mit
`E001` zulaessig.

Diese Tabelle praezisiert genau einen Satz aus S2-GY: Ein registrierter, aber
phasenunzulaessiger Code wird nicht als `E009`, sondern als Registry- und
Bindungsfehler `E002` abgeschlossen. Die aktuelle S2-GZ-Freigabe ist fuer
diese Verzweigung normativ. Alle anderen S2-GY-Regeln bleiben unveraendert.

Insbesondere gilt fuer die Receiptgrenze:

```text
_exclusive_json -> S2GTRecordingError(code="E008")
Registry enthaelt E008 fuer die aktuelle Phase
-> recorder.fail("E008", urspruengliche Operation)
-> RunFailureReceipt.error_code = "E008"
-> Terminalstatus NOT_EVALUABLE
```

Der Fehlerbeleg bindet urspruengliche Operation, Operationsindex,
Operationsklasse, Phase, Owner, Reservierung und letzten gueltigen
Eventdigest. Dynamischer Ausnahmetext wird verworfen. Scheitert der
Fehlerabschluss, darf kein zweiter Code den bereits klassifizierten Fehler
ersetzen.

## Abnahme und naechster Schritt

S2-GZ besteht ohne offenen Materialisierungs-, Groessen-, Nachfolger-,
Zirkularitaets- oder Budgetblocker. Es wurde keine Implementierung
freigegeben oder vorweggenommen.

Der naechste Schritt ist eine separat freizugebende enge Implementierung der
kompakten Receiptprojektion, der Rueckgabe des publizierten Artefaktdigests,
der drei Nachfolgerbindungen und der vierstufigen Fehlerentscheidung. Danach
ist eine neutrale Qualifikation mit neuer ID erforderlich. Ein neuer
S2-GT-Hauptlauf bleibt weiterhin gesperrt.
