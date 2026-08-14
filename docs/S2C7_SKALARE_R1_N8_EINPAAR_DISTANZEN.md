# S2-C7: Skalare r1.a-/N8-Einpaardistanzen

Stand: 2026-08-07

Status: `S2C7_SCALAR_R1_N8_SINGLE_PAIR_DISTANCES_BOUND`

Forschungsentscheidung: nein

Vollmatrix: gesperrt

Forschungslauf: nein

## Zweck

S2-C7 reduziert genau ein in S2-C6 gebundenes r1.a-/N8-Probespurenpaar auf
die bereits in S2-A vorregistrierten skalaren Distanzen:

```text
D_L(history, neutral) = ||L_r1 - L_N8||_inf vor S/H-Angleichung
D_S(P)                = max_t ||S_r1(t) - S_N8(t)||_inf waehrend P
D_H(P)                = max_t ||H_r1(t) - H_N8(t)||_inf waehrend P
```

Es wird weder `D_pair` berechnet noch eine technische oder fachliche
Entscheidung getroffen.

## Einpaarvertrag

`measure_s2c7_single_pair_distances` akzeptiert ausschliesslich:

- eine abgeschlossene r1.a-Bildung;
- die zugehoerige abgeschlossene N8-Bildung;
- das exakt zu diesen Formationdigests gehoerende S2-C6-Spurenpaar;
- denselben B0- oder B2-Modellarm und dieselbe Kopplung in allen Eingaben.

Fremde, vertauschte oder anders modellierte Spuren werden vor der Reduktion
abgewiesen.

## Skalare Reduktion

Fuer `D_S` und `D_H` wird das Maximum ueber alle 31 gemeinsamen Probe-Ticks
und alle 84 Feldorte gebildet. Es wird kein Endzustand stellvertretend fuer
den Probeverlauf verwendet.

Fuer B2 wird `D_L` unmittelbar aus den beiden abgeschlossenen
Formation-L-Zustaenden vor dem externen S/H-Abgleich berechnet. Beide
L-Zustaende muessen denselben Naturvertrag besitzen.

Das Ergebnis `S2SinglePairDistances` enthaelt nur Digests, Modellkennung,
Supportzahl und geordnete `S2ScalarMetric`-Werte.

## B0-Nullkontrolle

B0 besitzt keinen L-Zustand und darf deshalb keine `D_L`-Metrik ausgeben. Da
S und H vor derselben Probe exakt angeglichen werden und B0 keine
Geschichtstraegerrolle besitzt, muessen fuer B0 gelten:

```text
D_S(P) = 0.0 exakt
D_H(P) = 0.0 exakt
D_L    = nicht vorhanden
```

Der C7-Vertrag verwirft ein B0-Ergebnis, sobald eine der beiden S/H-Distanzen
von exakt null abweicht.

## Technische Pruefung

`tests/test_s2c7_single_pair_distances.py` bindet:

1. exakte B0-S/H-Nullkontrolle ohne vorgetaeuschte L-Metrik;
2. fuer B2 ausschliesslich `D_L`, `D_S` und `D_H`;
3. exakte Maximalreduktion ueber alle C6-S/H-Samples;
4. exakte L-Distanz aus den Formationzustaenden;
5. reproduzierbare skalare Ausgabe ohne Entscheidung;
6. Abweisung nicht zusammengehoeriger Formation- und Spurenarme.

```text
neue S2-C7-Suite:                  6 passed
gesamter relevanter Testverbund:  111 passed, 13 subtests passed
Python-Kompilation:               bestanden
```

Die bekannte Pytest-Cachewarnung hat keinen Einfluss auf die Ergebnisse.

## Aussagegrenze

S2-C7 implementiert nur die vorregistrierte technische Messung eines
synthetischen Einpaars. Ein von null verschiedener B2-Wert waere innerhalb
dieses Schritts lediglich die Wirkung der bereits bekannten linearen
S1-B/B2-Referenzgleichung. Er ist kein Nachweis fuer Praegung, Memory,
relative Feldzeit oder Organisation.

Noch fehlen mindestens der R/C-Paarvergleich, unabhaengige Pflichtbaselines,
Interventionen, Reproduktionstoleranzen und die vorregistrierte
Entscheidungslogik.

## Entscheidung

```text
D_S(P):                           gebunden
D_H(P):                           gebunden
D_L fuer B2:                      gebunden
B0-S/H-Nullkontrolle:             exakt bestanden
D_pair:                           nein
Entscheidungslogik:               nein
Vollmatrix:                       gesperrt
Forschungslauf:                   nein
```

## Bester naechster Schritt

S2-C8 bis S2-C16 binden Identitaetskontrolle, A/B-Pfade, Container,
Observermetrik und kanonische End-to-End-Komposition. Der
S2-Zwischenentscheid verweist als naechsten Schritt auf den statischen
S1-C-Kandidatenvertrag. Noch keine Entscheidung, Vollmatrix, Persistenz oder
Laufnummer.
