# S2-C10: R4/C4 zweiter Zeitstrukturkontrast

Stand: 2026-08-07

Status: `S2C10_R4_C4_SECOND_TIME_STRUCTURE_CONTRAST_BOUND`

Forschungsentscheidung: nein

Vollmatrix: gesperrt

Forschungslauf: nein

## Zweck

S2-C10 bindet das zweite R/C-Paar mit gleicher Gesamtkontaktzeit, aber
unterschiedlicher zeitlicher Gliederung:

```text
R4: A 0.4 s -> N 0.4 s -> A 0.4 s -> N 0.4 s
    -> A 0.4 s -> N 0.4 s -> A 0.4 s
C4: A zusammenhaengend 1.6 s
```

Beide Kontaktbloecke sind um 4.0 s zentriert. Die gesamte Welt dauert 8.0 s,
die aktive Kontaktzeit betraegt in beiden Armen 1.6 s.

## Gebundene Plaene

`S2PreparedR4C4Plan` akzeptiert ausschliesslich `r4.a` oder `c4.a`.
`prepare_s2c10_r4c4_receptor_plans` liefert beide Plaene in fester Reihenfolge
und bindet:

- getrennte kanonische Welt- und Sequenzdigests;
- denselben Organismustakt und dieselbe Rezeptoranatomie;
- R4 mit neun Phasen und C4 mit drei Phasen;
- je 871 vollstaendig zugeordnete Quellenstuetzpunkte;
- den gemeinsamen Horizont von 0.0 bis 8.0 s.

R4 und C4 bleiben getrennte kontrollierte Welten.

## B0/B2-Bildung und Probe

`advance_s2c10_r4c4_world` fuehrt jeden Plan getrennt durch B0 oder B2. Der
technische B2-Nullarm `g=0` dient nur als Fastprojektionskontrolle. Aktives
B2 verwendet unveraendert `rho=8` und `g=0.25/s`.

`observe_s2c10_r4c4_probe` verwendet denselben externen S/H-Abgleich und
dieselbe Probe P. Beobachtet werden die 31 bereits gebundenen Probe-Ticks.

## D_pair(4)

`measure_s2c10_r4c4_pair` berechnet zwischen den synchronen R4- und C4-Spuren:

```text
D_pair(4) = max(
    max_t ||S_R4(t) - S_C4(t)||_inf,
    max_t ||H_R4(t) - H_C4(t)||_inf
)
```

Fuer B0 gilt `D_pair(4)=0.0` exakt. Aktives B2 liefert in der technischen
Abnahme einen endlichen, positiven und reproduzierbaren Wert. Das ist nur die
erwartete Wirkung der bekannten linearen S1-B/B2-Referenzgleichung.

## Technische Pruefung

`tests/test_s2c10_r4c4_time_contrast.py` bindet:

1. gleiche Budgets bei neun R4- und drei C4-Phasen;
2. exakte B0-Gleichheit zu den bestehenden kontrollierten Phasenpfaden;
3. B2-Nullarmgleichheit zur jeweiligen B0-Fastprojektion;
4. digestgenaue aktive B2-Reproduktion beider Welten;
5. `D_pair(4)=0` exakt fuer B0;
6. endlichen positiven und reproduzierbaren B2-Referenzwert;
7. Abweisung unterschiedlich modellierter Paare.

```text
neue S2-C10-Suite:                 7 passed
direkter S1-B/S2-Testverbund:     78 passed
Python-Kompilation:               bestanden
```

Die bekannte Pytest-Cachewarnung hat keinen Einfluss auf die Ergebnisse.

## Aussagegrenze

S2-C10 zeigt nur, dass die lineare B2-Referenzdynamik auch die kontrollierten
n=4-Zeitgliederungen nach dem S/H-Abgleich technisch unterscheiden kann. Der
Befund ist weder eine neue Mechanik noch ein Nachweis fuer Praegung,
organisches Memory, relative Feldzeit, innere Organisation oder KI.

Die Werte fuer n=2 und n=4 duerfen noch nicht als Trend interpretiert werden.
Die Kontaktbudgets unterscheiden sich und es fehlt weiterhin n=8.

## Entscheidung

```text
r4.a/c4.a-Plaene:                 gebunden
gleiche Kontaktzeit:              1.6 s
unterschiedliche Gliederung:      gebunden
B0 D_pair(4):                     0.0 exakt
B2 D_pair(4):                     endlich, positiv, reproduzierbar
n=8:                              nein
Entscheidungslogik:               nein
Vollmatrix:                       gesperrt
Forschungslauf:                   nein
```

## Bester naechster Schritt

S2-C16 bindet ausschliesslich die kanonische A8/B8-End-to-End-Komposition.
Keine Schwelle, Weltspezifitaetsentscheidung, Intervention, Vollmatrix,
Persistenz oder Laufnummer.
