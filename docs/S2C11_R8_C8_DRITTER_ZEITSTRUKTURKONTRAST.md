# S2-C11: R8/C8 dritter Zeitstrukturkontrast

Stand: 2026-08-07

Status: `S2C11_R8_C8_THIRD_TIME_STRUCTURE_CONTRAST_BOUND`

Forschungsentscheidung: nein

Vollmatrix: gesperrt

Forschungslauf: nein

## Zweck

S2-C11 bindet das dritte unterschiedliche R/C-Paar:

```text
R8: acht A-Kontakte zu je 0.4 s, getrennt durch sieben N-Luecken zu 0.4 s
C8: ein zusammenhaengender A-Kontakt von 3.2 s
```

Beide Kontaktbloecke sind um 4.0 s zentriert. Die gesamte Welt dauert 8.0 s,
die aktive Kontaktzeit betraegt in beiden Armen 3.2 s.

## Gebundene Plaene

`S2PreparedR8C8Plan` akzeptiert ausschliesslich `r8.a` oder `c8.a`.
`prepare_s2c11_r8c8_receptor_plans` bindet:

- getrennte kanonische Welt- und Sequenzdigests;
- denselben Organismustakt und dieselbe Rezeptoranatomie;
- R8 mit 17 Phasen und C8 mit drei Phasen;
- je 871 vollstaendig zugeordnete Quellenstuetzpunkte;
- den gemeinsamen Horizont von 0.0 bis 8.0 s.

## B0/B2-Bildung, Probe und D_pair(8)

`advance_s2c11_r8c8_world` fuehrt beide Plaene getrennt durch B0 oder B2.
Der technische B2-Nullarm `g=0` dient nur als Fastprojektionskontrolle.
Aktives B2 bleibt bei `rho=8` und `g=0.25/s`.

`observe_s2c11_r8c8_probe` nutzt denselben externen S/H-Abgleich, dieselbe
Probe P und dieselben 31 Probe-Ticks wie die vorherigen Paare.

`measure_s2c11_r8c8_pair` berechnet ausschliesslich:

```text
D_pair(8) = max(
    max_t ||S_R8(t) - S_C8(t)||_inf,
    max_t ||H_R8(t) - H_C8(t)||_inf
)
```

Fuer B0 gilt `D_pair(8)=0.0` exakt. Aktives B2 liefert in der technischen
Abnahme einen endlichen, positiven und reproduzierbaren Wert. Das ist nur die
erwartete Wirkung der linearen S1-B/B2-Referenzgleichung.

## Technische Pruefung

`tests/test_s2c11_r8c8_time_contrast.py` bindet sieben Invarianten:

1. gleiche Budgets bei 17 R8- und drei C8-Phasen;
2. exakte B0-Gleichheit zu den bestehenden kontrollierten Phasenpfaden;
3. B2-Nullarmgleichheit zur jeweiligen B0-Fastprojektion;
4. digestgenaue aktive B2-Reproduktion beider Welten;
5. `D_pair(8)=0` exakt fuer B0;
6. endlichen positiven und reproduzierbaren B2-Referenzwert;
7. Abweisung unterschiedlich modellierter Paare.

```text
neue S2-C11-Suite:                 7 passed
direkter S1-B/S2-Testverbund:     85 passed
Python-Kompilation:               bestanden
```

Die bekannte Pytest-Cachewarnung hat keinen Einfluss auf die Ergebnisse.

## Aussagegrenze

Mit C8 existieren nun die einzelnen A-Paarpfade fuer n=1, 2, 4 und 8. Daraus
folgt noch kein Trend, Wiederholungsnachweis oder Memorybefund. Die n-Stufen
haben unterschiedliche Kontaktbudgets; ein Verlauf ueber n waere nur eine
Dosischarakterisierung. Die lineare B2-Wirkung bleibt Pflichtbaseline.

B-Kontakte, Interventionen, B1/B3/B4/B5, Vollmatrix und
Forschungsentscheidung sind weiterhin nicht freigegeben.

## Entscheidung

```text
r8.a/c8.a-Plaene:                 gebunden
gleiche Kontaktzeit:              3.2 s
unterschiedliche Gliederung:      gebunden
B0 D_pair(8):                     0.0 exakt
B2 D_pair(8):                     endlich, positiv, reproduzierbar
A-Paare n=1/2/4/8 einzeln:        technisch vorhanden
Trendentscheidung:               nein
Vollmatrix:                       gesperrt
Forschungslauf:                   nein
```

## Bester naechster Schritt

S2-C16 bindet ausschliesslich die kanonische A8/B8-End-to-End-Komposition.
Keine Schwelle, Weltspezifitaetsentscheidung, Intervention, Vollmatrix,
Persistenz oder Laufnummer.
