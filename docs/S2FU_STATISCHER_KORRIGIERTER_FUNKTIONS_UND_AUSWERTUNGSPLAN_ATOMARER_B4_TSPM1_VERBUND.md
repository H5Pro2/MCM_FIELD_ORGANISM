# S2-FU: korrigierter Funktions- und Auswertungsplan fuer den atomaren B4-/TSPM-1-Verbund

Stand: 2026-08-29
Status: `PASS_S2FU_STATIC_18_STEP_PLAN_MATERIALIZED`

## Auftrag und Abgrenzung

S2-FU ersetzt ausschliesslich die in S2-FT blockierte Ausfuehrungsprognose.
S2-FT bleibt der abgeschlossene Stoppbefund fuer die nicht tragfaehige
17-Schritt-Geschichte. Die korrigierte einzelne Geschichte lautet:

```text
P1, P2, P3, P4, P2, P1, P1, P1, P1,
P5, P6, P7, P8, P9, P10, P11, P3, P4
```

Der Plan bindet einen fruehen B4-Folgencheckpoint, getrennte Fast-/Slow-
Inhaltsbefunde und den spaeten Verlust nicht stabilisierter Inhalte. Er fuehrt
keine Zustandsfunktion aus. Fixtures, Implementierung, Tests, Runner,
Ergebnisdateien und Lauf bleiben gesperrt.

Ein spaeteres Bestehen duerfte nur einen begrenzten technischen Verbundbefund
bezeichnen: B4 traegt eine kurze explizite Bildungsreihenfolge, TSPM-1 traegt
Fast-Inhalte und wiederholungsabhaengig stabilisierte Slow-Inhalte. Es waere
kein Langzeit-Memory-, Semantik-, Kontext- oder Feldnachweis.

## Unveraenderte technische Quellen und Parameter

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| B4 | `mcm_field_organism/_tspm1_s2dr_private_comparison.py` | `96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c` |
| TSPM-1 | `mcm_field_organism/_tspm1_private.py` | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| Inhaltsprobe | `tools/_retention_capacity_read_only.py` | `524a42ae8294a14e58adfda29afa8602f3a799e0caaccae9675dc50bf0109ff7` |
| B4-Folgenprobe | `tools/_visual_sequence_memory_probe.py` | `d5fef4aa9fbbc06502f630e729161274b13c972f9ae2a1f13fb2084bb00593ec` |
| atomarer Koordinator | `tools/_s2fs_b4_tspm1_private_coordinator.py` | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` |

Unveraendert gelten:

- B4-Kapazitaet 9;
- TSPM-Fast-Kapazitaet 3;
- `consolidate_after = 2` und `expire_after_exposures = 8`;
- PPB-1-Stabilitaet ab Support 3;
- native auditive und visuelle TSPM-Matchgrenze 0,2;
- funktionale visuelle Auswertungsschwelle `44/765`;
- drei getrennte read-only Rollen `B4_RECENT`, `TSPM_FAST` und `TSPM_SLOW`.

Kein Parameter, Kern, Adapter, API-, Snapshot- oder Feldpfad wird geaendert.

## Elf literal gebundene audiovisuelle Zustaende

### Auditiv

Jeder Zustand besitzt eine eigene binaere 4-von-8-Maske. `1` und `0` sind die
exakten acht auditiven Rezeptorwerte in der angegebenen Reihenfolge.

| ID | hohe Positionen | acht auditive Werte |
| --- | --- | --- |
| P1 | 0123 | 1, 1, 1, 1, 0, 0, 0, 0 |
| P2 | 0124 | 1, 1, 1, 0, 1, 0, 0, 0 |
| P3 | 0125 | 1, 1, 1, 0, 0, 1, 0, 0 |
| P4 | 0126 | 1, 1, 1, 0, 0, 0, 1, 0 |
| P5 | 0127 | 1, 1, 1, 0, 0, 0, 0, 1 |
| P6 | 0134 | 1, 1, 0, 1, 1, 0, 0, 0 |
| P7 | 0135 | 1, 1, 0, 1, 0, 1, 0, 0 |
| P8 | 0136 | 1, 1, 0, 1, 0, 0, 1, 0 |
| P9 | 0137 | 1, 1, 0, 1, 0, 0, 0, 1 |
| P10 | 0145 | 1, 1, 0, 0, 1, 1, 0, 0 |
| P11 | 0146 | 1, 1, 0, 0, 1, 0, 1, 0 |

Alle Masken besitzen Gewicht 4. Zwei verschiedene Masken unterscheiden sich
in mindestens zwei Positionen. Der minimale normalisierte auditive L1-Abstand
ist exakt `2/8 = 0,25` und liegt ueber 0,2. Damit kann kein fremder P-Zustand
die auditive Spur eines anderen P-Zustands aktualisieren.

### Visuell

Jeder Zustand ist ein 3-x-2-Bild mit drei Zellwerten 210 und drei Zellwerten
30. Ein Zellwert wird auf seine drei visuellen Kanaele projiziert; die 18
visuellen Rezeptorwerte lauten daher jeweils `Zellwert/255` in Zell- und
Kanalreihenfolge.

| ID | hohe Zellpositionen | sechs Zellwerte |
| --- | --- | --- |
| P1 | 012 | 210, 210, 210, 30, 30, 30 |
| P2 | 013 | 210, 210, 30, 210, 30, 30 |
| P3 | 014 | 210, 210, 30, 30, 210, 30 |
| P4 | 015 | 210, 210, 30, 30, 30, 210 |
| P5 | 023 | 210, 30, 210, 210, 30, 30 |
| P6 | 024 | 210, 30, 210, 30, 210, 30 |
| P7 | 025 | 210, 30, 210, 30, 30, 210 |
| P8 | 034 | 210, 30, 30, 210, 210, 30 |
| P9 | 035 | 210, 30, 30, 210, 30, 210 |
| P10 | 045 | 210, 30, 30, 30, 210, 210 |
| P11 | 123 | 30, 210, 210, 210, 30, 30 |

Alle Bilder besitzen Gesamthelligkeit 720 und dasselbe Histogramm. Der
kleinste visuelle Abstand ist `180/765`, liegt ueber `44/765` und ueber 0,2.
Auch visuell kann daher kein fremder Zustand eine passende TSPM-Aktualisierung
ausloesen.

Die IDs bleiben ausschliesslich Versuchs- und Auswertungsmetadaten. Operatoren
erhalten nur Rezeptorwerte, Quellenobjekte und Zeitbindungen.

## Kausaler Zeit- und Quellenplan

| Phase | Umfang | Zeitfenster |
| --- | ---: | --- |
| Formationen 1 bis 4 | 4 | `[0,1)` bis `[3,4)` |
| fruehe Folgenprobe P1 bis P4 | 4 Probeinputs | `[4,5)` bis `[7,8)` |
| Formationen 5 bis 18 | 14 | `[8,9)` bis `[21,22)` |
| finale P1- und P2-Proben | 2 Probeinputs | `[22,23)`, `[23,24)` |

Das ergibt 24 einzigartige Rezeptoranalysen: 18 Formationen und sechs
Probeinputs. Auditive und visuelle Werte eines Schritts stammen aus derselben
validierten Rezeptorhuelle. Composite, Standalone-B4 und Standalone-TSPM
erhalten bytegleich dieselbe Formation. Ein Probeobjekt wird fuer alle
zulaessigen read-only Sichten wiederverwendet.

Die fruehen read-only Probeinputs veraendern keinen Speicherzustand. Die
Formation 5 folgt kausal erst nach ihrem letzten Fenster. Keine spaetere
Identitaet wird aus Probeinhalt, Label, Solltabelle oder Recorder rekonstruiert.

## Vollstaendige 18-Schritt-Prognose

| Schritt | Input | B4-Ereignis | TSPM-Fast | Fast-Verlust | PPB-Aufrufe je Modalitaet kumulativ | P1-Support | P2-Support |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: |
| 1 | P1 | `B4_APPENDED` | `FAST_CREATED` | - | 0 | 0 | 0 |
| 2 | P2 | `B4_APPENDED` | `FAST_CREATED` | - | 0 | 0 | 0 |
| 3 | P3 | `B4_APPENDED` | `FAST_CREATED` | - | 0 | 0 | 0 |
| 4 | P4 | `B4_APPENDED` | `FAST_REPLACED` | P1 | 0 | 0 | 0 |
| 5 | P2 | `B4_APPENDED` | `FAST_UPDATED` | - | 1 | 0 | 1 |
| 6 | P1 | `B4_APPENDED` | `FAST_REPLACED` | P3 | 1 | 0 | 1 |
| 7 | P1 | `B4_APPENDED` | `FAST_UPDATED` | - | 2 | 1 | 1 |
| 8 | P1 | `B4_APPENDED` | `FAST_UPDATED` | - | 3 | 2 | 1 |
| 9 | P1 | `B4_APPENDED` | `FAST_UPDATED` | - | 4 | 3 | 1 |
| 10 | P5 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P4 | 4 | 3 | 1 |
| 11 | P6 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P2 | 4 | 3 | 1 |
| 12 | P7 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P1 | 4 | 3 | 1 |
| 13 | P8 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P5 | 4 | 3 | 1 |
| 14 | P9 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P6 | 4 | 3 | 1 |
| 15 | P10 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P7 | 4 | 3 | 1 |
| 16 | P11 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P8 | 4 | 3 | 1 |
| 17 | P3 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P9 | 4 | 3 | 1 |
| 18 | P4 | `B4_EVICTED_AND_APPENDED` | `FAST_REPLACED` | P10 | 4 | 3 | 1 |

Es ist kein Fast-Ablauf erforderlich; die aufgefuehrten Verluste entstehen
deterministisch durch LRU-Ersetzung. P2 erzeugt bei Schritt 5 je Modalitaet
einen PPB-Prototyp mit Support 1. P1 wird bei Schritt 6 neu angelegt; die
Schritte 7, 8 und 9 erzeugen je Modalitaet Support 1, 2 und 3. Auditive und
visuelle PPB-Befunde muessen denselben Zustandsbezug tragen, bleiben aber
getrennt nachweisbar.

## Checkpoints und erwartete Befunde

### Nach Schritt 4

B4 enthaelt exakt die Bildungsindizes 1 bis 4 und die Wertefolge
`P1 -> P2 -> P3 -> P4`. Die vorhandene B4-Folgenprobe muss GEORDNET annehmen.
Die reihenfolgeblinde Sicht bestaetigt nur dieselben vier Inhalte.

TSPM-1 liefert statisch `NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE`. Es wird
kein TSPM-Folgenoperator, keine externe Folgenkennung und keine
Recorderrekonstruktion verwendet.

### Nach Schritt 18

B4 enthaelt exakt die Bildungsindizes 10 bis 18:

```text
P5, P6, P7, P8, P9, P10, P11, P3, P4
```

TSPM-Fast enthaelt P11, P3 und P4. P1 und P2 fehlen damit in B4 und Fast.
Die finalen unveraenderten read-only Prognosen lauten:

| Ziel | `B4_RECENT` | `TSPM_FAST` | `TSPM_SLOW` auditiv | `TSPM_SLOW` visuell |
| --- | --- | --- | --- | --- |
| P1 | kein Treffer | kein Treffer | stabiler Treffer, Support 3 | stabiler Treffer, Support 3 |
| P2 | kein Treffer | kein Treffer | Prototyp Support 1, kein stabiler Treffer | Prototyp Support 1, kein stabiler Treffer |

P2 ist unter den freigegebenen read-only Regeln funktional nicht abrufbar. Die
unstabilisierten Support-1-Prototypen bleiben jedoch als interne begrenzte Spur
vorhanden; S2-FU behauptet keine physische Tilgung jedes P2-Zustandswortes.
Durch die getrennten auditiven Masken existiert insbesondere kein gemeinsamer
stabiler auditiver Nullprototyp, der P2 faelschlich als erhalten erscheinen
lassen koennte.

## Probe- und Komponentenreferenzen

Gebunden bleiben sechs einzigartige Probeinputs und sieben high-level
read-only Aufrufe:

1. eine B4-Folgenprobe nach Schritt 4 mit vier Probevektoren P1 bis P4;
2. nach Schritt 18 je eine P1- und P2-Inhaltsprobe gegen den Composite-Zustand;
3. dieselben P1-/P2-Probeobjekte je einmal gegen Standalone-B4 und
   Standalone-TSPM.

Alle Proben muessen durch identische Vor-/Nachzustandsdigests read-only sein.
Nach jedem Formation Schritt muessen der Standalone-B4-Zustand und der
Standalone-TSPM-Zustand kanonisch exakt den jeweiligen Composite-Teilzustaenden
entsprechen. Die Referenzen verwenden frische eigene Zustaende, aber dieselben
Quellen und keine Zusatzhistorie.

Eine einfache transaktionale Parallelhuelle bleibt Engineeringbaseline. Sie
berechnet dieselben beiden reinen Kandidaten lokal, validiert beide und
veroeffentlicht nur das Paar. Reproduziert sie Funktion und Fehleratomaritaet
mit geringerem Aufwand, ist sie zu bevorzugen. Gleichwertigkeit ist kein
Scheitern der technischen Memory-Entwicklung.

## Vollstaendiges Ressourcenledger

### Composite-Formationen

Die S2-FS-Obergrenzen werden exakt auf 18 Formationen erweitert:

| Rolle | Rechnung | gebundener Umfang |
| --- | ---: | ---: |
| gemeinsame Projektion | `18 * 26` | 468 Terme |
| B4-Armwoerter | `18 * 293` | 5274 Woerter |
| TSPM-Armwoerter | `18 * 293` | 5274 Woerter |
| Koordinatorwoerter | `18 * 31` | 558 Woerter |
| **Formationswoerter gesamt** | `18 * 617` | **11106** |
| B4-Distanzterme | `18 * 234` | 4212 |
| TSPM-Distanzterme | `18 * 234` | 4212 |
| **Distanzterme gesamt** | `18 * 468` | **8424** |
| Koordinatorvalidierung | `18 * 18` | 324 |
| Koordinatordigests | `18 * 10` | 180 |
| **Kontrollterme gesamt** | `468 + 324 + 180` | **972** |

Native Kosten werden zusaetzlich berichtet: B4 schreibt 486 Woerter
(`18 * 27`); fuer TSPM-1 gilt die Obergrenze 5274.

### Read-only und Referenzen

- zwei finale Composite-Inhaltsproben: 28 Ergebniswoerter, null
  Zustandswoerter, 936 Distanzterme und 96 Kontrollterme;
- eine B4-Folgenprobe: null Zustandswoerter, 416 funktionale und 416
  validierende L1-Terme sowie 4 geordnete und 96 blind-pruefende Bits;
- Standalone-Formationen: getrennte Obergrenze 10548 Woerter und 8424
  Distanzterme; sie werden dem Verbund nicht kostenlos zugerechnet;
- vier finale Standalone-Inhaltsproben: null Zustandswoerter und 936
  Distanzterme.

Der spaetere vollstaendige Operationsumfang waere:

- 24 einzigartige Rezeptoranalysen;
- 18 Composite-, 18 Standalone-B4- und 18 Standalone-TSPM-Formationen;
- 18 kanonische Komponenten-Gleichheitspruefungen;
- eine B4-Folgenprobe;
- zwei Composite- und vier Standalone-Inhaltsproben.

Recorder-, Hash- und Auswertungsarbeit muss spaeter separat gezaehlt werden.
Sie darf keinem Speicherarm als Funktionsleistung zugerechnet werden.

## Auswertungs- und Stoppregeln

Ein spaeterer Lauf waere fachlich erfolgreich, wenn gleichzeitig gilt:

1. B4 rekonstruiert nach Schritt 4 ausschliesslich aus Bildungsindizes die
   Folge P1 bis P4.
2. Standalone-Komponenten und Composite-Teilzustaende bleiben nach allen 18
   Formationen identisch.
3. P1 und P2 fehlen final aus B4 und TSPM-Fast.
4. P1 wird auditiv und visuell nur aus stabilisiertem TSPM-Slow mit Support 3
   erkannt.
5. P2 liefert auditiv und visuell keinen stabilen read-only Treffer.
6. TSPM-1 liefert keine Folgenordnung und der Verbund trifft keine
   Gesamtentscheidung zwischen seinen drei Sichten.

Fachlich falsche Abrufe bleiben Ergebnisse. Der Versuch wird dagegen
`NOT_EVALUABLE` bei fremder oder ungleicher Quelle, abweichenden Ticks,
Teilcommit, Komponentenabweichung, Zustandsveraenderung waehrend einer Probe,
Labelnutzung als Speicherinput, TSPM-Folgenrekonstruktion, unvollstaendigem
Ledger oder unvollstaendiger Aufzeichnung.

Es gibt kein Feld `BEST_MEMORY`, keine Priorisierung, keine automatische
Erinnerungsauswahl und keinen inneren Kontext. Ein spaeterer Verbraucher ist
nicht Bestandteil von S2-FU.

## Entscheidung und naechster Schritt

`PASS_S2FU_STATIC_18_STEP_PLAN_MATERIALIZED`

Die 18-Schritt-Geschichte ist mit den unveraenderten technischen Regeln
statisch materialisierbar. P1 kann Support 3 erreichen, P2 bleibt bei Support
1, und beide verlassen anschliessend B4 und Fast. Die getrennten auditiven
Masken schliessen den in S2-FT noch offenen gemeinsamen Nullprototyp aus.

Noch nicht freigegeben sind Fixtures, Implementierung, Tests, Runner,
Ausfuehrung, API, Snapshot oder Feldintegration. Der naechste konkrete Schritt
waere nach ausdruecklicher Freigabe eine eng begrenzte private Fixture- und
Auswertungsimplementierung fuer genau diesen Plan, weiterhin ohne Lauf.

## Private Fixture- und Auswertungsimplementierung

Die spaeter getrennt freigegebene Implementierung ist in genau zwei neuen
privaten Modulen erfolgt:

```text
7e430f26d58f4e0122c42f6b93b23b0a0966e3cc4b96bd3f458797e9d598ca1a  tools/_s2fu_private_fixtures.py
52a3937dd496107e41f5f660b9a2ef262bbd0bc4b562fb1fd90faf2a13c5bd9e  tools/_s2fu_private_evaluator.py
```

Das Fixture-Modul bindet die elf literal definierten AV-Zustaende, alle 18
Expositionen und Zeitfenster, sechs Probequellen, 18 Erwartungszeilen und das
vollstaendige Ressourcenledger. Auditive Werte werden ausdruecklich als
synthetische auditive Rezeptorzustaende gefuehrt. Visuelle Analysebelege und
auditive Fixture-Bindungen besitzen getrennte Digestrollen. Pattern-IDs und
Sollwerte bleiben Auswertungsmetadaten und sind von den drei erlaubten
Operator-Eingabefeldern getrennt.

Der reine Auswerter akzeptiert nur bereits erzeugte, digestgebundene
Formation-, Komponenten-, Probequellen-, Folgen-, Sicht- und Ledgerbelege. Er
importiert keine Rezeptor-, B4-, TSPM-1-, PPB-1-, Koordinator-, Runner- oder
Dateimodule und ruft keine dieser Funktionen auf. Methodenverletzungen ergeben
`NOT_EVALUABLE`; bei gueltiger Methode werden funktionale Abweichungen getrennt
als `S2FU_FUNCTION_FALSIFIED` berichtet. P2-Support 1 bleibt als instabile Spur
sichtbar. Es gibt keine automatische Auswahl zwischen den drei Sichten.

## Statischer Codeaudit

Nach der Implementierung wurde ausschliesslich ein AST- und Quellenaudit ohne
Import oder Funktionsaufruf durchgefuehrt. Er bestaetigt:

- genau elf Pattern, auditive Mindestdifferenz `2/8` und visuelle
  Mindestdifferenz `180/765` direkt aus den Literalen;
- exakt 18 Schritte in der gebundenen Reihenfolge und sechs Probequellen;
- 18 Erwartungszeilen mit finalem Support `P1=3`, `P2=1`;
- Ressourcen `11106/8424/972` und 103 vollstaendige high-level Operationen;
- nur Standardbibliothek im Fixture und Standardbibliothek plus genau das
  private Fixture im Auswerter;
- keine Datei-, Runner-, Speicher-, Koordinator-, Feld- oder Auswahlaufrufe.

`PASS_S2FU_PRIVATE_FIXTURE_EVALUATOR_STATIC_CODE_AUDIT`

Dieser Befund ist ausschliesslich eine statische Implementierungsabnahme. Es
wurden keine Module importiert, keine Tests ausgefuehrt und keine Rezeptor-,
Zustands-, Probe- oder Auswertungsfunktion aufgerufen. Runner, Ergebnisablage,
Tests und Hauptlauf bleiben gesperrt.
