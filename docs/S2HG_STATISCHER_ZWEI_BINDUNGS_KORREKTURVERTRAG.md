# S2-HG: Statischer Zwei-Bindungs-Korrekturvertrag

Status: `S2HG_STATIC_TWO_BINDING_CORRECTION_CONTRACT_BOUND`

## Zweck und Grenze

S2-HG schliesst ausschliesslich die beiden im S2-HF-Audit festgestellten
Offline-Validierungsluecken `HF-B01` und `HF-B02`. Der Vertrag fuegt keine
Funktions-, Speicher- oder Diagnosewerte hinzu. Er bindet zwei bereits vor den
betroffenen Receipts vorhandene Digests an die kompakten
Aufzeichnungsprojektionen.

Nicht freigegeben sind Implementierung, Import, Test, Zustandsaufruf,
Rezeptorausfuehrung oder Funktionslauf. Die In-Memory-Objekte, die
Funktionslogik, die Registrybudgets und die Fehlercodewege bleiben
unveraendert. S2-HC bleibt dauerhaft `NOT_EVALUABLE`.

## HF-B01: Owner-Vorzustand der Formation

`CompactCompositeFormationReceiptV1` erhaelt das zusaetzliche Feld:

```text
owner_prestate_digest
```

Die Quelle ist ausschliesslich der validierte Snapshot des privaten
`B4TSPM1CoordinatorOwner` unmittelbar vor dessen Wechsel nach `IN_PROGRESS`.
Der bestehende Koordinator bildet diesen Digest vor dem ersten Armaufruf und
uebergibt exakt denselben Wert an `B4TSPM1StepReceipt`.

Die verbindliche Reihenfolge lautet:

```text
validierter Owner-Vorzustand
  -> owner_prestate_digest
  -> atomarer Formation-Schritt
  -> B4TSPM1StepReceipt
  -> B4TSPM1StepResult
  -> CompactCompositeFormationReceiptV1
```

Der Digest darf weder aus dem Owner-Nachzustand noch aus
`owner_authorized_digests`, `result_digest` oder einem aufgezeichneten
Nachfolger rekonstruiert werden. Die kompakte Projektion muss ihn gegen
`B4TSPM1StepReceipt.owner_prestate_digest` pruefen.

Mit diesem Feld kann der Offline-Verifikator den Step-Receipt-Digest aus der
vollstaendigen typisierten Rollenmenge erneut berechnen.

## HF-B02: Verwendete Sequenzevidenz von S2-GC

Die bisherige Einzelrolle

```text
sequence_finding_digest
```

wird in `CompactS2GCProjectionReceiptV1` durch genau eine positionale
Digestrolle ersetzt:

```text
sequence_digests = (
    sequence_evidence_digest,
    sequence_finding_digest,
)
```

Die Positionen sind typisiert und unvertauschbar:

1. `sequence_evidence_digest` ist exakt
   `ValidatedB4ShortSequenceEvidence.evidence_digest` des Objekts, das dem
   S2-GC-Projektor tatsaechlich uebergeben wurde.
2. `sequence_finding_digest` ist exakt der Digest des daraus gebildeten
   `B4ShortSequenceFinding`.

Die Evidenz wird vor dem Finding gebildet. Das Finding bindet denselben Wert
bereits als `source_evidence_digest`. Die kompakte Aufzeichnung darf ihn daher
direkt aus den validierten Projektionsobjekten uebernehmen. Eine Ableitung aus
Status, Referenzen, Fixture, Sollwert oder spaeterer Auswertung ist verboten.

Die verbindliche Reihenfolge lautet:

```text
ValidatedB4ShortSequenceEvidence
  -> sequence_evidence_digest
  -> B4ShortSequenceFinding.source_evidence_digest
  -> sequence_finding_digest
  -> PerceptualContextBundle
  -> CompactS2GCProjectionReceiptV1
```

Die vorhandene Einzelrolle wird ersetzt und nicht zusaetzlich dupliziert.
Damit bleibt die Projektion kompakt und der Sequence-Finding-Digest kann
offline vollstaendig nachgerechnet werden.

## Quellen- und Typbindung

Beide Digests muessen vor ihrer jeweiligen kompakten Aufzeichnung existieren,
64 kleingeschriebene hexadezimale Zeichen besitzen und gegen den konkreten
Quelltyp validiert sein.

- `owner_prestate_digest` ist nur fuer die zugehoerige Formation, ihren Owner,
  ihre Autorisierung und ihren Vorzustand gueltig.
- `sequence_evidence_digest` ist nur fuer die zugehoerige Probe, den
  beobachteten B4-Zustand und die tatsaechlich verwendeten
  Sequenzreferenzen gueltig.
- Fremde, fehlende, vertauschte oder nachtraeglich erzeugte Digests stoppen
  fail-closed.
- Kein Digest darf einen Inhalt ersetzen, den ein Funktionsnachfolger
  benoetigt. Die vollstaendigen In-Memory-Objekte werden unveraendert
  weitergereicht.

## Korrigierte Feldmengen

Formation verwendet die in S2-HE gebundene Feldmenge plus
`owner_prestate_digest`.

S2-GC verwendet die in S2-HE gebundene Feldmenge mit genau dieser
Substitution:

```diff
- sequence_finding_digest
+ sequence_digests[sequence_evidence_digest, sequence_finding_digest]
```

S2-GI bleibt unveraendert.

## Groessenwirkung

Kanonisches ASCII-JSON, sortierte Schluessel, kompakte Trenner und ein LF
ergeben fuer die Formation eine exakte Zunahme von 91 Byte. Die S2-GC-
Substitution erhoeht die vollstaendige Huelle exakt um 62 Byte.

Damit gelten vor dem S2-HF-Wiederholungsaudit:

| Rolle | Korrigierte Formen | Maximum |
| --- | --- | ---: |
| Formation | 2.788 / 2.801 Byte | 2.801 Byte |
| S2-GC | 3.174 / 2.658 Byte | 3.174 Byte |
| S2-GI | 2.977 / 2.509 Byte | 2.977 Byte |

Alle Formen bleiben unter der unveraenderten 3.200-Byte-Projektionsgrenze und
der effektiven 4.095-Byte-Registrygrenze. Die kleinste Registryreserve betraegt
921 Byte.

## Digestgraph

Die neuen Kanten zeigen ausschliesslich vorwaerts:

```text
Owner-Vorzustand -> Step-Receipt -> Step-Result -> Formation-Projektion

Sequenzevidenz -> Sequenzfinding -> S2-GC-Bundle -> S2-GC-Projektion
```

`projection_digest` wird weiterhin ueber die Projektion ohne sich selbst
gebildet. Der Recorder-Artefaktdigest entsteht erst danach. Evaluation und
Abschluss sind keine Quellen der beiden Digests.

## Unveraenderte Grenzen

- `COMPACT_PROJECTION_MAX_ARTIFACT_BYTES = 3200` bleibt unveraendert.
- Die effektive Registrygrenze bleibt 4.095 Byte.
- Erfolgs-, Fehler- und Gesamtpfadbudgets bleiben unveraendert.
- `E008`, `E002` und `E009` behalten ihre gebundenen Bedeutungen.
- S2-GC-, S2-GI-, B4-, TSPM-1-, PPB-1- und Feldfunktionen bleiben
  unveraendert.

## Entscheidung

S2-HG ist statisch gebunden. Die beiden fehlenden Offline-Rollen sind nun
eindeutig, nichtzirkulaer und ohne neue Funktion materialisiert. Dieser Vertrag
ist noch keine Implementierung. Als naechster und in derselben Freigabe
geforderter Schritt folgt der vollstaendige statische S2-HF-
Wiederholungsaudit ueber alle 60 korrigierten Artefakthuellen.
