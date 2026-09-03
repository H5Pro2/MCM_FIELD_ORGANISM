# S2-KY - Auditive Teilhinweis-Geometriematerialisierung

## Ergebnis

```text
S2KY_AUDIO_PARTIAL_CUE_GEOMETRY_MATERIALIZED
```

Die vorab festgeschriebene PCM-Geometrie erfuellt alle acht Distanzgates und
alle acht Beziehungsklassen des S2-KX-Vertrags. Dies ist ein
Materialisierungsbefund vor Memorybeginn, noch kein Teilhinweisabruf und kein
Memorybefund.

## Gebundene Ausfuehrung

- Quellcommit: `844043e2ac8cfbb50e236d45c28ce109533d767c`
- Plan: `docs/S2KY_AUDITORY_PARTIAL_CUE_GEOMETRY_PLAN.json`
- tatsaechlicher Aufruf: `python -m tools._s2ky_auditory_partial_cue_geometry`
- Exit-Code: `0`
- Ergebnisdigest: `f98a23c3054ef3ee725c333897b9b2b0f0122eae7fbe632149dd134362cb7d5e`
- SHA-256 der Ergebnisdatei: `87ac9aed39e6f3cd63f4d3cee24873a7e67357ce5cd9e5ed1ccc353d407d1dc3`

Ein vorheriger Launcheraufruf mit dem Dateipfad endete bereits beim
Python-Paketimport mit `ModuleNotFoundError`. Zu diesem Zeitpunkt waren weder
Plan noch PCM geladen, kein Rezeptor aufgerufen und kein Ergebnisverzeichnis
angelegt. Dieser Start war `START_BLOCKED` und keine Materialisierung. Der
vorab gebundene Quellstand und die Fixture blieben unveraendert.

## Umfang

| Position | Istwert |
| --- | ---: |
| Materialisierungen | 1 |
| PCM-Fenster | 6 |
| Audiohops | 60 |
| Rezeptorabschluesse | 6 |
| Beziehungsklassen | 8 |
| Memoryaufrufe | 0 |
| Slotscanaufrufe | 0 |
| Kontextaufrufe | 0 |
| Feldaufrufe | 0 |
| Parametersuchen | 0 |
| Ersatzfixtures | 0 |

Jedes Fenster bestand aus 4.800 echten Float32-Samples und wurde in zehn
geordneten 480-Sample-Hops durch einen frischen unveraenderten
`BroadbandHearingPath` gefuehrt. Der Beleg enthaelt die tatsaechlichen
48-Werte-Rezeptorausgaben, aber keine PCM-Rohsamples.

## Gemessene Distanzen

| Linke Rolle | Rechte Rolle | Metrik | Istwert | gebundenes Intervall |
| --- | --- | --- | ---: | ---: |
| `CUE_LOW` | `CANDIDATE_PLUS` | beobachtete 24 Baender | `7.036867813356767e-11` | `0..0.000001` |
| `CUE_LOW` | `CANDIDATE_MINUS` | beobachtete 24 Baender | `1.2327556304197705e-10` | `0..0.000001` |
| `CANDIDATE_PLUS` | `CANDIDATE_MINUS` | beobachtete 24 Baender | `9.817018673792375e-11` | `0..0.000001` |
| `CANDIDATE_HIGH` | `CANDIDATE_PLUS` | beobachtete 24 Baender | `0.03167999726488322` | `0.030..0.033` |
| `CUE_LOW` | `CANDIDATE_PLUS` | volle 48 Baender | `0.014399999088649598` | `0.0138..0.0150` |
| `CUE_LOW` | `CANDIDATE_MINUS` | volle 48 Baender | `0.004799999442841757` | `0.0045..0.0051` |
| `CANDIDATE_PLUS` | `CANDIDATE_MINUS` | volle 48 Baender | `0.00959999972837876` | `0.0090..0.0102` |
| `CANDIDATE_HIGH` | `CANDIDATE_PLUS` | volle 48 Baender | `0.02064000018821595` | `0.0201..0.0212` |

Damit sind eindeutige A- und B-Beziehungen, oeffentliche A/B-Mehrdeutigkeit,
interne A-Bankmehrdeutigkeit, B4/Fast-Konflikt, interne Slow-Mehrdeutigkeit,
gueltige Abwesenheit und Nichtanwendbarkeit geometrisch erreichbar.

## Filterbank und Fast-Regel

U- und V-Basis besitzen wegen Hann-Fenster und FFT numerisch in allen 48
Baendern von null verschiedene Werte. Es wurde keine disjunkte Unterstuetzung
behauptet. Gemessen wurden:

```text
mittlere V-Energie in beobachteten Baendern = 4.6485694187452486e-10
mittlere U-Energie in maskierten Baendern   = 6.272936030269758e-09
minimaler gemeinsamer voller L1-Anteil      = 1.7603214854268592e-09
```

Die Fast-`AND`-Regel wurde mit derselben realen auditiven Distanz
`0.00959999972837876` geprueft:

```text
Audio <= 0.2 AND Video = 0.0 <= 0.2 -> MATCH
Audio <= 0.2 AND Video = 1.0 >  0.2 -> NO_MATCH
```

Damit bleibt auch die komplementaere Trennungsregel korrekt:

```text
Audio > 0.2 OR Video > 0.2 -> getrennt
```

## Aussagegrenze

S2-KY bestaetigt nur, dass die fest gebundene 24/24-PCM-Geometrie mit dem
realen Audiorezeptor materialisierbar ist. Nicht bestaetigt sind
Slotscanfunktion, Memoryabruf, automatische akustische Verdeckungserkennung,
Audiovervollstaendigung, Crossmodalitaet oder Feldwirkung.

Nach diesem Befund duerfen die private S2-KX-Slotscanfunktion, eine unabhaengige
Direktbaseline und neutrale Vertragstests unmittelbar implementiert werden.
