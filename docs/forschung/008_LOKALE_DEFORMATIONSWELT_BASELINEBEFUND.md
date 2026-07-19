# Lokale Deformationswelt: Baselinebefund

## Status

Passiver Grenzbefund auf `E2 / FIXED_LOCAL_INTERPOLATION_SUFFICIENT`.

Grundlage ist die
[vorregistrierte lokal stetige Deformationswelt](../architektur/060_MINIMALE_LOKAL_STETIGE_DEFORMATIONSWELT.md).

## Lauf

```text
Beobachtungen:                         336
faire identifizierbare Holdouts:       110
D3-Holdouts:                            44
D4-Holdouts:                            66
D5-Paarungsnullen:                       6
Runtime- oder Memoryänderung:           nein
```

Welt-Digest:

```text
ecce078b165d20afc4424cbf7829212e67c29daf369f3558f892067be43f4a28
```

Baseline-Digest:

```text
386543c684b05dcdafcb2663f45e65109f722c685436a8ff216a9170ab7f0bec
```

## Hauptbefund

Die feste stückweise lineare Baseline L4 trägt:

```text
D3:       44 / 44
D4:       66 / 66
gesamt:  110 / 110
```

Sie benötigt tatsächlich begrenzende Nachbarkontakte. In den stationären D0-
und D1-Zweigen gibt sie keine Fortsetzung aus.

L9, das vollständige Kontaktarchiv mit demselben festen Interpolator, gewinnt
gegenüber L4 keine zusätzliche Funktion.

## D5

D5 erhält die Eintritts- und Austrittsränder, zerstört aber ihre lokale
Paarung.

L4 erreicht dort nur:

```text
2 / 6
```

Die zwei Treffer entstehen an einer zufällig weiterhin passenden Mittellage.
Die lokale Beziehung als Ganzes ist nicht erhalten.

## Unveränderte Feldruntime

L0 liest ausschließlich den bekannten schnellen Feldzustand vor dem
Holdoutaustritt. Nach der verdeckten Phase besitzt er in allen 336 Zweigen
keine eindeutige Austrittsantwort:

```text
Abdeckung: 0 / 336
```

Damit trägt die heutige Runtime keine eigene gelernte lokale
Fortsetzungsfunktion.

## Gesamtscores

Die Gesamtscores enthalten absichtlich auch D0 bis D2 sowie D5 und sind
deshalb nicht die primäre Erfolgsmetrik.

```text
Baseline  Abdeckung  Treffer / Antworten
L0          0,000      0 /   0
L1          0,929     44 / 312
L2          0,857     73 / 288
L3          0,857    138 / 288
L4          0,833    138 / 280
L5          0,786     62 / 264
L6          0,857    144 / 288
L7          0,929     66 / 312
L8          0,929     86 / 312
L9          0,833    138 / 280
```

## Interpretation

Gezeigt ist:

```text
lokal verteilte Kontaktpaare
-> feste stückweise lineare Rekonstruktion
-> exakte faire Holdoutfortsetzung
```

Nicht gezeigt ist:

- organisches Memory;
- Bildung einer inneren Feldtopologie;
- natürliche Lösung und Wiederbindung;
- semantische Resonanz;
- Reflexionsrückwirkung;
- Feldintelligenz.

Die Welt hat ihren Zweck erfüllt: Sie bestimmt genauer, welche lokale
Beziehungsinformation eine spätere Trägerfunktion bewahren müsste. Sie
begründet aber keine fest programmierte Interpolation im Organismus.

## Stopplinie

L4 erklärt alle fair identifizierbaren Holdouts vollständig. Deshalb wird aus
diesem Lauf weder eine Memory-Rolle noch eine Updategleichung oder
Runtimeerweiterung abgeleitet.

## Nächster Schritt

Die anschließende
[feldgetragene Beziehungswirkungsgrenze](../architektur/061_FELDGETRAGENE_BEZIEHUNGSWIRKUNGSGRENZE.md)
bestimmt den verbleibenden Mangel inzwischen nicht als schwierigere
Vorhersage, sondern als fehlende kausale Feldwirkung vor dem unbekannten
Austritt. Eine bloße digitale Nachbildung des äußeren Interpolators bleibt
eine statische Sackgasse.
