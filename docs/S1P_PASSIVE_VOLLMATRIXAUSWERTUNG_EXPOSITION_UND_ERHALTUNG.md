# S1-P: Passive Vollmatrixauswertung Exposition und Erhaltung

Stand: 2026-08-09

Dosis: `MONOTONIC_DOSE_GRADATION`

Nullkontakt: `NONMONOTONIC_NULL_CONTACT_RESPONSE`

Segmentierung: `EVENT_SEGMENTATION_SENSITIVE`

Mechanik: `CURVE_LINEARLY_EXPLAINED`

Formaler Forschungslauf: nein

## Ziel

S1-P komponiert die 32 in S1-N vorregistrierten und in S1-O technisch
gebundenen Zellen vollstaendig im Speicher. Jede Zelle wird mit F3 bei
Verfeinerung 2 und 4 sowie mit der linearen gekoppelten Baseline bei
Verfeinerung 4 ausgewertet.

Die Auswertung verwendet ausschliesslich die vorregistrierten zellbezogenen
Nachweisboeden und vier getrennten Klassifikationsrollen.

## Implementierung

Der passive Kompositor
[`s1p_exposure_retention_evaluator.py`](../mcm_field_organism/s1p_exposure_retention_evaluator.py)
bindet:

- 32 unveraenderte Zellen;
- 96 Hauptzellpfade;
- vollstaendige S/H-Effektvektoren;
- zellbezogene 2/4-Konvergenzboeden;
- lineare Effektvektorreste;
- Dosis- und Nullkontaktordnung mit lokaler Paartoleranz;
- Segmentierungsreste zwischen wiederholter und kontinuierlicher Quelle;
- acht technische Erhaltungshorizonte;
- P0-, `eta=0`- und M-neutralisierte Sentinelkontrollen;
- exakte Wiederholung einer langen Randzelle.

Die Auswertung ist innerhalb eines Prozesses einmalig gecacht. Sie besitzt
keine Runtime-Rueckschreibung und erzeugt keine Ergebnisdatei.

## Kontrollstatus

| Kontrolle | Ergebnis |
|---|---|
| 32 eindeutige Zellen | bestanden |
| Quellenmarginalien | bestanden |
| exakte S/H-Angleichung | bestanden |
| Massenbilanz und Nichtnegativitaet | bestanden |
| P0-/`eta=0`-/M-neutralisierte Sentinels | bestanden |
| exakte Wiederholung | bestanden |
| endliche Zellmetriken | bestanden |

Alle Klassifikationen sind damit technisch gueltig. Keine Schwelle wurde
nach Kenntnis der Matrix veraendert.

## Kompaktergebnis

```text
detected cells:                         27 / 32
maximum linear relative residual:       0.04073372905751632
linear equivalence limit:               0.05
maximum segmentation vector Linf:       0.0010036850076167196
```

Alle acht Dosis-/Quellenform-Kombinationen besitzen bei 1.6 Sekunden noch
mindestens eine nachweisbare technische Wirkung. Ihre Horizonte werden
deshalb bei 1.6 Sekunden rechtszensiert. Daraus folgt keine Aussage ueber
laengere Dauer.

## Dosisordnung

```text
MONOTONIC_DOSE_GRADATION
```

Bei Nullkontaktdauer 0.0 Sekunden fallen die Effekte ueber die Dosen 1, 2, 4
und 8 innerhalb der zellbezogenen Toleranzen nicht ab; mindestens ein
Dosisuebergang ist streng groesser.

Dies ist eine technische Dosisgradation aus gemeinsam wachsender
Kontaktanzahl und kumulierter Kontaktdauer. Sie trennt noch nicht Wiederholung
von Gesamtexposition und wird nicht Praegung genannt.

## Nullkontaktordnung

```text
NONMONOTONIC_NULL_CONTACT_RESPONSE
```

Mindestens eine Dosis-/Quellenform-Kurve steigt mit laengerem Nullkontakt
oberhalb ihrer Toleranz an. Damit ist die aktuelle Kurve keine reine
Abnahmekurve.

Dieser Befund ist mit der bereits technisch bekannten Ereigniskausalitaet
vereinbar: Unmittelbar am Kontaktabschluss kann M noch uniform sein und sich
erst in spaeterer Feldzeit aus der vorhandenen S-Lage veraendern. S1-P
entscheidet aber nicht nachtraeglich, dass dies die einzige Ursache ist.

Solange Bildungsphase und spaetere Abnahme nicht getrennt sind, sind Aussagen
ueber Erhaltung, Zerfall oder Vergessen gesperrt.

## Ereignissegmentierung

```text
EVENT_SEGMENTATION_SENSITIVE
```

Mindestens eine wiederholte und dauerangeglichene kontinuierliche Quelle
unterscheidet sich im vollstaendigen spaeteren Effektvektor oberhalb des
zellbezogenen Nachweisbodens. Der maximale Vektor-Linf-Unterschied betraegt
`0.0010036850076167196`.

Die Quellen besitzen gleiche integrierte Dauer-/L1-/L2-Marginalien, aber
verschiedene Abschlussereignisse. Der Befund zeigt technische Sensitivitaet
fuer zeitliche Segmentierung, keine erlernte Syntax oder Ereignisbedeutung.

## Mechanikerlaerung

```text
CURVE_LINEARLY_EXPLAINED
```

Alle 27 nachweisbaren Zellen bleiben mit ihrem vollstaendigen Effektvektor
innerhalb der festen 5-Prozent-Grenze der linearen gekoppelten Baseline. Der
groesste relative Rest betraegt `0.04073372905751632` beziehungsweise rund
4.073 Prozent.

Die Dosis- und Segmentierungsbefunde benoetigen im geprueften Korridor keine
neue Feldphysik. F3 bleibt eine transparente endliche Engineeringreferenz.

## Testergebnis

Der fokussierte Vollmatrixverbund besteht mit:

```text
4 passed
32 subtests passed
137.46 s
```

Die Klassifikationen wurden in einem getrennten kompakten Konsolenlauf
bitgleich erneut berechnet. Es wurde keine Datei erzeugt. Die bekannte
Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen Cachepfad.

## Aussagegrenze

S1-P ist eine passive technische In-Memory-Vollauswertung, kein formaler
Forschungslauf. Der Stand belegt nicht:

- Praegung, Lernen, Vergessen oder Rekonstruktion;
- MCM-Memory oder organisches Memory;
- Cluster- oder Feldzeitverdichtung;
- relative Feldzeit oder inneren Kontext;
- Semantik, Organisation, Topologie, Selbstregulation oder KI.

Es gab keinen Browserstart, keine reale Sensorik, keinen externen Runner,
keinen Report und keine neue Laufnummer. Lauf 194 und Lauf 197 bleiben
unberuehrt.

## Bester naechster Schritt

S1-Q bindet statisch eine kleine Ursachenpruefung der nichtmonotonen
Nullkontaktantwort. Sie muss Bildungsphase und spaetere Abnahme trennen,
bevor weitere Erhaltungsdauern untersucht werden.

Der kleinste zulaessige Weg verwendet nur ausgewaehlte Dosis-1- und
Dosis-8-Zellen, dichtere feste fruehe Nullkontaktgrenzen sowie F3 und lineare
Baseline. Es wird weder eine Peakzeit nachtraeglich ausgewaehlt noch
Vergessen, Konsolidierung oder Feldzeit behauptet.
