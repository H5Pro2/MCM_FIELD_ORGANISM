# S2-KA - Prospektives Lernen mit zurueckgehaltener Variante

## Status und Frage

`S2KA_STATIC_FUNCTION_AND_FALSIFICATION_CONTRACT_COMPLETE`

S2-KA bindet genau einen begrenzten prospektiven Versuch fuer die Frage:

> Veraendert wiederholte Erfahrung mit real erzeugten, variierten
> AV-Wahrnehmungen die spaetere Behandlung einer waehrend der Bildung nie
> gesehenen positiven Variante, waehrend ein ebenfalls zurueckgehaltener
> negativer Distraktor getrennt bleibt?

Dieser Vertrag implementiert und startet nichts. Kontext, MCM-Feld,
Schwellenlernen und neue Memorymechanik bleiben ausgeschlossen. Der
abgeschlossene S2-JY-Lauf bleibt unveraendert.

## Eingefrorene Grundlage

| Bindung | Wert |
| --- | --- |
| Ausgangscommit | `941dc847de985ed612bfa81a2aa0b3fce38b8dd9` |
| S2-JY-Ergebnisdatei | `7742dcbd683602ce565d4685c345f6ca996a9215e1f8fccc1ee965e27bd15477` |
| PPB-1-Quelle | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| TSPM-1-Quelle | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| B4-Operator | `96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c` |
| Default-Live-Profilquelle | `ad5c8f607bc375daa8a6ed70134f6ed716780658a2a5e88bddb77a980da1af6f` |

Unveraendert gelten `48 + 288` Rezeptorwerte, B4-Kapazitaet 9,
TSPM-Fast-Kapazitaet 3, Fast-Schwellen `0,2/0,2`, Fast-Update `0,5`,
PPB-Schwellen `0,02` auditiv und `0,01` visuell, PPB-Update `0,05` und
Stabilitaet ab Support 3.

## Prospektive reale AV-Fixtures

Jede visuelle Fixture ist ein echtes `1920 x 1080 x 3`-RGB8-Bild. Die
vorhandenen `12 x 8 x 3 = 288` Rezeptorcarrier werden jeweils durch einen
konstanten `160 x 135`-Byteblock erzeugt. Der unveraenderte Rezeptor bildet
einen solchen Block exakt auf `byte/255` ab.

Jedes Audiofenster besteht aus 4.800 echten `PCM_F32LE`-Samples bei 48 kHz
und wird in zehn 480-Sample-Hops durch den bestehenden auditiven Rezeptor
gefuehrt. Fuer `T_PLUS`, `T_MINUS` und `H1` gilt dasselbe 50-Hz-Rechtecksignal
mit den exakt darstellbaren Samples `+0,5/-0,5`.

### Positive Trainingsfamilie und Holdout

Die 288 visuellen Carrier werden kanonisch in die Ordinalbereiche `0..143`
und `144..287` geteilt:

| Rolle | Carrier `0..143` | Carrier `144..287` | Formation |
| --- | ---: | ---: | --- |
| `T_PLUS` | 132 | 130 | ja |
| `T_MINUS` | 132 | 126 | ja |
| `H1` | 128 | 128 | niemals |

Die Bilder werden aus diesen Bytes erzeugt. Die 288er-Werte werden nicht
hinter dem Rezeptor eingesetzt. `H1` ist die positive zurueckgehaltene
Variante und darf weder Formation noch Baseline-Training erreichen.

### Negativer Holdout

`N0` ist ein vollstaendig schwarzes RGB8-Bild und ein PCM-Fenster aus exakt
4.800 Nullsamples. `N0` darf ebenfalls niemals Formation oder
Baseline-Training erreichen. Seine visuelle Distanz zu jedem positiven
Trainingswert ist mindestens `126/255 > 0,2`. Gegen D1..D9 ist seine
visuelle Distanz mindestens `130/288 > 0,2`, weil jedes dieser Bilder
mindestens 130 aktive Carrier besitzt.

### Verdraengungsfixtures

`D1..D9` werden unveraendert aus der gebundenen S2-JV-/S2-JX-Rezeptur
uebernommen: RGB8-Ordinalzahlen `2..10` und auditive Perioden
`400,300,240,160,120,80,60,40,30`. Jede Rolle wird genau einmal exponiert.

Fuer jeden ihrer visuellen Carrier gilt gegen `T_PLUS`, `T_MINUS` und `H1`
eine Byteabweichung von mindestens 123. Damit liegt jede Distanz mindestens
bei `123/255 > 0,2`. Untereinander besitzen D1..D9 weiterhin mindestens
`13/24 > 0,2` visuellen Abstand. Kein Distraktor aktualisiert den positiven
Fast-Slot oder einen anderen Distraktor-Fast-Slot.

## Mathematische Machbarkeit der Gegenprognose

Fuer die visuelle mittlere L1-Distanz gilt exakt:

```text
d(H1,T_PLUS)  = 3/255 = 1/85 = 0,011764705882352941 > 0,01
d(H1,T_MINUS) = 3/255 = 1/85 = 0,011764705882352941 > 0,01
d(T_PLUS,T_MINUS) = 2/255 = 0,007843137254901961 < 0,01
```

Der erste PPB-Prototyp wird bei der zweiten Formation als `T_PLUS` mit
Support 1 erzeugt. Danach folgen sechs `T_MINUS`-Updates. Mit
`r = 1 - 0,05 = 19/20` bleibt die erste Carrierhaelfte bei Bytecode 132.
Der effektive Code der zweiten Haelfte ist nach sechs Updates:

```text
q = (19/20)^6 = 47045881/64000000
p_second = 126 + 4q = 128,9403675625
```

Die groesste Distanz eines `T_MINUS`-Updates zum jeweils vorherigen
Prototyp betraegt `2/255 < 0,01`; die gesamte Aktualisierungskette ist daher
mechanisch zulaessig. Fuer den finalen adaptiven Prototyp gilt:

```text
d(H1,P_adaptiv)
  = (4 + 0,9403675625) / (2*255)
  = 26348627/2720000000
  = 0,009686995220588236 < 0,01
```

Die Reserve innerhalb der Schwelle betraegt
`851373/2720000000 = 0,0003130047794117647`. H1 liegt zugleich ausserhalb
jedes einzelnen Trainingsbeispiels. Damit sind prospektiv drei verschiedene
Vorhersagen moeglich:

| Modell | finale H1-Vorhersage |
| --- | --- |
| eingefrorener Erstprototyp `T_PLUS` | abweisen |
| Replay/Nearest-Exemplar unter PPB-Schwellen | abweisen |
| adaptiv verschobener PPB-Prototyp | annehmen |

Diese Rechnung belegt die statische Konstruierbarkeit. Vor einem spaeteren
Memorylauf muessen alle Werte und Abstaende dennoch einmal aus den
tatsaechlichen Rezeptorausgaben materialisiert und ohne Regelanpassung
gebunden werden. Eine abweichende reale Materialisierung ergibt
`START_BLOCKED_FIXTURE_MATERIALIZATION`, nicht einen Memorybefund.

## Eine Geschichte und vier Checkpoints

Die einzige Bildungsfolge lautet:

```text
T_PLUS, T_PLUS,
T_MINUS, T_MINUS, T_MINUS, T_MINUS, T_MINUS, T_MINUS,
D1, D2, D3, D4, D5, D6, D7, D8, D9
```

Die positive Supportfolge ist vorab gebunden:

| Formation | Eingabe | Fast-Ereignis | PPB-Ereignis | Slow-Support |
| ---: | --- | --- | --- | ---: |
| 1 | `T_PLUS` | erzeugt | keines | 0 |
| 2 | `T_PLUS` | aktualisiert | Erstprototyp erzeugt | 1 |
| 3 | `T_MINUS` | aktualisiert | angepasst | 2 |
| 4 | `T_MINUS` | aktualisiert | angepasst, stabil | 3 |
| 5..8 | `T_MINUS` | aktualisiert | weiter angepasst | 3 |

An jedem Checkpoint werden `H1` und `N0` in dieser Reihenfolge read-only
geprobt:

| Checkpoint | Zustand | gebundene Quellenprognose fuer H1 |
| --- | --- | --- |
| `C0` | vor jeder Formation | kein B4-, Fast- oder Slow-Treffer |
| `C1` | nach einer `T_PLUS`-Formation | B4/Fast moeglich, kein Slow-Zustand |
| `C2` | nach allen acht positiven Formationen | B4, Fast und stabiler Slow-Inhalt |
| `C3` | nach D1..D9 | weder B4 noch Fast; ausschliesslich stabiler Slow-Inhalt |

`N0` darf an keinem Checkpoint einen mechanischen Treffer liefern. Die
Quellproben verwenden jeweils neue Zeitfenster, bleiben aber auf Payload- und
Rezeptorwertebene rollenidentisch. Keine Probe schreibt Zustand, Support,
Zeit oder Owner fort.

Nach Formation 8 besitzt der positive Slow-Slot Support 3. Nach den neun
Distraktoren enthaelt B4 ausschliesslich D1..D9. Der positive Fast-Slot wurde
zuletzt bei Schritt 8 verwendet und verfaellt spaetestens vor Schritt 16,
weil `expire_after_exposures = 8`. D1..D9 werden nur einmal exponiert und
loesen keine eigene Slow-Konsolidierung aus. Der positive Slow-Slot bleibt
unveraendert vorhanden, weil die PPB-Schrittzaehler durch diese nicht
konsolidierten Einzelreize nicht fortgeschrieben werden.

## Drei getrennte Baselines

Alle Baselines erhalten dieselben bereits erzeugten Rezeptorwerte, aber
keine Memoryreceipts, Sollwerte oder Fallentscheidungen.

1. `FROZEN_FIRST_PROTOTYPE` bindet den ersten tatsaechlichen
   Konsolidierungseingang `T_PLUS` und aktualisiert ihn nie.
2. `REPLAY_NEAREST_EXEMPLAR` behaelt ausschliesslich die reduzierten
   336-Werte-Formationsbeispiele und waehlt read-only das naechste Beispiel.
   Fuer den Vergleich mit B_STABLE gelten die unveraenderten PPB-Schwellen.
3. `ADAPTIVE_PROTOTYPE_BANK` erhaelt in einer getrennten frischen Bank die
   prospektiv festgelegte Konsolidierungsfolge `T_PLUS` plus sechs
   `T_MINUS`-Updates. Sie darf den Memoryzustand weder lesen noch veraendern.

Alle drei berechnen L1 direkt und getrennt fuer Audio und Bild. Keine
Baseline kennt die Rollen `positiv` oder `negativ`. Das Versuchsergebnis wird
erst danach gegen die versiegelte Auswertungsfixture geprueft.

## Endlicher Umfang und Budgets

| Rolle | Anzahl beziehungsweise Grenze |
| --- | ---: |
| semantisch verschiedene AV-Fixturerollen | 13 |
| sequenzielle AV-Bloecke einschliesslich Proben | 25 |
| visuelle Rezeptoranalysen | 25 |
| auditive Hop-Aufrufe | 250 |
| Memoryformationen | 17 |
| read-only Memoryproben | 8 |
| Memory-Top-Level-Operationen, vier je Bildung/Probe | 100 |
| Baselineoperationen | 31 |
| gesamte funktionale Ledgeroperationen | 157 |
| reduzierte Rezeptorwerte | 8.400 |
| gestreamte Rohbytes | 156.000.000 |
| maximal gleichzeitig Frame plus Hop | 6.222.720 Bytes |
| maximaler numerischer Memoryzustand | 44.544 Bytes |
| Memory-L1-Obergrenze | 133.344 Terme |
| Frozen-Baseline-L1-Obergrenze | 2.688 Terme |
| Replay-L1-Terme | 17.472 |
| adaptive Baseline-L1-Terme | 3.360 |
| gesamte L1-Obergrenze | 156.864 Terme |

Die 157 Ledgeroperationen bestehen aus 25 AV-Materialisierungen, 100
Memoryoperationen, 31 Baselineoperationen und einer reinen Auswertung.
Rezeptorinterne Arbeit und native Memorykosten werden zusaetzlich berichtet,
nicht in diesen Top-Level-Zaehler umgedeutet. Rohdaten werden blockweise
erzeugt, nach der Rezeptorreduktion verworfen und nie aufgezeichnet.

## Ergebnis- und Falsifikationsregeln

`S2KA_WITHHELD_VARIANT_GENERALIZATION_CONFIRMED` ist nur zulaessig, wenn:

- H1 und N0 in keiner Formation und keinem Baselinetraining vorkommen;
- C0, C1 und C2 die oben gebundene Quellenentwicklung zeigen;
- H1 an C3 weder in B4 noch in TSPM-Fast vorhanden ist;
- H1 an C3 in auditivem und visuellem B_STABLE mit Support 3 erkannt wird;
- N0 an C3 in keiner Memorysicht erkannt wird;
- der eingefrorene Erstprototyp und Nearest-Exemplar H1 unter den
  PPB-Schwellen abweisen;
- die adaptive Prototypbank H1 annimmt und mit TSPM-Slow uebereinstimmt;
- alle acht Proben identische Vor- und Nachzustandsdigests besitzen;
- Quellen-, Rollen-, Operations- und Kostenbelege vollstaendig sind.

Ein vollstaendig aufgezeichneter Lauf mit anderer Funktion endet als
`S2KA_WITHHELD_VARIANT_GENERALIZATION_FALSIFIED`. Das ist ein fachlicher
Befund und darf nicht durch neue Schwellen, andere Fixtures oder eine
Wiederholung umgedeutet werden.

`NOT_EVALUABLE` bleibt auf Quellen-, Materialisierungs-, Reihenfolge-,
Owner-, Digest-, Ledger-, Zustandsunveraenderlichkeits- oder
Aufzeichnungsbruch beschraenkt.

## Aussagegrenze und naechster Schritt

Ein positiver Befund waere erstmals begrenztes perzeptives Lernen und
Generalisieren: Die erfahrungsabhaengige Verschiebung eines stabilen
Prototyps veraendert die spaetere Behandlung einer ungesehenen Variante. Er
waere weiterhin vollstaendig durch eine bekannte adaptive Prototypbank
erklaerbar und weder besondere MCM-Physik noch allgemeine Kategorienbildung.

Der Nachweis waere visuell innerhalb eines echten audiovisuellen Paars; eine
unabhaengige auditive Holdout-Generalisation waere damit noch nicht belegt.
Kontext- und Feldintegration bleiben bis zum Befund gesperrt.

Der naechste zulassbare Schritt ist eine kleine private Fixture-, Mess-,
Runner- und Verifikatorimplementierung mit neutraler Qualifikation. Der
vollstaendige `17/8/157`-Lauf benoetigt danach eine eigene Freigabe.
