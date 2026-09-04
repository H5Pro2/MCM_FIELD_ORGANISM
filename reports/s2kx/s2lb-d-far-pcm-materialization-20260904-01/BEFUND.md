# S2-LB - D_FAR PCM-Materialisierungsbefund

## Status

`S2LB_D_FAR_PCM_MATERIALIZED`

Die einzige vorab gebundene Rolle `D_FAR` wurde einmal durch den
unveraenderten Default-Live-Audiorezeptor materialisiert. Es gab keine
Parametersuche, keine Ersatzfixture und keinen Memory-, Slotscan-, Kontext-
oder Feldaufruf.

## Bindungen

| Bindung | Wert |
| --- | --- |
| Lauf-ID | `s2lb-d-far-pcm-materialization-20260904-01` |
| Quellencommit | `4d5de109d0af2ba9f9ba9f7da1aed891f24316d8` |
| Plan | `docs/S2LB_D_FAR_PCM_MATERIALISIERUNGSPLAN.json` |
| Plandigest | `f77f074cb9df6ada1f182c1bdb4abfb5fe233ca923f8a7bd99334c9c13a85d48` |
| Ergebnisdigest | `12bb7334dd4fa4c05b07067235bf29a3b522a66dd063282f1b01bd6d929a62e1` |
| Ergebnisdatei SHA-256 | `1fd9ab971acbdb1bcacd6dde7c69a4ba485edd7056697ed240d00d465a9b05d0` |
| Rezeptorwertedigest | `4cb2bf1dda6e02d9c5e482bfc749b3efe5910e46ea72e8195f376a67874774f0` |

Der Plandigest wurde aus der gespeicherten Ergebnisdatei uebernommen. Das
Ergebnis enthaelt alle 48 reduzierten Rezeptorwerte, aber keine PCM-Rohsamples.

## Versiegeltes Rezept

`D_FAR` ist ein deterministischer logarithmischer Rechteck-Chirp:

```text
Abtastrate:       48000 Hz
Fenster:          4800 Samples / 100 ms
Startfrequenz:    50 Hz
Endfrequenz:      890 Hz
Anfangsphase:     pi/7
Skalierung:       float32(0.98) = 0.9800000190734863
Clipping:         nein
Normalisierung:   nein
```

Die gemessenen Samplegrenzen waren exakt
`-0.9800000190734863..0.9800000190734863` und lagen damit innerhalb
`[-1,1]`.

## Distanzgate

Die verbindliche Sicherheitsgrenze war fuer beide Beziehungen strikt
`> 0.205`; die native A-Scanschwelle blieb `0.2`.

| Beziehung | beobachtete L1, 24 Baender | Reserve ueber 0.2 | volle L1, 48 Baender |
| --- | ---: | ---: | ---: |
| D_FAR - CUE_LOW | `0.2215433131751913` | `0.02154331317519126` | `0.15134123368233138` |
| D_FAR - CANDIDATE_HIGH | `0.2333722493498397` | `0.03337224934983968` | `0.16222309977593635` |

Beide beobachteten Beziehungen liegen mit gebundener Reserve auf der
Nichttrefferseite. Die vollen 48-Werte-Distanzen sind ausschliesslich
diagnostisch und ersetzen nicht das Teilscan-Gate.

## Neun Druckformationen

Der D_FAR-Audioanteil wird mit den vorhandenen visuellen S2-JV-D1-D9-
Begleitern gepaart. Die statisch exakt ableitbaren visuellen Distanzen
betragen sowohl gegen X als auch zwischen allen verschiedenen Begleitern
mindestens:

```text
13/24 = 0.5416666666666666 > 0.2
```

Geprueft wurden:

- neun Beziehungen X gegen D1-D9;
- alle 36 paarweisen Beziehungen innerhalb D1-D9;
- die native Regel `audio <= 0.2 AND visual <= 0.2`.

Alle 45 Beziehungen sind gemeinsame Fast-Nichttreffer. Da jede der neun
Druckformationen genau einmal vorkommt, kann sie einen neuen oder ersetzenden
Fast-Slot mit Support 1 erzeugen, aber keinen PPB-Aufruf ausloesen.

## Ausfuehrungsgrenze

| Zaehler | Wert |
| --- | ---: |
| Materialisierungen | 1 |
| PCM-Fenster | 1 |
| Audiohops | 10 |
| Rezeptorabschluesse | 1 |
| Distanzpaare | 2 |
| Parametersuchen | 0 |
| Ersatzfixtures | 0 |
| Memoryaufrufe | 0 |
| Slotscanaufrufe | 0 |
| Kontextaufrufe | 0 |
| Feldaufrufe | 0 |

Ein direkter Skriptstart scheiterte vor dem Projektimport an der lokalen
Modulpfadauflosung. Dabei entstanden weder ein Laufverzeichnis noch PCM-,
Rezeptor- oder Ergebnisarbeit. Die einzige tatsaechliche Materialisierung
erfolgte danach ohne Quell- oder Parameteraenderung ueber den gebundenen
Python-Moduleinstieg.

## Aussage und naechster Schritt

S2-LB schliesst die in S2-LA identifizierte minimale Geometrieluecke:
`D_FAR` ist fuer CUE_LOW und CANDIDATE_HIGH beim auditiven Teilscan sicher
kein A-Treffer. Mit D1-D9 als visuellen Begleitern sind neun getrennte
Fast-Druckformationen statisch moeglich.

Dies ist noch kein Memorybefund. Vor einem realen Lauf ist nur noch eine
kurze statische Zustandsspur fuer die sechs fachlich relevanten Faelle
zulaessig:

1. `UNIQUE_A`;
2. `UNIQUE_B`;
3. oeffentliche A/B-Mehrdeutigkeit;
4. A-Bankmehrdeutigkeit;
5. `NO_CONTEXT`;
6. `NO_APPLICABLE_CONTEXT`.

B4/Fast-Konflikt und Slow-Mehrdeutigkeit bleiben neutrale, bereits
qualifizierte Sicherheitsfaelle. Ein realer Memorylauf bleibt bis zur
statischen Sechs-Faelle-Zustandsspur gesperrt.
