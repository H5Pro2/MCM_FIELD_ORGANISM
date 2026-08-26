# S2-C9: R2/C2 erster Zeitstrukturkontrast

Stand: 2026-08-07

Status: `S2C9_R2_C2_FIRST_TIME_STRUCTURE_CONTRAST_BOUND`

Forschungsentscheidung: nein

Vollmatrix: gesperrt

Forschungslauf: nein

## Zweck

S2-C9 bindet erstmals ein R/C-Paar mit gleicher Gesamtkontaktzeit, aber
unterschiedlicher zeitlicher Gliederung:

```text
R2: A 0.4 s -> N 0.4 s -> A 0.4 s
C2: A zusammenhaengend 0.8 s
```

Beide Kontaktbloecke sind um 4.0 s zentriert. Die gesamte Welt dauert 8.0 s,
die aktive Kontaktzeit betraegt in beiden Armen 0.8 s.

## Gebundene Plaene

`S2PreparedR2C2Plan` akzeptiert ausschliesslich `r2.a` oder `c2.a`.
`prepare_s2c9_r2c2_receptor_plans` liefert beide Plaene in fester Reihenfolge
und bindet:

- getrennte kanonische Welt- und Sequenzdigests;
- denselben Organismustakt und dieselbe Rezeptoranatomie;
- R2 mit fuenf Phasen und C2 mit drei Phasen;
- je 871 vollstaendig zugeordnete Quellenstuetzpunkte;
- den gemeinsamen Horizont von 0.0 bis 8.0 s.

R2 und C2 werden nicht zu einer gemeinsamen Welt zusammengelegt.

## B0/B2-Bildung und Probe

`advance_s2c9_r2c2_world` fuehrt jeden Plan getrennt durch B0 oder B2. Der
technische B2-Nullarm `g=0` bleibt nur als Fastprojektionskontrolle
zulaessig. Aktives B2 verwendet unveraendert `rho=8` und `g=0.25/s`.

`observe_s2c9_r2c2_probe` wendet denselben externen S/H-Abgleich und dieselbe
Probe P an und beobachtet beide Arme an den 31 gebundenen Probe-Ticks.

## D_pair(2)

`measure_s2c9_r2c2_pair` berechnet direkt zwischen den synchronen R2- und
C2-Spuren:

```text
D_pair(2) = max(
    max_t ||S_R2(t) - S_C2(t)||_inf,
    max_t ||H_R2(t) - H_C2(t)||_inf
)
```

`S2R2C2PairResult` enthaelt nur Formation- und Probe-Digests, Modellkennung,
Supportzahl und eine skalare `d_pair`-Metrik.

Fuer B0 muss `D_pair(2)=0.0` exakt gelten. B0 besitzt nach dem externen
S/H-Abgleich keinen verbleibenden Geschichtstraeger. Eine Abweichung wird als
technischer Fehler verworfen.

Aktives B2 liefert in der kontrollierten Implementierungsabnahme einen
endlichen, reproduzierbaren Wert groesser null. Dieser Wert ist die erwartete
Wirkung der bereits bekannten linearen S1-B/B2-Referenzgleichung und keine
neue Mechanik.

## Technische Pruefung

`tests/test_s2c9_r2c2_time_contrast.py` bindet:

1. gleiche Budgets bei fuenf R2- und drei C2-Phasen;
2. exakte B0-Gleichheit zu den bestehenden kontrollierten Phasenpfaden;
3. B2-Nullarmgleichheit zur jeweiligen B0-Fastprojektion;
4. digestgenaue aktive B2-Reproduktion beider Welten;
5. `D_pair(2)=0` exakt fuer B0;
6. endlichen positiven und reproduzierbaren B2-Referenzwert;
7. Abweisung unterschiedlich modellierter Paare.

```text
neue S2-C9-Suite:                  7 passed
gesamter relevanter Testverbund:  124 passed, 13 subtests passed
Python-Kompilation:               bestanden
```

Die bekannte Pytest-Cachewarnung hat keinen Einfluss auf die Ergebnisse.

## Aussagegrenze

S2-C9 zeigt nur, dass die lineare B2-Referenzdynamik zwei kontrollierte
Zeitgliederungen nach dem S/H-Abgleich technisch unterscheiden kann. S1-B
ist definitionsgemaess dieselbe lineare Pflichtbaseline. Daher folgt kein
Nachweis fuer Praegung, organisches Memory, relative Feldzeit, innere
Organisation oder KI.

Ein einzelner n=2-Wert beschreibt auch keinen Trend ueber Kontaktdosis oder
Wiederholungszahl.

## Entscheidung

```text
r2.a/c2.a-Plaene:                 gebunden
gleiche Kontaktzeit:              0.8 s
unterschiedliche Gliederung:      gebunden
B0 D_pair(2):                     0.0 exakt
B2 D_pair(2):                     endlich, positiv, reproduzierbar
n=4/n=8:                          nein
Entscheidungslogik:               nein
Vollmatrix:                       gesperrt
Forschungslauf:                   nein
```

## Bester naechster Schritt

S2-C10 bis S2-C16 schliessen die A/B-Referenz bis zur kanonischen
End-to-End-Komposition. Der S2-Zwischenentscheid verweist als naechsten
Schritt auf den statischen S1-C-Kandidatenvertrag. Keine Schwelle,
Vollmatrix, Persistenz oder Laufnummer.
