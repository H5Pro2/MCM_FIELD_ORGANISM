# S2-KK - Prospektiver Kontextnutzen im 336-Werte-Profil

## Status und Funktionsfrage

`S2KK_STATIC_FUNCTION_AND_FALSIFICATION_CONTRACT_COMPLETE`

S2-KK bindet genau eine neue prospektive Aufgabe:

> Verbessert ein zuvor gelernter `B_STABLE_VISUAL`-Kontext die Verarbeitung
> einer spaeteren, teilweise verdeckten und niemals trainierten visuellen
> Wahrnehmung gegenueber `CURRENT_PERCEPTION_ONLY`?

Der Vertrag implementiert und startet nichts. Er aendert weder Rezeptoren,
Memorykerne, Schwellen, Feldpfad noch S2-KJ. Automatische Kontextwahl,
Semantik und Feldrueckwirkung bleiben ausgeschlossen.

## Eingefrorene Grundlage

Ausgangscommit ist `c4b9eb2b2bc05819f8e9b7f759e0e33ff61f0a72`.

| Quelle | SHA-256 |
| --- | --- |
| S2-KJ Same-Probe-Binder | `920762c4a29d2baf579829fdb896526c5a2901ffd3629d52ab1658b0436a0b6c` |
| S2-KJ Zwei-Bereich-Projektion | `5e2510eb6dd58ffef27901fc545ad700d1f8a5e4d5b3363d09811fe11c0a1d17` |
| S2-KA Fixture-Referenz | `e85cd6aead34e7b22d894df0ffa5cc7565acfee7a8a7bbf84ea1eb281c8173df` |
| S2-KA Mess-/Baseline-Referenz | `74669f66fab86f2aa8d407d4f53fd183cf61919cf0bd6e046c97cf7a976b287c` |
| visueller Rezeptorpfad | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` |
| auditiver Rezeptorpfad | `a20456b24c04d099ba5ee2da6250e3d83dc657392603c41d816b13ca68a37fb7` |
| PPB-1 | `15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0` |
| TSPM-1 | `321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516` |
| B4-Operator | `96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c` |
| bestaetigter S2-KA-Ergebnisbeleg | `903d9acc7020b43ce8a0b10f98a27e4b407fd54104bb6206a374e797ee6b0c8c` |

S2-KA bleibt eine feste Lernreferenz. Seine Ergebnisdateien und seine
Holdoutwerte werden fuer S2-KK nicht wiederverwendet. S2-KK erzeugt eine
neue Fixture, neue Zeitlinie, neue Zustaende und neue Belege.

Unveraendert gelten das Default-Live-Profil mit `48 + 288` Werten,
B4-Kapazitaet 9, TSPM-Fast-Kapazitaet 3, Fast-Schwellen `0,2/0,2`,
PPB-Schwellen `0,02` auditiv und `0,01` visuell, PPB-Update `0,05` und
Stabilitaet ab Support 3.

## Prospektive AV-Fixtures

Jede funktionale Quelle besteht aus einem echten
`1920 x 1080 x 3`-RGB8-Frame und einem echten PCM-Fenster mit 4.800
`float32`-Samples. Das Audio ist fuer Training, Vollprobe und maskierte Probe
bitidentisch: ein 50-Hz-Rechtecksignal mit `+0,5/-0,5`. Nur Quelle,
Blockordinalzahl und Zeitfenster unterscheiden Expositionen. Die bestehenden
Rezeptoren erzeugen daraus die 48 auditiven und 288 visuellen Werte.

Die visuellen Carrier werden kanonisch in drei Bereiche geteilt:

```text
VISIBLE         = 0..31       32 Carrier
MASKED_COMMON   = 32..159    128 Carrier
MASKED_VARIABLE = 160..287   128 Carrier
MASKED          = 32..287    256 Carrier
```

Jeder Carrier wird als konstanter `160 x 135`-RGB-Kanalblock mit dem
angegebenen Bytewert erzeugt. Es werden keine 288er-Vektoren hinter dem
Rezeptor eingesetzt.

| Fixture | `VISIBLE` | `MASKED_COMMON` | `MASKED_VARIABLE` | Formation |
| --- | ---: | ---: | ---: | --- |
| `T_PLUS` | 0 | 132 | 130 | ja |
| `T_MINUS` | 0 | 132 | 126 | ja |
| `H_FULL` | 0 | 128 | 128 | niemals |
| `H_MASKED` | 0 | 0 | 0 | niemals |

`H_MASKED` ist ein real analysierter, verdeckter RGB8-Frame. Seine
Maskenpositionen enthalten technisch den gebundenen Okkluderwert 0. Die
zusaetzliche unveraenderliche Maske erklaert diese 256 Rezeptorwerte jedoch
zu nicht beobachteten Zielpositionen. Kein Arm darf den Okkluderwert als
Schaetzung oder Zielwert behandeln. Die 32 sichtbaren Werte bleiben reale
Rezeptorwerte.

`D1..D9` sind neu materialisierte Quellen nach der bestehenden
S2-KA-Rezeptur: neun verschiedene binaere RGB-Blockmuster und die gebundenen
auditiven Perioden `400,300,240,160,120,80,60,40,30`. Vor Memorybeginn muss
aus den tatsaechlichen Rezeptorwerten belegt sein, dass jeder Distraktor zu
`T_PLUS`, `T_MINUS` und `H_FULL` ausserhalb beider Fast-Matchbereiche liegt
und dass kein Distraktorpaar einen Fast-Slot gemeinsam aktualisiert.

Rohframes und PCM-Fenster werden einzeln gestreamt, nach der
Rezeptorreduktion verworfen und weder in Memory noch Kontext oder Ergebnis
gespeichert.

## Lerngeometrie

Fuer die tatsaechlichen visuellen Rezeptorwerte gelten prospektiv:

```text
d(H_FULL,T_PLUS)  = d(H_FULL,T_MINUS)
                  = (128*4 + 128*2) / (288*255)
                  = 8/765
                  = 0,01045751633986928 > 0,01

d(T_PLUS,T_MINUS) = (128*4) / (288*255)
                  = 16/2295
                  = 0,006971677559912854 < 0,01
```

Der erste visuelle PPB-Prototyp entsteht bei der zweiten `T_PLUS`-Formation.
Danach erfolgen sechs `T_MINUS`-Updates. Mit `q=(19/20)^6` besitzt der finale
adaptive Prototyp folgende Werte:

```text
VISIBLE:          0
MASKED_COMMON:    132
MASKED_VARIABLE:  126 + 4q
                  = 128,9403675625
```

Damit gilt theoretisch:

```text
d(H_FULL,P_adaptiv)
  = 26348627/3060000000
  = 0,008610662418300654 < 0,01

MAE_MASKED(H_FULL,P_adaptiv)
  = 26348627/2720000000
  = 0,009686995220588236
```

Die 32 sichtbaren Positionen bleiben waehrend aller Updates exakt beim
Rezeptorwert 0. Dadurch benoetigt die spaetere Sichtbarkeitspruefung weder
Float-Rundung noch eine neue Gleichheitsschwelle.

Vor dem ersten Memoryaufruf werden die real erzeugten 48er- und 288er-Werte,
alle obigen Distanzen sowie die sechs konkreten adaptiven Updateabstaende
einmal gemessen und versiegelt. Zulaessig ist fuer den adaptiven
Holdoutabstand nur das vorab gebundene Intervall
`0,0086106624182..0,0086106624184`. Eine Abweichung stoppt als
`START_BLOCKED_FIXTURE_MATERIALIZATION`; sie darf keine Suche oder
Parameteranpassung ausloesen.

## Eine Bildungsgeschichte

Die einzige Memorygeschichte beginnt aus einem frischen Composite-Zustand:

```text
T_PLUS, T_PLUS,
T_MINUS, T_MINUS, T_MINUS, T_MINUS, T_MINUS, T_MINUS,
D1, D2, D3, D4, D5, D6, D7, D8, D9
```

Nach Formation 8 muss der positive visuelle Slow-Slot Support 3 besitzen.
Nach D1 bis D9 gilt fuer `H_FULL`:

- kein B4-Treffer;
- kein TSPM-Fast-Treffer;
- visueller Slow-Treffer mit Support 3;
- keine Veraenderung des positiven Slow-Slots durch die neun einmaligen
  Distraktoren.

Die Vollprobe `H_FULL` liegt in einem neuen Block unmittelbar nach Formation
17. Sie dient ausschliesslich dem read-only Kontextabruf. Der bestehende
S2-KJ-Binder uebernimmt die Kandidatenwerte im selben Probevorgang; die
S2-KJ-Projektion erzeugt danach `TwoAreaPerceptualContext336`.

Die maskierte Wahrnehmung `H_MASKED` folgt in einem strikt spaeteren Block
mit neuen RGB-/PCM-, Quellen-, Zeit- und Probendigests. Weder diese Probe
noch `H_FULL` darf eine Formation oder ein Baselinetraining erreichen.

Der Kontextverbraucher erhaelt nur:

- die maskierte Probe und ihre Positionsmaske;
- das fertige S2-KJ-Kontextobjekt;
- die ausdrueckliche Rolle `B_STABLE_VISUAL`.

Er erhaelt weder die Werte der Vollprobe noch den
`ValidatedPerceptualFinding336V1`, Formationstabellen, Fixture-IDs oder
Auswertungsziele. `B_STABLE_AUDITORY`, B4 und Fast bleiben sichtbar gebunden,
werden aber nicht als Fuellquelle verwendet.

## Getrennte Zielwertfixture

Eine unabhaengige `EvaluationTarget336V1` bindet die vollstaendigen 288
Rezeptorwerte von `H_FULL`, den RGB-Fixturedigest und den Evaluationsplandigest.
Sie ist eine eigene Evaluationswurzel und kein Elternbeleg des
Ausfuehrungspfads. Erst nach vollstaendigen Armresultaten darf der reine
Auswerter diese Wurzel mit der Laufbeweiskette verbinden.

Dass Vollprobe und Evaluationsziel denselben Wahrnehmungsinhalt besitzen,
wird erst in dieser spaeten Bindung festgestellt. Kein Verbraucher und keine
Baseline erhaelt die Zielrolle oder den Zielobjektdigest.

## Fuenf Vergleichsarme

Alle Arme erhalten dieselbe bereits analysierte `H_MASKED`-Wahrnehmung und
dieselbe Maske. Kein Arm erzeugt eine zweite Rezeptor- oder Memoryprobe.

### `CURRENT_PERCEPTION_ONLY`

Gibt die 32 sichtbaren Werte unveraendert aus und laesst alle 256
Maskenpositionen ungeliefert. Der Okkluderwert wird nicht als Rekonstruktion
uebernommen.

### `FROZEN_FIRST_PROTOTYPE`

Der unabhaengige eingefrorene Erstprototyp wird aus dem zweiten
`T_PLUS`-Trainingswert gebildet. Die vorgeschaltete Vollprobe liegt mit
`8/765 > 0,01` ausserhalb seiner visuellen Schwelle. Der Arm liefert deshalb
keine Maskenwerte.

### `REPLAY_NEAREST_EXEMPLAR`

Replay speichert ausschliesslich die 17 reduzierten Trainingsbeispiele.
`H_FULL` liegt zu jedem positiven Einzelbeispiel bei mindestens
`8/765 > 0,01`; Distraktoren liegen weiter entfernt. Replay liefert deshalb
keine Maskenwerte. Tie-Breaking darf diesen Schwellenausgang nicht aendern.

### `ADAPTIVE_B_STABLE_CONTEXT`

Dieser Arm verwendet ausschliesslich den explizit benannten visuellen
S2-KJ-Kandidaten. Er prueft die 32 sichtbaren Werte exakt, laesst sie
unveraendert und uebernimmt genau die 256 Werte des Kandidaten an `MASKED`.
Jeder Konflikt oder jede fehlende Rollenbindung stoppt ohne Teilfuellung.

### `DIRECT_ADAPTIVE_MASK_FILL`

Die staerkste Baseline fuehrt eine eigene adaptive Prototyplinie ueber exakt
dieselben acht positiven Trainingswerte. Sie liest weder Memory noch S2-KJ
und ruft den Kontextverbraucher nicht auf. Nach eigener Vollprobenpruefung
kopiert sie direkt dieselben 256 adaptiven Prototypwerte. Funktions- und
Arbeitsbudget sind zum Kontextarm identisch.

## Rekonstruktionsmetrik

Der Auswerter berechnet erst nach Abschluss aller Arme fuer jede der 288
Positionen normalisierten absoluten Fehler. Eine ungelieferte Maskenposition
erhaelt vorab fest den maximal moeglichen Fehlerbeitrag `1,0`; damit ist
fehlende Ausgabe nicht gegen eine numerische Schaetzung bevorteilt.

```text
loss = (
  Summe |output_i - target_i| fuer gelieferte Werte
  + Anzahl ungelieferter Maskenwerte
) / 288
```

Vorab folgt daraus:

| Arm | gelieferte Maskenwerte | erwarteter Loss |
| --- | ---: | ---: |
| Current only | 0 | `256/288 = 8/9` |
| Frozen | 0 | `8/9` |
| Replay | 0 | `8/9` |
| adaptiver B-Kontext | 256 | etwa `0,0086106624183` |
| direkte adaptive Baseline | 256 | identisch zum Kontextarm |

Zusaetzlich werden Masken-MAE, Vollvektor-Loss, gelieferte Positionen,
sichtbare Unveraendertheit, Herkunft und alle Vor-/Nachzustandsdigests
getrennt berichtet.

## Endlicher Umfang und Ressourcen

| Ressource | Gebundene Anzahl oder Obergrenze |
| --- | ---: |
| Memorygeschichten | 1 |
| Memoryformationen | 17 |
| vollstaendige Memory-Kontextproben | 1 |
| maskierte Verbraucherproben | 1 |
| funktionale AV-Bloecke | 19 |
| Evaluation-only-Zielframes | 1 |
| visuelle Rezeptoranalysen | 20 |
| auditive Hop-Aufrufe | 190 |
| Memory-Top-Level-Operationen | 72 |
| Baseline-Trainingsoperationen, drei je Formation | 51 |
| Baseline-Vollproben | 3 |
| S2-KJ Binder-/Projektionsoperationen | 7 |
| Maskenbindung und Armoperationen | 6 |
| Evaluationsbindung und Auswertung | 2 |
| funktionale Top-Level-Operationen gesamt | 161 |
| reduzierte Rezeptorwerte | 6.672 |
| gestreamte Rohbytes gesamt | 124.780.800 |
| maximal gleichzeitig Frame plus Hop | 6.222.720 Bytes |
| maximaler numerischer Memoryzustand | 44.544 Bytes |
| maximale numerische Baselinezustaende | 51.072 Bytes |
| S2-KJ-Kontextausgabe | 65.536 Bytes |
| Memory-L1-Obergrenze | 69.504 Terme |
| Baseline-L1-Obergrenze | 8.736 Terme |
| Evaluationsfehlerterme | 1.440 |
| sichtbare Kontextvergleiche | 64 |
| maskierte Kopien | 512 |

Die 161 Operationen sind Funktionsoperationen, keine neue Recorderregistry.
Eine spaetere kleine Implementierung muss sie aus vorhandenen privaten
Formation-, Probe-, S2-KJ- und Auswerterbausteinen ableiten. Native Laufzeit
und Prozessspeicher werden getrennt berichtet. Rohbytes, Feldsnapshot,
Zielwerte und Sollrollen gehoeren nicht in Memory- oder Kontextbelege.

## Erfolg, Falsifikation und technische Ungueltigkeit

`S2KK_LEARNED_VISUAL_CONTEXT_UTILITY_CONFIRMED_DIRECT_ADAPTIVE_FILL_EXPLAINS`
ist nur zulaessig, wenn gemeinsam gilt:

1. `H_FULL` und `H_MASKED` kamen in keiner Formation und keinem
   Baselinetraining vor.
2. Der positive visuelle Slow-Slot besitzt Support 3; `H_FULL` ist nach den
   Distraktoren weder in B4 noch Fast, aber in `B_STABLE_VISUAL` anwendbar.
3. Current-only, Frozen und Replay liefern keinen Maskenwert.
4. Der Kontextarm liefert genau 256 Werte und besitzt geringeren Loss als
   Current-only.
5. Alle 32 sichtbaren Werte bleiben in allen Armen unveraendert.
6. Die unabhaengige direkte adaptive Baseline ist wert-, positions- und
   kostenidentisch zum Kontextarm.
7. Memory-, Probe-, S2-KJ-, Baseline- und Verbraucherzustaende bleiben bei
   allen read-only Schritten unveraendert.

Bei vollstaendiger gueltiger Beweiskette ist der Vertrag fachlich
falsifiziert, wenn ein erwarteter Match-, Fuell-, Fehler- oder
Read-only-Befund abweicht. Ein solcher Lauf darf nicht durch neue Masken,
Schwellen oder Wiederholung umgedeutet werden.

`NOT_EVALUABLE` gilt ausschliesslich bei Quellen-, Zeit-, Rollen-, Owner-,
Digest-, Dimensions-, Zustands-, Ledger- oder Aufzeichnungsbruch. Eine
Materialisierungsabweichung vor dem ersten Memoryaufruf bleibt
`START_BLOCKED_FIXTURE_MATERIALIZATION`.

## Aussagegrenze und naechster zulassbarer Schritt

Ein Erfolg belegt, dass eine erfahrungsabhaengig gebildete visuelle
Slow-Memory eine spaetere, explizit maskierte Wahrnehmungsverarbeitung
gegenueber Current-only verbessert. Die direkte adaptive Fuellbaseline darf
und soll den Nutzen vollstaendig erklaeren. Der Befund waere begrenztes
perzeptives Lernen plus transparente Kontextnutzung, keine besondere
MCM-Physik.

Nicht nachgewiesen waeren automatische Maskenerkennung, Kontextwahl,
Objektverstaendnis, Semantik, Feldrueckwirkung oder allgemeine
Ansichtsinvarianz. Der naechste zulassbare Schritt ist eine kleine private
Fixture-, Verbraucher-, Baseline- und Auswerterimplementierung mit neutraler
Qualifikation. Ein realer Funktionslauf benoetigt danach eine eigene
Freigabe; neue Lauf-, Recorder- oder Plattforminfrastruktur ist nicht
begruendet.
