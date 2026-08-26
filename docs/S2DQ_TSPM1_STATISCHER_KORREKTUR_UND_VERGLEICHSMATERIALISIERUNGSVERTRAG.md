# S2-DQ: Statischer TSPM-1-Korrektur- und Materialisierungsvertrag

## Auftrag und Grenze

S2-DQ schliesst ausschliesslich die acht S2-DP-Blocker fuer einen spaeteren
privaten TSPM-1-Funktionsvergleich. Der Vertrag bindet Konfiguration,
Fixtures, Baselineoperatoren, Ressourcen- und Operationsledger,
Comparatorreihenfolge sowie Zell-, Receipt- und Ergebnisformen.

Es wurden keine Projektmodule importiert, keine Zustandsfunktion aufgerufen,
keine Tests oder Vergleiche ausgefuehrt und keine Implementierungsdatei
geaendert. TSPM-1, PPB-1, API, Snapshot, Feldpfad und Produktion bleiben
unveraendert.

## DP-B01: Feste Vergleichskonfiguration

Die Vergleichskonfiguration wird aus der bereits in S2-DH verwendeten
synthetischen Browserprofilanatomie materialisiert. Spaetere Implementierung
darf die Werte nicht neu waehlen:

| Rolle | Wert |
| --- | ---: |
| Fast-Kapazitaet `K` | `3` |
| auditive Fast-Schwelle | `0.2` |
| visuelle Fast-Schwelle | `0.2` |
| Fast-Updatefaktor | `0.5` |
| Konsolidierungsgrenze `C` | `2` |
| Fast-Ablaufgrenze `E` | `8` Expositionen |
| auditive Dimension | `8` |
| visuelle Dimension | `18` |
| auditive PPB-Kapazitaet | `8` |
| auditive PPB-Schwelle | `0.02` |
| auditive PPB-Updaterate | `0.05` |
| auditive PPB-Stabilisierung | `3` |
| auditive PPB-Ablaufgrenze | `256` Schritte |
| visuelle PPB-Kapazitaet | `4` |
| visuelle PPB-Schwelle | `0.01` |
| visuelle PPB-Updaterate | `0.05` |
| visuelle PPB-Stabilisierung | `3` |
| visuelle PPB-Ablaufgrenze | `64` Schritte |

Profil-ID ist `browser`, Fast-Bank-ID `tspm1.fast`. Die spaetere Fixture muss
dieselben deterministischen Konstruktoren und Geometrien wie
`tests/test_tspm1_s2dh_private_fast_core.py` verwenden, darf die Testdatei
aber nicht als Produktionsabhaengigkeit importieren.

Die Quellanatomie ist literal gebunden:

- auditive Quellkonfiguration: `LogSpectralConfig(8000,800,80,50.0,3000.0,8)`;
- auditive Geometrie: `auditory.log8.50-3000.w800.h80.v1`;
- auditive Traeger: die acht geordneten IDs
  `auditory.log_hz.50.000000`, `auditory.log_hz.89.741146`,
  `auditory.log_hz.161.069466`, `auditory.log_hz.289.091169`,
  `auditory.log_hz.518.867457`, `auditory.log_hz.931.275205`,
  `auditory.log_hz.1671.474085`, `auditory.log_hz.3000.000000`;
- SHA-256 der kompakten UTF-8-JSON-Liste dieser auditiven Traeger:
  `75896189fabe33f1cd0f7d61ac181d4761813d55cac3b6624ef152e537b79e1e`;
- visuelle Quellkonfiguration: `VisualGridConfig(120,80,3,2,30.0)`;
- visuelle Geometrie: `visual.grid3x2.channels3.source120x80.v1`;
- visuelle Traeger: geordnet nach Zeile `0..1`, Spalte `0..2`, Kanal `0..2`
  mit Literalform `visual.cell.r<row>.c<column>.channel<channel>`;
- SHA-256 der kompakten UTF-8-JSON-Liste dieser 18 visuellen Traeger:
  `b1bdc7559b8f5c3ed932f8646280bb37b1ed8a27a09fa50e433aba10838bd629`.

Gebundene Git-Blob-Digests:

- `_tspm1_private.py`:
  `c33ea3fdbc399b88e1416e91f8421f362060de1e368817e3673a93c522013252`;
- `_ppb1_reference.py`:
  `9fad3b04661fb9b8da053afd5599e3bdfe73019681ae50115263c39f3052ca9d`;
- `_ppb1_receptor_profiles.py`:
  `6e119fbb36b34f89bef786e600f1860bc98573175af9e227a8c916cfce0273d2`;
- `_ppb1_active_receptor_batch_binding.py`:
  `553b123fe36ed775fc11db32ed1a4db7646427a5c855e13acf0c87d682f274c9`;
- S2-DH-Testquelle:
  `836bd2a6ed663590eb2bcbe17442d2bc2e9bab8f2032c34208953dae50b3865d`.

Jede Abweichung sperrt Materialisierung und Ausfuehrung.

## DP-B02: Literale Vektoren und Zeitform

Ein skalares Paar `(a, v)` wird ausschliesslich zu einem auditiven
8er-Vektor `(a, ..., a)` und einem visuellen 18er-Vektor `(v, ..., v)`
expandiert. Alle Werte liegen in `[-1, 1]`.

Gebundene Zustandsnamen:

| ID | skalares Paar |
| --- | --- |
| `AX` | `(0.0, 0.0)` |
| `AY` | `(0.0, 0.6)` |
| `BX` | `(0.6, 0.0)` |
| `P2` | `(-0.8, -0.8)` |
| `P3` | `(-0.8, 0.8)` |
| `P4` | `(0.8, -0.8)` |
| `D1` | `(-1.0, -1.0)` |
| `D2` | `(-1.0, 0.0)` |
| `D3` | `(-1.0, 1.0)` |
| `D4` | `(0.0, -1.0)` |
| `D5` | `(0.0, 1.0)` |
| `D6` | `(1.0, -1.0)` |
| `D7` | `(1.0, 0.0)` |
| `D8` | `(1.0, 1.0)` |
| `NEAR` | `(0.15, 0.15)` |
| `PARTIAL_OUT` | `(0.21, 0.0)` |
| `OUTSIDE` | `(0.21, 0.21)` |
| `FAR` | `(1.0, 1.0)` |

Jede Bildungsexposition mit Einmalindex `i` verwendet das halboffene
Intervall `[(i-1)*10, i*10)` auf Feldclock
`field.synthetic.s2dq`. Probeindizes folgen streng nach der letzten
Bildungsexposition derselben Geschichte und verwenden fortlaufende
10-Tick-Intervalle. Audio und Video einer Exposition teilen das Feldfenster,
behalten aber getrennte Modalitaets-, Geometrie-, Traeger- und
Quellidentitaeten.

Jede Geschichte verwendet den Weltvertrag
`synthetic.s2dq.tspm1.world.v1` mit den literalen Phasen
`rest.before=(10,static,0.0)`, `change=(10,moving,0.2)` und
`rest.after=(10,static,0.0)`, ferner `startup_frame_count=1`,
`start_lead_ns=1`, `movement_cycles=1` und `tone_frequency_hz=100.0`.
Quell-IDs sind `source.s2dq.<history_id>.<modality>`, Frame-IDs
`frame.s2dq.<history_id>.formation.<index>.<modality>` beziehungsweise
`frame.s2dq.<history_id>.probe.<index>.<modality>`, und Batch-Binding-IDs
`binding.s2dq.<history_id>.formation` beziehungsweise
`binding.s2dq.<history_id>.probe`. Keine ID darf aus einem Kandidatenbefund
oder einem Ergebnisreceipt abgeleitet werden.

### H1 bis H7

| Geschichte | Bildung in exakter Reihenfolge | Checkpoints und read-only Proben | budgetangepasste PPB-Indizes |
| --- | --- | --- | --- |
| `H1` | `AX` | nach 1: `AX` | keine |
| `H2` | `AX,AX,AX,AX` | nach 1: `AX`; nach 4: `AX` | `2,3,4` |
| `H3` | `AX,AX,AX,AX,D1,D2,D3,D4,D5,D6,D7,D8` | nach 12: `AX` | `2,3,4` |
| `H4` | `AX,AX,AX,AX,AY,BX` | nach 6: `AX,AY,BX` | `2,3,4` |
| `H5` | `AX,AX,AX,AX,P2,P3,P2,P4` | nach 8: `AX,P4` | `2,3,4,7` |
| `H6` | `AX,AX,AX,AX,D1,D3,D8` | nach 7: `AX,D1,D3,D8` | `2,3,4` |
| `H7` | `AX,AX,AX,AX` | nach 4: `AX,NEAR,PARTIAL_OUT,OUTSIDE,FAR` | `2,3,4` |

`H3` enthaelt damit exakt acht nicht passende Expositionen nach der letzten
AX-Auswahl; AX muss vor der Probe aus der Fast-Ebene abgelaufen sein. `H5`
bindet AX zuletzt an Schritt 4, P3 an Schritt 6 und P2 an Schritt 7. P4 muss
deshalb in Schritt 8 den AX-Fast-Slot als eindeutigen LRU-Slot ersetzen,
waehrend der zuvor stabilisierte langsame AX-Zustand getrennt bestehen kann.

`H7` bindet die Distanzmargen und Wahrheitslabels literal: `AX` und `NEAR`
sind positive Aehnlichkeitsproben. `NEAR` liegt innerhalb der Fast-Schwellen,
aber ausserhalb beider PPB-Schwellen. `PARTIAL_OUT`, `OUTSIDE` und `FAR` sind
negative Proben; `PARTIAL_OUT` liegt nur auditiv ausserhalb der
Fast-Schwelle, `OUTSIDE` in beiden Modalitaeten und `FAR` eindeutig weit
ausserhalb. Der erwartete Vektor lautet damit
`[true,true,false,false,false]` in Tabellenreihenfolge.

## DP-B03: Zwei widerspruchsfreie PPB-Arme

`B1_PPB1_DIRECT` und `B1_PPB1_BUDGET_MATCHED` verwenden dieselben zwei
unveraenderten PPB-1-Baenke und denselben globalen Ressourcenrahmen.

- `PPB1_DIRECT` erhaelt jeden Bildungsindex der jeweiligen Geschichte genau
  einmal. Es ist der Vollinputarm und bleibt wegen seiner unterhalb des
  gemeinsamen Operationsmaximums liegenden Kosten budgetgueltig.
- `PPB1_BUDGET_MATCHED` erhaelt ausschliesslich die in der H1-bis-H7-Tabelle
  literal genannten Indizes. Die Auswahl ist vorregistriert und wird nicht
  aus einem spaeteren TSPM-1-Ergebnis gelesen.

Beide Arme erhalten jede read-only Probe genau einmal je Modalitaet. Sie
duerfen keine Fast-Slots, TSPM-Receipts oder kandidatenabhaengigen
Konsolidierungsentscheidungen lesen.

## DP-B04: Eindeutige B2-, B3- und B4-Regeln

### B2: Homogene gemeinsame Online-Prototypbank

B2 besitzt genau neun audiovisuelle Slots. Jeder Slot traegt 8 auditive und
18 visuelle Werte, Belegung, Support und letzten Auswahlschritt. Gemeinsamer
Match verlangt getrennt auditive und visuelle mittlere L1-Distanz `<=0.2`.
Rangfolge, Updatefaktor `0.5`, Supportsaettigung `2`, Ablauf `8`, freie
Slotwahl und LRU-Tie-Break entsprechen der Fast-Ebene. B2 besitzt keine
zweite Ebene und keine Konsolidierung.

### B3: Homogener Nachhallzustand

B3 besitzt genau einen gemeinsamen Audio-/Video-Vektor, ein Belegungsflag,
letzten Auswahlschritt und akzeptierte Expositionszahl. Die erste Exposition
setzt den Vektor. Jede weitere Exposition aktualisiert alle Werte mit
`neu = 0.5*alt + 0.5*eingang`. Eine Probe ist nur positiv, wenn seit der
letzten Bildung weniger als acht Expositionsschritte vergangen sind und
beide mittleren L1-Distanzen `<=0.2` sind. Es gibt keine Slotsuche,
Konsolidierung oder diskrete alte Zustandsmenge.

### B4: Kurzfristiger FIFO-Zustand

B4 ist ausschliesslich FIFO, nicht Ringwahl. Er besitzt neun Eintraege mit je
einem reduzierten 8+18-Vektor, Belegungsflag und Bildungsindex. Ein voller
Zustand verwirft beim naechsten Schreiben exakt den aeltesten Eintrag. Die
Probe prueft alle belegten Eintraege, verlangt beide Distanzen `<=0.2` und
ordnet Treffer nach maximaler Modalitaetsdistanz, Distanzsumme, juengerem
Bildungsindex und fester Slot-ID. Die Probe veraendert nichts.

## DP-B05: Kanonisches Ressourcenledger

Eine `functional_word64` ist genau ein persistierter Float-, Integer- oder
Booleanwert, der einen spaeteren Uebergang oder Abruf beeinflussen kann.
Statische IDs, Schemawerte, Quellenprovenienz und Sicherheitsdigests werden
nicht als funktionale Kapazitaet gezaehlt; sie werden fuer alle Arme separat
als `proof_bytes` ausgewiesen und duerfen nicht als Eingabe oder Matchwert
dienen.

Gemeinsames Maximum je Arm: `269 functional_word64` beziehungsweise
`2152 functional_bytes`.

| Arm | funktionale Woerter | ungenutzte Woerter |
| --- | ---: | ---: |
| TSPM-1 | `269` | `0` |
| B0 | `0` | `269` |
| B1 Direct | `176` | `93` |
| B1 Budget Matched | `176` | `93` |
| B2 | `264` | `5` |
| B3 | `29` | `240` |
| B4 | `255` | `14` |
| R0 | `269` | `0` |

TSPM-1 zaehlt 90 Fast-Slotwoerter, Fast-Schritt und zwei letzte
Quellzeitpunkte, 90 auditive PPB-Woerter und 86 visuelle PPB-Woerter. Ein
Fast-Slot zaehlt dabei neben 26 Werten Belegung, Support, letzte Auswahl und
Konsolidierungszahl. B2 zaehlt neun mal 29 Slotwoerter, Schritt und zwei
letzte Quellzeitpunkte. B4 zaehlt neun mal 28 Eintragswoerter, Schritt und
zwei letzte Quellzeitpunkte. Kein Arm darf ungenutztes Budget durch versteckte Historie
oder Replay belegen.

## DP-B06: Vorab festes Operationsledger

Alle Arme erhalten unabhaengig von spaeteren Ergebnissen dieselben Maxima:

- `293 functional_word_writes` je Bildungsexposition;
- `234 distance_terms` je Bildungsexposition;
- `234 distance_terms` je read-only Probe;
- null funktionale Schreibvorgaenge je Probe;
- genau die in der H1-bis-H7-Tabelle gebundene Zahl von Bildungs- und
  Probeaufrufen.

Ein `distance_term` ist genau eine skalare Absolutdifferenz. Ein
`functional_word_write` ist genau die Aenderung eines gezaehlten
funktionalen Wortes. Unveraenderte Werte, Digestberechnung und
Provenienzvalidierung zaehlen nicht als funktionale Writes.

Die Obergrenzen stammen aus der groessten zugelassenen einfachen Baseline:
B2 kann beim Ablauf neun Slots loeschen, danach einen Slot schreiben und den
Schrittzaehler fortsetzen; B4 kann bei FIFO-Verschiebung neun Eintraege
schreiben. Die Grenzen sind daher vorab
und kandidatenunabhaengig. Jeder Zellreceipt muss tatsaechliche Nutzung und
Restbudget ausweisen.

## DP-B07: Comparator- und Tie-Regeln

Vor jeder Funktionsentscheidung gilt diese feste Reihenfolge:

1. Quellen-, Fixture-, Konfigurations-, Freshness- oder Ledgerabweichung:
   `METHOD_INVALID`.
2. Zustandsmutation durch Probe, nicht atomarer Kandidatenschritt oder
   TSPM-Quellfehler: `TSPM1_FUNCTION_NOT_VALID`.
3. Fuer jeden Arm werden die folgenden fuenf booleschen Pflichtpraedikate
   berechnet:
   - `P1_EARLY`: H1 positiver gemeinsamer Abruf;
   - `P2_LATE`: H3 positiver langsamer Abruf bei fehlendem AX-Fast-Slot;
   - `P3_CONFLICT`: H4 behaelt AX unveraendert und langsam abrufbar; AY und
     BX duerfen nach ihrer einmaligen Bildung nur als schnelle, nicht als
     langsame Bindungen erscheinen;
   - `P4_EVICTION`: H5 AX-Fast-Slot korrekt ersetzt, P4 fast und AX langsam
     abrufbar;
   - `P5_ERROR`: null falsche Konsolidierungen, keine langsame H6-Bindung fuer
     D1, D3 oder D8 und exakt der H7-Vektor
     `[true,true,false,false,false]`.
4. R0 muss alle normalisierten TSPM-1-Zustaende, Ereignisse und Findings
   exakt reproduzieren. Jede Abweichung macht den Vergleich
   `METHOD_INVALID`.
5. Erfuellt mindestens eine einfache Baseline P1 bis P5 vollstaendig, lautet
   das Ergebnis `FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS`.
6. Erfuellt TSPM-1 nicht alle P1 bis P5, lautet es
   `TSPM1_FUNCTION_NOT_VALID`.
7. Erfuellt TSPM-1 alle, aber keine einfache Baseline alle Pflichtpraedikate,
   lautet es
   `TSPM1_TWO_TIMESCALE_ENGINEERING_ADVANTAGE_OVER_SIMPLE_BASELINES`.

R0-Gleichheit bindet in jedem gueltigen Fall die generische
Engineeringeinordnung.

Es gibt keine Mehrheitswertung. Boolescher Gleichstand ist exakte Gleichheit.
Nur fuer die Berichtsrangfolge gleichklassiger Baselines gilt
lexikographisch: mehr erfuellte P1-bis-P5-Praedikate, weniger
Fehlakzeptanzen, kleinere Capture-Latenz, weniger funktionale Writes,
Baseline-ID.

## DP-B08: Zell-, Receipt- und Ergebnisformen

Die spaetere private Matrix besitzt exakt 56 Zellen:

```text
7 Geschichten * (TSPM-1 + 6 einfache Baselines + R0)
```

Jede ID lautet `S2DQ:<history_id>:<arm_id>`. Jede Zelle startet frisch und
darf genau einmal konsumiert werden.

### Statische Datentraeger

1. `S2DQConfigRecord`: alle obigen Konfigurationswerte, Quellblobdigests und
   eigener Digest.
2. `S2DQFixtureRecord`: Geschichte, geordnete literale Bildungswerte,
   Checkpoints, Proben, PPB-Budgetindizes, Feldclock und eigener Digest.
3. `S2DQArmSpec`: Arm-ID, Zustandsform, Kapazitaet, Regeln,
   Ressourcenobergrenzen und eigener Digest.
4. `S2DQCellPlan`: Zell-ID, Config-, Fixture- und Arm-Digests, frischer
   Vorzustandsdigest, erwartete Aufrufzahlen und eigener Digest.
5. `S2DQBudgetReceipt`: tatsaechliche und verbleibende funktionale Woerter,
   Writes, Distanzterme und Probezahl.
6. `S2DQCellReceipt`: Quell-, Vorzustands-, Ereignis-, Finding-, Budget- und
   Nachzustandsdigests sowie terminaler Ownerstatus.
7. `S2DQCellResult`: genau ein atomarer Endzustand, geordnete read-only
   Findings, Budgetreceipt und Zellreceipt.
8. `S2DQComparisonResult`: Digests aller 56 Zellergebnisse, P1-bis-P5-Vektor
   je Arm, Comparatorreihenfolge, R0-Aequivalenz und genau eine der vier
   S2-DO-Endentscheidungen.

Die funktionalen Vor- und Nachzustandsformen sind ebenfalls fest:

| Arm | kanonischer funktionaler Zustand |
| --- | --- |
| TSPM-1 | drei Fast-Slots, Fast-Schritt, zwei unveraenderte PPB-1-Bankzustaende |
| B0 | leeres Tupel |
| B1 Direct / Matched | auditiver und visueller PPB-1-Bankzustand |
| B2 | neun geordnete gemeinsame Slots und Schrittzaehler |
| B3 | Belegung, 26 Werte, letzter Auswahlschritt, Expositionszahl |
| B4 | neun geordnete FIFO-Eintraege und Schrittzaehler |
| R0 | generische Kopie der drei Fast-Slots, des Fast-Schritts und der zwei PPB-Zustaende |

R0 bildet jeden TSPM-1-Fast-Slot positionsgleich auf einen generischen Slot,
jeden PPB-1-Zustand unveraendert auf seine Modalitaetsrolle, jedes
Konsolidierungsereignis auf ein gleichindiziertes generisches
Uebergabeereignis und jedes read-only Finding auf
`(context_source, auditory_match, visual_match, distance_pair)` ab. Verglichen
werden die normalisierten Nutzdaten und ihre Digests; TSPM-spezifische
Schema- und Typnamen werden nur aus der Gleichheitsprojektion entfernt.

Fremde, doppelte, stale, teilverbrauchte oder zwischen Zellen vertauschte
Datentraeger fuehren fail-closed zu keinem Teilresultat. Findings binden den
Vorzustand und besitzen keinen Nachzustand. Das Gesamtresultat darf erst
veroeffentlicht werden, wenn alle 56 Zellen und R0-Relationen vollstaendig
validiert sind.

## Blockerschluss

| S2-DP-Blocker | S2-DQ-Bindung |
| --- | --- |
| `DP-B01` | feste Browser-/Fast-/PPB-Konfiguration |
| `DP-B02` | literale Vektoren, Zeiten, H1-bis-H7-Folgen und Proben |
| `DP-B03` | getrennte PPB-Direkt- und vorregistrierte Budgetindizes |
| `DP-B04` | eindeutige B2-, B3- und FIFO-B4-Operatoren |
| `DP-B05` | `functional_word64`-Ledger mit Armwerten |
| `DP-B06` | kandidatenunabhaengige Operationsmaxima |
| `DP-B07` | feste Gate-, Pflichtpraedikat- und Tie-Reihenfolge |
| `DP-B08` | acht vollstaendige private Datentraegerrollen und 56 Zellen |

## Entscheidung

`PASS_TSPM1_STATIC_COMPARISON_MATERIALIZATION_CORRECTION_BOUND`

S2-DQ schliesst die acht statischen Bindungsluecken auf Vertragsniveau. Es
belegt weder Materialisierbarkeit im Wiederholungsaudit noch einen
TSPM-1-Funktionsvorteil.

## Naechster Schritt

S2-DP muss nach separater Freigabe erneut ausschliesslich statisch pruefen,
ob alle acht Korrekturen widerspruchsfrei, nichtzirkulaer und eindeutig
implementierbar sind. Bis zu einem bestandenen Wiederholungsaudit bleiben
Implementierung, Tests, Vergleichsausfuehrung, API und Feldintegration
gesperrt.
