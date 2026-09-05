# S2-MG Rezeptor-/PPB-Materialisierung

## Status

`S2ME_SLOT_APPLICABILITY_HISTORY_NOT_MATERIALIZABLE`

Die einmalige Materialisierung des unveraenderten S2-MG-Plans ist technisch
vollstaendig. Der harte S2-ME-Starttest ist fuer diese Variationsklasse nicht
erfuellt. Es folgt kein Retry, kein neuer Seed, keine Umordnung und keine
Schwellenanpassung.

## Vorbindung

```text
Plan-ID:
s2mg-slot-applicability-corpus-20260905-01

Plandigest:
ff2d0f6955e1a8b60d3a4784626b2239c61459c4a75bb12b5f4b972278c50f33

Planfile-SHA-256:
02d0834a64a762ad3c9751564d3c650ca7dbe6c6c1e9b6aeb7c171682620ae45

Korpusmodul-SHA-256:
3ed54b65d6eea6d72c5b03b883d25c884ff29fa7482c6451aa8d9a491993a639

Materialisierungsmodul-SHA-256:
e67f5e1c380300e1409525821f5e743fd4f17627c87594e41b1940095630f8e5

Ausfuehrender Commit:
59cb27171aff3a3a3589315c9237b0f1df9f7f5f
```

Vor dem ersten Rezeptoraufruf wurden alle `27` RGB8-Payloads neu aus ihren
versiegelten Rezepten erzeugt. Payload-SHA-256, Bytezahl, RGB-Summe und
Quellbindungsdigest stimmten fuer alle Quellen mit dem Plan ueberein. Der
Preflightdigest lautet:

```text
49ac5c0a40711724af65a83c369bebea7b008918aa25d50fe589de635e5df662
```

## Materialisierung

- visuelle Rezeptoraufrufe: `27`;
- eindeutige Rezeptorzustandsdigests: `27`;
- eindeutige 288-Werte-Digests: `27`;
- Formdeskriptoren fuer die tatsaechlich verwendeten Formationseingaenge:
  `17`;
- direkte PPB-Aufrufe: `19`;
- aufgezeichnete PPB-Uebergaenge: `19`;
- Holdout-Auswertungen: `0`;
- B4-/TSPM-Koordinatoraufrufe: `0`;
- Huelle, Kontext und Feld: jeweils `0`;
- gespeicherte Rohpayloads: `0`.

Jeder PPB-Uebergang bindet Event, Quelle, Rezeptorzustand, 288-Werte-Digest,
144-Werte-Formdeskriptordigest, Slot, nativen Matchabstand, kleinsten
Prestate-Abstand, Support, Slotgeneration sowie PPB-Prestate, Eingang,
Transition und Poststate.

## Uebergangsbefund

Die reale Folge lautet:

```text
CREATED CREATED CREATED CREATED
REPLACED REPLACED REPLACED REPLACED
MATCHED MATCHED
REPLACED REPLACED REPLACED REPLACED REPLACED REPLACED REPLACED REPLACED REPLACED
```

Die ersten vier Varianten belegten vier verschiedene Slots. Die naechsten
vier Varianten ersetzten diese Generationen. Die spaeter wiederholten
`input-001` und `input-007` wurden danach zwar jeweils einem der neuen Slots
zugeordnet, erhoehten deren Support aber nur von `1` auf `2`:

```text
event-007 input-004 REPLACED slot.002 support=1
event-009 input-001 MATCHED  slot.002 support=2 distance=0.007552650689905593

event-008 input-010 REPLACED slot.003 support=1
event-010 input-007 MATCHED  slot.003 support=2 distance=0.007552650689905593
```

Keine Slotgeneration besitzt die verlangte Folge
`CREATED -> MATCHED -> MATCHED`. Es gibt `17` Generationen und `0`
qualifizierende Generationen. Damit entsteht keine stabile Slotgeneration
mit mindestens zwei unterschiedlichen realen Rezeptor- und
Formdeskriptordigests.

## Entscheidung

Die niedrige S2-ME-Materialisierbarkeit ist nicht bestanden. S2-ME wird fuer
diese Variationsklasse nicht implementiert. Der direkte PPB-Test war negativ;
deshalb ist der nur bei positivem Befund geforderte statische Nachweis der
Fast-ausgeloesten PPB-Aufrufe nicht anwendbar und wurde nicht ausgefuehrt.

Dies ist kein Gegenbefund zur bestehenden Memoryfunktion. Gezeigt ist enger,
dass die unveraenderte visuelle PPB-Zuordnung die vorversiegelten realen
Varianten nicht als eine stabile, hinreichend unterschiedliche Slotgeneration
materialisiert.

## Ergebnisintegritaet

```text
Ergebnisdatei: 48.769 Byte
Ergebnisdatei-SHA-256:
b2843606276f0c9eb371ca4efff8a0aa6fb84be3d0158a5df27f7a868c91effd

Kanonischer Ergebnisdigest:
ea358e091f3654fc944ffdbc1bd0a812d001a71a4e75aadd6f7a00b5a31a8ec6

Finaler PPB-Zustandsdigest:
3dd20aabe5076cb607f6a5e6f4892f6f9a5987880dba8b5685555ea671e1bab5

Gate nach dem Aufruf: False
```

Der kanonische Ergebnisdigest wurde nach dem Lauf read-only neu berechnet und
stimmt. Die README bleibt unveraendert.
