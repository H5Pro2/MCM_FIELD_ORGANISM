# S2-FY: Korrektur und Qualifikation der Slow-Support-Auslesung

## Grenze

S2-FY korrigiert ausschliesslich die Instrumentierung kuenftiger
Formationsbelege. Der abgeschlossene Lauf `s2fx-main-20260830-01` und seine
Belege bleiben unveraendert. B4, TSPM-1, PPB-1, S2-FS, die 18-Schritt-Fixture,
Schwellen, Auswertungsregeln, API, Snapshot und Feldpfad wurden nicht
geaendert.

## Ursache und Korrektur

Der bisherige Helfer `_slow_supports` verlangte exakte Gleichheit zwischen
dem literal gebundenen Zielvektor und `prototype_values`. Ein durch die
unveraenderte PPB-1-Aktualisierung gemittelter visueller Prototyp kann sich im
letzten Gleitkommabereich vom Literal unterscheiden. Der vorhandene Slot wurde
dadurch als Support `0` protokolliert.

Die korrigierte Auslesung:

- validiert die PPB-1-Bank gegen ihre unveraenderte native Konfiguration;
- verwendet `normalized_mean_l1_distance` aus dem bestehenden PPB-1-Kern;
- verwendet weiterhin die nativen Matchschwellen `0,02` auditiv und `0,01`
  visuell;
- bindet auditive und visuelle Bank jeweils an ihre eigene Konfiguration;
- gibt bei keinem passenden Slot Support `0` zurueck;
- verwirft mehrere passende Slots als mehrdeutig fail-closed;
- prueft die Zustandsunveraendertheit ueber den Bankdigest.

Es wurde weder eine Schwelle kalibriert noch eine neue Match- oder
Speicherregel eingefuehrt.

## Neutrale Qualifikation

Genau eine neue Testdatei wurde unter der Lauf-ID
`s2fy-support-readout-qualification-20260830-01` genau einmal mit `unittest`
ausgefuehrt. Die acht neutralen Tests verwenden keine P1-P11-Zustaende und
keine vollstaendige Hauptgeschichte. Geprueft wurden:

1. gemittelter visueller Prototyp mit Support `3`;
2. exakter Prototyp mit Support `1`;
3. getrennte auditive und visuelle native Schwellen;
4. Ablehnung einer modalitaetsfremden Bank-/Konfigurationsbindung;
5. fail-closed bei mehrdeutigen Slots;
6. fail-closed bei nicht kanonischen Zielwerten;
7. Support `0` ausserhalb der nativen Schwelle;
8. identischer Bankdigest vor und nach der Auslesung.

Ergebnis: `8/8`, Exit-Code `0`, terminal `OK`.

## Statischer Abschlussaudit

Der AST-, Quellen- und Diffabgleich bestaetigt:

- die einzige bestehende Codedateiaenderung liegt im privaten
  S2-FV-Instrumentierungshelfer;
- die neue Testdatei enthaelt weder Hauptgate noch `run_main_once` noch die
  gebundenen Hauptmuster;
- der Helfer ruft die bestehende PPB-1-Validierung und Distanzfunktion auf;
- `MAIN_EXECUTION_ENABLED` bleibt `False`;
- die S2-FX-Ergebnisdateien sind unveraendert;
- B4-, TSPM-1- und PPB-1-Grundkerne sind unveraendert.

Status:

`PASS_S2FY_SLOW_SUPPORT_READOUT_CORRECTION_AND_NEUTRAL_QUALIFICATION`

Dieser Status qualifiziert nur die kuenftige Support-Instrumentierung. Er
erzeugt keinen nachtraeglichen S2-FX-Funktionsbefund. Ein neuer
18-Schritt-Bestaetigungslauf benoetigt eine neue Lauf-ID und eine separate
ausdrueckliche Freigabe.
