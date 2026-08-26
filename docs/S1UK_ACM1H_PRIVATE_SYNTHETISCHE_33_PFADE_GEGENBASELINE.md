# S1-UK: ACM-1H private synthetische 33-Pfade-Gegenbaseline

## Auftrag und Grenze

S1-UK setzt die ausdrueckliche Freigabe fuer genau einen privaten
synthetischen Vergleich um. Die gebundene Matrix umfasst 18 ACM-1H-Pfade,
12 CGR-1-Pfade, einen ACM-OFF-Pfad und zwei E1-Pfade.

Alle integrierten Pfade beginnen mit demselben Vier-Knoten-Feldvorzustand
`F_PROBE` mit `S=(1.0, 0.5, 0.0, 0.0)` und `H=(0,0,0,0)`. Die
G/O-Zustandsbildung ist eine getrennte synthetische Intervention. Damit wird
nur eine vermittelte spaetere Feldwirkung geprueft.

Oeffentliche API, Feldsnapshot, reale Rezeptorlaeufe und zweidimensionale
Topologie blieben unveraendert. Die Ausfuehrung ist kein realer Feldlauf.

## Private Implementierung

`mcm_field_organism/_acm1h_s1uk_matrix.py` enthaelt den unveraenderlichen
33-Pfade-Plan, die G/O- und Probe-Fixtures, den E1-Vergleichsadapter, die
getrennte CGR-1-Reduktionskontrolle, Comparatoren und einen Einmal-Executor.
Bei vorhandenem Ergebnisartefakt verweigert er jede weitere Ausfuehrung.
Die Infrastruktur ist weder aus dem Paketroot noch aus `current_api`
erreichbar.

## Ausfuehrung

Vor der Matrix bestanden 34 fokussierte Vertrags- und bestehende
Runtime-Tests. Danach wurde der gebundene Plan genau einmal ausgefuehrt und
als `reports/s1uk_acm1h_33_path_result.json` versiegelt.

- Pfade: `33`
- Ergebnisdigest:
  `cda8755beca86d724fcf03c22c1b2d9242513eeb23f27469c82bdde1d54c4bbb`
- Ergebnis: `EXPLAINED_BY_BASELINE`

## Gebundene Kontrollen

Alle Kontrollen sind erfuellt:

1. ACM-1H mit `Z0` ist fuer alle sechs Konfigurationen feldgleich zu ACM-OFF.
2. ACM-1H `G` und `O` erzeugen unterschiedliche Motivraten und
   Feldfolgezustaende.
3. Zustandswechsel und Nullzustand folgen der registrierten Intervention.
4. E1 bildet fuer `G` und `O` identische Bindings, Raten und Feldoutputs.
5. CGR-1 reproduziert ACM-1H fuer `G` und `O` in allen sechs
   Konfigurationen exakt: Kantenraten, `S`, `H`, Folgezustand und
   Felddigest stimmen ueberein.
6. Alle sechs Konfigurationen sind vollstaendig enthalten.
7. Jeder Pfad verwendet denselben Probe-Feldvorzustand.
8. Die Matrix enthaelt exakt 33 Pfade.

## Ergebnis und Stoppregel

Das exklusive S1-UK-Ergebnis lautet:

> ACM-1H wird durch eine Baseline erklaert.

Der G/O-Unterschied gegen ACM-OFF und E1 ist ein technischer vermittelter
Effekt. Er ist jedoch kein eigenstaendiger relationaler Wirkungsrest, weil
die breitere CGR-1-Gainbaseline ihn vollstaendig und exakt reproduziert.

Damit ist die in S1-UJ gebundene Gegenprognose entschieden. Aus S1-UK folgt
keine weitergehende Funktionsbehauptung.

## Naechster fachlicher Schritt

Als Anschluss ist ausschliesslich S1-UL sinnvoll: ein statischer Abschluss-
und Konsolidierungsaudit des ACM-1H-Zweigs. Er soll die private
Engineeringinfrastruktur erhalten, die fehlende Eigenstaendigkeit gegen
CGR-1 festhalten und entscheiden, welche Teile nur als Test- oder
Baselinewerkzeug weitergefuehrt werden.

S1-UL darf keine Gleichung, Parameter, Implementierung, Matrixausfuehrung
oder neue Kandidatenentscheidung enthalten.
