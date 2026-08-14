# S1-R: Implementierung In-Memory-Phasentrennungsmatrix

Stand: 2026-08-09

Implementierungsstatus: `CELL_ADAPTER_IMPLEMENTED_NOT_CLASSIFIED`

Formaler Forschungslauf: nein

## Ziel

S1-R implementiert den in S1-Q vorregistrierten zellweisen Adapter fuer die
engere Phasentrennungsmatrix. Er stellt feste Quellen, Vorproben-M-Lage und
spaetere Probeantwort bereit, berechnet aber keine Fenster- oder
Hauptklassifikation.

## Implementierung

Der Adapter
[`s1r_phase_separation_matrix.py`](../mcm_field_organism/s1r_phase_separation_matrix.py)
bindet:

- Dosis 1 und 8;
- `repeated-supports` und `continuous-support`;
- acht feste Nullkontaktgrenzen von 0.000 bis 1.600 Sekunden;
- die unverrueckbare technische Phasengrenze 0.200 Sekunden;
- F3 bei Verfeinerung 2 und 4;
- lineare gekoppelte Baseline bei Verfeinerung 4;
- P0, `eta=0` und externe M-Neutralisierung als Sentinelarme;
- den vollstaendigen Vorproben-M-Differenzvektor;
- den vollstaendigen spaeteren S/H-Probeeffektvektor.

Nullkontakt wird in Supports von hoechstens 0.100 Sekunden zerlegt. Die
bereits in S1-O vorhandenen Grenzen 0.200, 0.800 und 1.600 Sekunden behalten
damit ihren bisherigen Ereignispfad.

## Technische Kontrollen

| Kontrolle | Ergebnis |
|---|---|
| 32 eindeutige Zellen | bestanden |
| acht exakte Nullkontaktgrenzen | bestanden |
| Quellenmarginalien je Randdosis | bestanden |
| S/H-Angleichung vor P | bestanden |
| Gesamtmasse und Nichtnegativitaet | bestanden |
| P0- und `eta=0`-Sentinels | bestanden |
| M-neutralisierte Sentinels | bestanden |
| S1-O-Gleichheit bei 0.200 s | bestanden |
| exakte Wiederholung lange Randzelle | bestanden |
| keine Klassifikations-/Runtimeautoritaet | bestanden |

Die aktive neue 0.025-Sekunden-Zelle besitzt getrennt eine von null
verschiedene Vorproben-M-Differenz und eine von null verschiedene spaetere
Probeantwort. Das ist nur ein technischer Pfadnachweis und keine
Phasenklassifikation.

## Testergebnis

Der fokussierte S1-R-Verbund besteht mit:

```text
7 passed
28 subtests passed
```

Gemeinsam mit dem unveraenderten S1-O-Adapter besteht der direkte Verbund
mit:

```text
12 passed
40 subtests passed
33.61 s
```

Die bekannte Pytest-Cachewarnung `WinError 183` betrifft ausschliesslich den
lokalen Cachepfad.

## Aussagegrenze

S1-R hat weder die 32-Zellen-Vollmatrix ausgefuehrt noch die in S1-Q
vorregistrierten Fensterrollen berechnet. Es gibt keinen Befund zu Bildung,
Abschwaechung, Erhaltung oder internem Zeitverlauf.

Insbesondere belegt S1-R keine Praegung, kein Lernen, kein Vergessen, keine
Feldzeit, kein Memory, keinen inneren Kontext und keine Organisation,
Topologie, Selbstregulation, Semantik oder KI.

Es gab keinen Browserstart, keine reale Sensorik, keinen Runner, keinen
Report und keine neue Laufnummer. Lauf 197 sowie die geschlossenen Zweige
bleiben unberuehrt.

## Bester naechster Schritt

S1-S implementiert den begrenzten passiven Vollmatrixkompositor fuer die
32 S1-Q-Zellen. Er berechnet zellbezogene 2/4-Nachweisboeden, getrennte
Vorproben-M- und Probeeffektfenster, die vorregistrierte Hauptrolle und die
lineare Mechanikrolle. Schwellen, Phasengrenze und Zellauswahl bleiben
unveraendert; es entsteht kein Report und keine Forschungslaufnummer.

## Spaeterer Auswertungsstand S1-S

S1-S hat die 32 gebundenen Zellen inzwischen passiv und reproduzierbar
klassifiziert. Die feste 0.200-Sekunden-Grenze trennt die interne M-Lage
nicht vollstaendig: Drei spaete M-Fenster bleiben gemischt. Die technische
Rolle lautet `FORMATION_EXTENDS_BEYOND_FIXED_BOUNDARY`; die Kurven bleiben
linear erklaert.
