# S2-MT: Statischer Materialisierungs-Ursachenaudit

## Entscheidung

Die erste deterministisch verletzte Materialisierungsbindung liegt beim
ersten visuellen Teilhinweis `e22` vor:

```text
S2MTMaterializedEventV1.source_digest
!= MaskedMemoryCue336V1.source_digest
```

Ursache ist der Vergleich von `spec.event_type` mit dem nicht registrierten
Literal `PARTIAL_VISUAL`. Der tatsaechliche Ereignistyp lautet
`PARTIAL_VISUAL_CUE`.

Der Befund ist ein enger privater Adapter- und Provenienzfehler. S2-MR,
Feld, Memory und Kontextlogik wurden in Lauf 02 nicht erreicht und bleiben
durch diesen Audit unbewertet.

## 1. Ereignismaterialisierung

Die Ereignisspezifikationen werden aus 20 vollstaendigen AV-Ereignissen und
den acht Eintraegen von `CUE_SEQUENCE` aufgebaut. Die Cue-Typen entstehen als
`PARTIAL_{modality}_CUE`. Der zweite Cue ist visuell; damit ist `e22` der erste
konkrete Wert `PARTIAL_VISUAL_CUE`.

Im visuellen Zweig wird zunaechst korrekt gebildet:

```text
source_base
-> source_digest = digest(source_base)
-> build_masked_memory_cue_336(source_digest=source_digest)
```

Danach wird `source_payload` um `cue_digest` erweitert. Die folgende Bedingung
ist jedoch fuer `PARTIAL_VISUAL_CUE` wahr:

```python
if spec.event_type != "PARTIAL_VISUAL":
    source_digest = _digest(source_payload)
```

Dadurch erhaelt das Materialisat den Digest der erweiterten Form, waehrend der
unveraenderliche Cue weiterhin den zuvor gebildeten Digest von `source_base`
traegt. Die beiden Digests bezeichnen verschiedene kanonische Payloads.

Die engste belegte Korrektur ist ausschliesslich:

```python
if spec.event_type != "PARTIAL_VISUAL_CUE":
```

Ein Alias, Fallback oder toleranter Vergleich ist nicht erforderlich und
waere methodisch falsch.

## 2. Geometrieprojektion

`_geometry` konsumiert aus den Materialisaten nur:

- auditive und visuelle Rezeptorwerte der 20 Formationen;
- beobachtete Werte der acht Teilhinweise;
- Rezeptordistanzen und die festen Matchgrenzen.

Weder `S2MTMaterializedEventV1.source_digest` noch der im visuellen Cue
gebundene `source_digest` gehen in die Geometrieentscheidung ein. Der oben
nachgewiesene Digestwiderspruch kann daher durch `_geometry` weder erkannt
noch als `S2MT_GEOMETRY_NOT_MATERIALIZABLE` klassifiziert werden.

Die Geometrieform bindet vier Sammelbedingungen:

1. bitgleiche Rezeptorwerte bei Wiederholungen;
2. Fast-Trennung aller 66 unterschiedlichen Formationspaare;
3. getrennte auditive und visuelle Slow-Distanzen fuer `n00/n01/n02`;
4. exakt die erwarteten Treffermengen der acht Teilhinweise.

Lauf 02 speichert bei einem Fehler absichtlich keine Geometrieprojektion.
Ohne Funktionsausfuehrung kann deshalb nicht nachtraeglich bestimmt werden,
ob eine dieser numerischen Sammelbedingungen im konkreten Lauf falsch war.
Es wurde in diesem Audit keine Distanz neu berechnet.

## 3. Startgate

Das einzige explizite Gate nach `_geometry` lautet:

```text
geometry.status == S2MT_GEOMETRY_MATERIALIZED
```

Die Fehlerphase `MATERIALIZATION` umfasst aktuell sowohl alle Aufrufe in
`_materialize_events` als auch `_geometry` und dieses Gate. Der Beleg aus Lauf
02 beweist daher nur:

- keine Runtimeinitialisierung;
- null abgeschlossene Ereignisse;
- keinen Runtime-Snapshot;
- einen Fehler innerhalb dieses Materialisierungsabschnitts.

Er beweist nicht, dass gerade der falsche Ereignistypvergleich die geworfene
Ausnahme verursacht hat. Der Vergleich erzeugt dennoch bereits vor der
Runtime einen deterministisch inkonsistenten visuellen Quellenbeleg und muss
vor einem weiteren Lauf geschlossen werden.

## Korrektur- und Qualifikationsgrenze

Freigabefaehig ist nur die literale Korrektur
`PARTIAL_VISUAL -> PARTIAL_VISUAL_CUE` mit einem fokussierten neutralen Test,
der fuer alle vier visuellen Cues bindet:

- Cue-Quelldigest entspricht dem Quelldigest des Materialisats;
- Source-Receipt-Digest wird aus der unveraenderten Basis, dem Cue-Digest und
  genau diesem Quelldigest gebildet;
- auditive Cues und vollstaendige AV-Ereignisse bleiben bytegleich;
- Ereignisfolge, Korpus, Rezeptorwerte, Schwellen und Geometrieregeln bleiben
  unveraendert.

Keine Implementierung, kein Test und keine Projektfunktionsausfuehrung war
Teil dieses Audits. Die Laeufe 01 und 02 bleiben unveraendert
`NOT_EVALUABLE`; ein dritter Transferlauf ist nicht freigegeben.
