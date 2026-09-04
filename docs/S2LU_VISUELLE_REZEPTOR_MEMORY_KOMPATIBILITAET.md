# S2-LU: Visuelle Rezeptor-Memory-Kompatibilitaet

## Umfang

S2-LU vergleicht zwei vorab versiegelte Formfamilien mit je acht Varianten fuer
Position, Kantenlage, Groesse, Kontrast und Anordnung. Alle 16 RGB8-Frames
besitzen kanonische Quelldigests und werden erst nach deren Pruefung durch den
unveraenderten `1920x1080`-Rezeptor gefuehrt.

Hauptrepraesentation sind die bestehenden 288 Blockmittelwerte. Lokale
Gradienten mit 576 Werten dienen ausschliesslich als feste Diagnosebaseline.
Memory, Kontext und Feld werden nicht aufgerufen. Quellen werden weder nach
Messwerten ausgewaehlt noch nachtraeglich angepasst.

## Ergebnis

Der Vergleich ist mit `RECORDING_COMPLETE` abgeschlossen. Alle 120 Beziehungen
sind im Ergebnisbeleg enthalten: 56 innerhalb und 64 zwischen den Familien.

| Messung | Innerhalb einer Familie | Zwischen den Familien |
| --- | ---: | ---: |
| Blockmittel-L1, Minimum | `0.002227` | `0.014524` |
| Blockmittel-L1, Maximum | `0.037763` | `0.045752` |
| Blockmittel-L1 `<= 0.01` | `8/56` | `0/64` |
| Blockmittel-L1 `<= 0.2` | `56/56` | `64/64` |

Die 288 Blockmittelwerte tragen die geordnete Formstruktur: Jede gemessene
familienuebergreifende Beziehung liegt oberhalb der bestehenden visuellen
Slow-Grenze. Die Grenze von `0.01` umfasst aber nur 8 von 56 Beziehungen
innerhalb derselben Formfamilie. Die Fast-Grenze von `0.2` umfasst saemtliche
Beziehungen. Fuer dieses Korpus ist daher keine groessere visuelle
Repraesentation begruendet; die festen Matchinggrenzen sind jedoch nicht mit
der beobachteten Variantenstreuung kompatibel.

Die Gradientendiagnose trennt auf ihrer aktuellen Skalierung keine Beziehung
an der Grenze `0.01` und rechtfertigt keine Produktionsintegration.

## Teilhinweismaske

Die unveraenderte visuelle Maske beobachtet die Positionen `0..31`. Das sind
nur 32 von 288 Werten: zehn vollstaendige Zellen und zwei Kanaele einer
weiteren Zelle, ausschliesslich in Rasterzeile 0.

- 56 von 64 familienuebergreifenden Paaren sind auf diesen Positionen exakt
  gleich.
- 49 von 56 innerfamiliaeren Paaren sind dort ebenfalls exakt gleich.
- Insgesamt unterscheiden sich 105 Vollvektorpaare, obwohl ihr sichtbarer
  Teilhinweis exakt identisch ist.

Die feste Maske traegt fuer zentral angeordnete Formen kaum
Unterscheidungsinformation. Sowohl die exakte Positionsregel als auch ihre
metrische Variante liefern deshalb fuer die meisten Paare Kollisionen.

## Schluss

Der Engpass liegt in diesem Versuch nicht primaer bei der Groesse der
288-Werte-Repraesentation. Vor einem neuen Memorylauf muessen die feste
visuelle Slow-/Fast-Kompatibilitaet und die raeumlich einseitige
Teilhinweismaske getrennt behandelt werden. S2-LU waehlt keine neue Schwelle
und aendert keinen Produktionscode.

Belege:

- `reports/s2lu/s2lu-visual-memory-compatibility-corpus-20260905-01/presealed-plan.json`
- `reports/s2lu/s2lu-visual-memory-compatibility-comparison-20260905-01/comparison.json`
- `reports/s2lu/s2lu-visual-memory-compatibility-comparison-20260905-01/verification.json`
- `reports/s2lu/s2lu-visual-memory-compatibility-qualification-20260905-01/qualification.json`
