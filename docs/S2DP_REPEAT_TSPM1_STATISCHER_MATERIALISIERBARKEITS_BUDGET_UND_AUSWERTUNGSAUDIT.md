# S2-DP Wiederholung: Statischer TSPM-1-Materialisierbarkeitsaudit

## Auftrag und Grenze

Der S2-DP-Wiederholungsaudit prueft ausschliesslich, ob die acht in S2-DQ
geschlossenen Bindungen widerspruchsfrei, vollstaendig, nichtzirkulaer und
eindeutig materialisierbar sind. Grundlage sind der unveraenderte
S2-DO-Vergleichsvertrag, der urspruengliche S2-DP-Stopp und der
S2-DQ-Korrekturvertrag.

Es wurden keine Projektmodule importiert, keine Zustandsfunktion aufgerufen,
keine Tests oder Vergleiche ausgefuehrt und keine Implementierungsdatei
geaendert. Dieser Audit ist kein Funktions- oder Memory-Befund.

## Quellenbindung

- S2-DO-Artefaktdigest:
  `431fa352d0a32789af72531f34bdd6b2462fcee8f43b026db47bb39fb1ddade2`;
- urspruenglicher S2-DP-Artefaktdigest:
  `290a96deb478ef7ab09efd0efa637350fd7c3e562afced820c1ff8bd09a7d8ae`;
- S2-DQ-Artefaktdigest:
  `ae6fb10da3c016cdd957f5a307115a1f29406ce91606165bec91e86c39b8de08`.

Die fuenf in S2-DQ gebundenen Quellblobdigests stimmen bytegenau mit den
Git-Blobinhalten von `HEAD` ueberein. Abweichende Arbeitskopie-Zeilenenden
sind nicht Teil dieser Git-Blobidentitaet.

## DP-B01: Konfiguration, Dimension und Quelle

`K=3`, `C=2`, `E=8`, die Fast-Schwellen `0.2`, der Updatefaktor `0.5` und
beide unveraenderten PPB-1-Konfigurationen sind literal gebunden.

Die auditive Quellanatomie besitzt acht Traeger. Die visuelle
`3 x 2 x 3`-Anatomie besitzt exakt 18 Traeger, nicht sechs. Damit umfasst ein
gemeinsamer audiovisueller Nutzvektor exakt `8 + 18 = 26` Werte. Geometrien,
Traegerreihenfolge, Traegerdigests, Weltvertrag, Quell-, Frame- und
Binding-ID-Formen sind kandidatenunabhaengig gebunden.

**Befund:** `DP-B01_CLOSED`.

## DP-B02: H1 bis H7

Alle sieben Geschichten besitzen endliche literale Bildungsfolgen,
Checkpoints, Probevektoren, PPB-Budgetindizes und halboffene
10-Tick-Intervalle.

- H1 bindet die erste schnelle Aufnahme.
- H2 bindet die PPB-Angebote an die Bildungsindizes 2, 3 und 4.
- H3 legt nach der letzten AX-Auswahl in Schritt 4 exakt acht nicht passende
  Schritte bis Schritt 12 fest. Wegen `12 - 4 >= E` ist der Fast-Ablauf vor
  der Probe eindeutig.
- H4 bindet die Teilassoziationen AY und BX nach stabilisiertem AX.
- H5 erzeugt mit AX, P2, P3 und P4 bei `K=3` einen eindeutigen LRU-Ersatz von
  AX in Schritt 8; die letzten Auswahlschritte sind AX=4, P3=6 und P2=7.
- H6 trennt einmalige Stoerer von einer langsamen AX-Bindung.
- H7 bindet exakt `[true,true,false,false,false]` fuer AX, NEAR,
  PARTIAL_OUT, OUTSIDE und FAR.

Keine Fixtureentscheidung liest ein spaeteres Kandidaten- oder
Baselineergebnis.

**Befund:** `DP-B02_CLOSED`.

## DP-B03: PPB-Direktbudgets

Beide PPB-Arme besitzen dieselbe feste Zustandskapazitaet von 176
funktionalen Woertern, dieselben PPB-Konfigurationen, dieselben gemeinsamen
Operationsobergrenzen und dieselbe Probezahl.

`B1_DIRECT` erhaelt alle Originalframes genau einmal und ist die vorab
deklarierte staerkere Vollinputbaseline. `B1_BUDGET_MATCHED` erhaelt nur die
literal gebundenen, kandidatenunabhaengigen Indizes. Beide bleiben getrennt
auszuweisen. Da der Vollinputarm innerhalb der gemeinsamen festen
Operationsobergrenzen liegt, ist er nicht nachtraeglich durch ein
TSPM-1-Ergebnis budgetiert. Reproduziert er die Pflichtprognose, sperrt er
einen TSPM-1-Vorteilsbefund.

**Befund:** `DP-B03_CLOSED`.

## DP-B04: B2, B3 und B4

- B2 ist genau eine gemeinsame adaptive Online-Prototypbank mit neun Slots,
  getrennten mittleren L1-Schwellen, Updatefaktor `0.5`, Supportsaettigung
  2, Ablauf 8, freier Slotwahl und eindeutigem LRU-Tie-Break.
- B3 ist genau ein gemeinsamer Nachhallvektor mit homogener Aktualisierung
  `0.5*alt + 0.5*eingang`, Ablaufgrenze 8 und gemeinsamer read-only Probe.
- B4 ist genau ein FIFO mit neun Eintraegen und festem Treffer-Tie-Break;
  Ringwahl ist ausgeschlossen.

Die drei Baselines besitzen keine zweite Speicherebene, kein Replay und
keine kandidatenabhaengige Regel.

**Befund:** `DP-B04_CLOSED`.

## DP-B05: Ressourcenledger

Die Einheit `functional_word64` ist eindeutig. IDs, Schemata, Provenienz und
Sicherheitsdigests werden getrennt als Belegbytes behandelt und duerfen
nicht funktional genutzt werden.

Die Maximalzaehlung ist reproduzierbar:

```text
TSPM-1 Fast:       3 * (26 Werte + 4 Metadaten) + 3 Zaehler/Zeitwerte = 93
PPB-1 auditiv:     8 * ( 8 Werte + 3 Metadaten) + 2 Zaehler/Zeitwerte = 90
PPB-1 visuell:     4 * (18 Werte + 3 Metadaten) + 2 Zaehler/Zeitwerte = 86
TSPM-1 gesamt:                                                    269
```

Die weiteren Armwerte `0`, `176`, `176`, `264`, `29`, `255` und `269`
ueberschreiten dieses gemeinsame Maximum nicht. `269 * 8 = 2152` Bytes.
Ungenutzte Kapazitaet darf nicht als versteckte Historie belegt werden.

**Befund:** `DP-B05_CLOSED`.

## DP-B06: Operationsbudget

Die gemeinsamen Obergrenzen sind vor der Ausfuehrung fest:

- 293 funktionale Wortschreibungen je Bildung;
- 234 skalare Distanzterme je Bildung;
- 234 skalare Distanzterme je Probe;
- null funktionale Schreibungen je read-only Probe.

Die Distanzgrenze folgt aus `9 * 26 = 234`. Die Schreibgrenze deckt den
groessten gebundenen B2-Fall mit neun Slotloeschungen, einer anschliessenden
Slotbelegung und drei Schritt-/Zeitwerten ab. Fuer TSPM-1 ergeben drei
Fast-Slotvergleiche plus beide PPB-Suchen hoechstens
`3*26 + 8*8 + 4*18 = 214` Distanzterme. Die Grenzen werden daher nicht aus
einem spaeteren Kandidatenlauf abgeleitet.

**Befund:** `DP-B06_CLOSED`.

## DP-B07: Comparator und Gleichstaende

Die Auswertung besitzt eine feste Fail-Closed-Reihenfolge: methodische
Ungueltigkeit, Kandidatenfehler, R0-Gleichheit, Erklaerung durch eine einfache
Baseline, fehlendes Kandidatenpraedikat und erst zuletzt ein moeglicher
technischer Zwei-Zeitskalen-Vorteil.

P1 bis P5 sind boolesch und gemeinsam erforderlich. Es gibt keine
Mehrheitswertung und keinen Ausgleich zwischen Geschichten. Die staerkste
einfache Baseline wird nur fuer die Berichtsreihenfolge anhand der
vorregistrierten lexikographischen Tie-Regeln bestimmt. R0-Gleichheit bleibt
in jedem gueltigen Fall die generische Engineeringeinordnung und sperrt eine
MCM-spezifische Interpretation.

**Befund:** `DP-B07_CLOSED`.

## DP-B08: Zellen, Receipts und Resultate

Die Matrix besitzt exakt `7 * 8 = 56` frische, einmalig konsumierbare Zellen
mit IDs der Form `S2DQ:<history_id>:<arm_id>`. Acht private Datentraegerrollen
binden Konfiguration, Fixture, Arm, Zellplan, Budget, Receipt, Zellresultat
und atomaren Gesamtvergleich.

Funktionale Vor- und Nachzustandsformen sind fuer alle acht Arme festgelegt.
Findings sind read-only, binden ihren Vorzustand und besitzen keinen
Nachzustand. R0 bildet Fast-Slots, PPB-Zustaende,
Konsolidierungsereignisse und Findings positions-, modalitaets- und
indexerhaltend ab. Fremde, stale, doppelte, vertauschte oder teilverbrauchte
Traeger fuehren zu keinem Teilresultat.

**Befund:** `DP-B08_CLOSED`.

## Gesamtergebnis

Alle acht S2-DP-Blocker sind auf Vertragsniveau geschlossen. Die Bindungen
sind untereinander widerspruchsfrei, kandidatenunabhaengig und eindeutig in
private Vergleichstypen und Operatoren ueberfuehrbar.

`PASS_TSPM1_STATIC_COMPARISON_MATERIALIZABILITY_BUDGET_AND_EVALUATION_REPEAT_AUDIT`

Der Befund autorisiert keine Ausfuehrung. Er macht ausschliesslich eine
separat freizugebende private Vergleichsimplementierung methodisch zulaessig.
TSPM-1 bleibt eine private technische Memory-Architektur; ein Funktionsvorteil
oder MCM-spezifischer Mechanismus ist nicht belegt.

## Naechster Schritt

S2-DR darf nach separater Freigabe ausschliesslich die private
Vergleichsimplementierung und synthetische Vertragstests fuer die bereits
gebundenen 56 Zellplaene festlegen. Zustaende oder Vergleiche duerfen erst in
einem danach gesondert freizugebenden Ausfuehrungsschritt ausgefuehrt werden.
API, Snapshot, Feldpfad, Produktion und reale Eingaben bleiben gesperrt.
