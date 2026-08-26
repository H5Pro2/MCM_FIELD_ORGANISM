# S1-S: Passive Vollmatrixauswertung Phasentrennung

Stand: 2026-08-09

Phase: `FORMATION_EXTENDS_BEYOND_FIXED_BOUNDARY`

Mechanik: `PHASE_CURVES_LINEARLY_EXPLAINED`

Formaler Forschungslauf: nein

## Ziel

S1-S wertet die 32 in S1-Q vorregistrierten und in S1-R technisch gebundenen
Zellen vollstaendig im Speicher aus. Vorproben-M-Lage und spaetere
Probeantwort besitzen getrennte 2/4-Nachweisboeden, Fensterrollen und lineare
Baselinereste.

## Kontrollstatus

| Kontrolle | Ergebnis |
|---|---|
| 32 eindeutige Zellen | bestanden |
| Quellenmarginalien | bestanden |
| S/H-Angleichung vor P | bestanden |
| Massenbilanz und Nichtnegativitaet | bestanden |
| P0-/`eta=0`-/M-neutralisierte Sentinels | bestanden |
| exakte Wiederholung | bestanden |
| endliche Zellmetriken | bestanden |

Keine Grenze oder Schwelle wurde nach Kenntnis der Ergebnisse veraendert.

## Kompaktergebnis

```text
nachweisbare Vorproben-M-Zellen:        29 / 32
nachweisbare Probeeffektzellen:         29 / 32
maximaler linearer M-Rest:              0.03741898881868446
maximaler linearer Probeeffektrest:     0.043589721634606275
lineare Aequivalenzgrenze:              0.05
```

## Fensterrollen

| Messrolle | Dosis | Quellenform | frueh 0.0-0.2 s | spaet 0.2-1.6 s |
|---|---:|---|---|---|
| Vorproben-M | 1 | wiederholt | Anstieg | gemischt |
| Vorproben-M | 1 | kontinuierlich | Anstieg | gemischt |
| Vorproben-M | 8 | wiederholt | Anstieg | Abnahme |
| Vorproben-M | 8 | kontinuierlich | Anstieg | gemischt |
| Probeeffekt | 1 | wiederholt | Anstieg | Abnahme |
| Probeeffekt | 1 | kontinuierlich | Anstieg | Abnahme |
| Probeeffekt | 8 | wiederholt | gemischt | Abnahme |
| Probeeffekt | 8 | kontinuierlich | Anstieg | Abnahme |

Alle vier Vorproben-M-Kurven zeigen im fest gebundenen fruehen Fenster einen
technischen Anstieg. Im spaeten Fenster nimmt nur die wiederholte Dosis-8-
Kurve rein ab; die drei anderen M-Kurven enthalten weiterhin mindestens
einen Anstieg und einen Abfall oberhalb ihrer lokalen Toleranzen.

Alle vier Probeeffektkurven nehmen im spaeten Fenster geordnet ab. Damit
reicht die spaetere Probeantwort allein nicht aus, um die Phase der internen
M-Lage zu bestimmen.

## Hauptentscheidung

```text
FORMATION_EXTENDS_BEYOND_FIXED_BOUNDARY
```

Die engere Rolle `FIXED_BOUNDARY_FORMATION_THEN_ATTENUATION` ist nicht
zulaessig. Die feste Grenze 0.200 Sekunden trennt den internen M-Verlauf
nicht fuer alle vier Kurven in reinen Aufbau und reine Abnahme.

Diese technische Rolle sagt nicht, dass eine biologische Bildung,
Konsolidierung oder Erinnerung stattfindet. Sie besagt nur, dass mindestens
eine M-Kurve nach der vorab fixierten Grenze noch einen nachweisbaren
Anstieg enthaelt.

## Mechanikerlaerung

```text
PHASE_CURVES_LINEARLY_EXPLAINED
```

Alle jeweils nachweisbaren Vorproben-M- und Probeeffektvektoren bleiben
innerhalb der festen 5-Prozent-Grenze der linearen gekoppelten Baseline. Der
groesste M-Rest betraegt rund 3.742 Prozent, der groesste Probeeffektrest
rund 4.359 Prozent.

Die Fensterstruktur benoetigt im geprueften Korridor keine neue Feldphysik.
Sie bleibt eine Eigenschaft der transparenten F3-Engineeringreferenz.

## Testergebnis

Der fokussierte, in einem frischen Prozess reproduzierte Verbund besteht mit:

```text
4 passed
32 subtests passed
118.82 s
```

Die bekannte Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen
Cachepfad.

## Aussagegrenze

S1-S belegt keine Praegung, kein Lernen, kein Vergessen und kein MCM-Memory.
Die externen Zeitgrenzen sind keine Feldzeit und kein innerer Zeitkontext.
Es gibt keinen Befund zu Semantik, Organisation, Topologie,
Selbstregulation, innerem Kontext oder KI.

Es gab keinen Browserstart, keine reale Sensorik, keinen externen Runner,
keinen Report und keine neue Laufnummer. Lauf 197 sowie die geschlossenen
Zweige bleiben unberuehrt.

## Bester naechster Schritt

S1-T verlaengert die Zeitachse nicht nachtraeglich. Stattdessen zerlegt es
zuerst statisch die bekannte F3-/lineare M-Aenderung in ihre bereits
existierenden lokalen Beitragsrollen ueber die festen S1-Q-Intervalle.

Ziel ist ein vorregistrierbarer Komponentenobserver, der fuer ausgewaehlte
Dosis-1-/Dosis-8-Kurven bilanziert, welcher transparente Gleichungsbeitrag
die spaeten M-Anstiege und -Abfaelle traegt. Erst danach kann entschieden
werden, ob eine weitere Zeitgrenze eine neue Frage beantwortet oder nur die
bekannte lineare Relaxation verlaengert.

## Spaeterer Richtungsstand S1-T

S1-T hat diese Beitragszerlegung inzwischen statisch vorregistriert. Die
direkten M-Rollen sind massenausgleichender Transport und
aktivierungsgradientengetriebene Verschiebung; die reziproke Rueckwirkung
veraendert S und damit spaetere M-Raten. H besitzt in der aktiven Gleichung
keinen Rueckpfad. Eine Ausfuehrung steht noch aus.
