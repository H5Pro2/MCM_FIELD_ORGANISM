# S2-C13: R8-B/C8-B kontrolliertes zweites Weltpaar

Stand: 2026-08-07

Status: `S2C13_R8B_C8B_SECOND_WORLD_PAIR_BOUND`

Forschungsentscheidung: nein

A/B-Vergleich: nein

Forschungslauf: nein

## Zweck

S2-C13 bindet Kontakt B als getrenntes n=8-R/C-Weltpaar:

```text
R8-B: acht B-Kontakte zu je 0.4 s, getrennt durch sieben N-Luecken
C8-B: ein zusammenhaengender B-Kontakt von 3.2 s
```

Kontakt B verwendet die vorregistrierten 760 Hz und eine von A getrennte
visuelle Lage. Beide B-Arme besitzen denselben Zeitplan und dasselbe
Kontaktbudget wie ihre A-Gegenstuecke. A und B werden in C13 nicht verglichen.

## Technischer Pfad

`S2PreparedR8BC8BPlan` und `prepare_s2c13_r8bc8b_receptor_plans` binden:

- nur `r8.b/c8.b`;
- R8-B mit 17 und C8-B mit drei Phasen;
- je 871 Quellenstuetzpunkte;
- 8.0 s Horizont und 3.2 s Kontaktzeit;
- getrennte kanonische Welt-, Sequenz- und Plandigests.

`advance_s2c13_r8bc8b_world` fuehrt nur B0 oder B2. Der B2-Nullarm `g=0`
bleibt Fastprojektionskontrolle; aktives B2 verwendet `rho=8`, `g=0.25/s`.

`observe_s2c13_r8bc8b_probe` nutzt denselben S/H-Abgleich, dieselbe Probe P
und dieselben 31 Probe-Ticks. `measure_s2c13_r8bc8b_pair` berechnet nur
`D_pair_B(8)` zwischen R8-B und C8-B.

## Technische Pruefung

`tests/test_s2c13_r8bc8b_world_control.py` bindet sieben Invarianten:

1. gleiche Budgets bei 17/3 Phasen;
2. exakte B0-Gleichheit zu den kanonischen B-Weltpfaden;
3. B2-Nullarmgleichheit zur B0-Fastprojektion;
4. digestgenaue aktive B2-Reproduktion;
5. `D_pair_B(8)=0` exakt fuer B0;
6. endlichen positiven reproduzierbaren B2-Referenzwert ohne
   Weltspezifitaetsfeld;
7. Abweisung gemischter Modellarme.

```text
neue S2-C13-Suite:                 7 passed
direkter S1-B/S2-Testverbund:     98 passed
Python-Kompilation:               bestanden
```

## Aussagegrenze

Der positive B2-Wert ist ausschliesslich eine lineare Referenzwirkung innerhalb
der B-Welt. Ohne A/B-Kontrast folgt daraus keine Geschichts- oder
Weltspezifitaet. Auch ein spaeterer Unterschied zwischen A und B waere noch
keine Bedeutung oder Semantik.

Es wurde keine Ergebnisdatei geschrieben und kein Forschungslauf gestartet.

## Bester naechster Schritt

S2-C16 bindet ausschliesslich die kanonische A8/B8-End-to-End-Komposition.
Keine Schwelle, Weltspezifitaetsentscheidung, Semantikbehauptung,
Intervention, Vollmatrix, Persistenz oder Laufnummer.
