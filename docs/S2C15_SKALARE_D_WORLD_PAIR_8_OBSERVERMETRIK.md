# S2-C15: Skalare D_world_pair(8)-Observermetrik

Stand: 2026-08-07

Status: `S2C15_D_WORLD_PAIR_8_OBSERVER_METRIC_BOUND`

Schwelle: nein

Forschungsentscheidung: nein

Forschungslauf: nein

## Zweck

S2-C15 bindet genau eine aus dem C14-Container abgeleitete Observermetrik:

```text
D_world_pair(8) = abs(D_pair_A(8) - D_pair_B(8))
```

Die Metrik wird nicht in Welt, Rezeptoren oder S/H/L zurueckgegeben.

## Getrennter Metrikvertrag

`S2WorldPairMetric` akzeptiert nur `d_world_pair` und einen endlichen,
nichtnegativen Wert im Felddomainbereich. Sie wird bewusst nicht in die
globale `S2_METRIC_IDS`-Liste aufgenommen, weil diese zum bereits gebundenen
vollstaendigen S2-Paketschema gehoert.

`S2N8WorldPairDistance` bindet:

- Modellarm und Kopplungswert;
- C14-Container-Digest;
- Probe-Provenienz und Support;
- beide Quellskalare;
- exakt die daraus berechnete absolute Differenz.

B0 muss `D_world_pair(8)=0` exakt liefern.

## Bewusst fehlende Funktionen

Das Ergebnis besitzt keine:

- Schwelle;
- Entscheidung;
- Weltspezifitaetsbewertung;
- Semantik- oder Bedeutungszuordnung;
- Rueckwirkung auf die Runtime.

## Technische Pruefung

`tests/test_s2c15_n8_world_pair_distance.py` prueft sechs Invarianten:

1. exakte B0-Nullmetrik und fehlende Auswertungsfelder;
2. absolute, deterministische B2-Berechnung;
3. Symmetrie gegen Vertauschung der beiden Skalarwerte;
4. Abweisung eines nicht typisierten Containers;
5. Abweisung einer zur Quelle inkonsistenten Metrik;
6. Abweisung falscher Kennung und nichtendlicher Werte.

```text
neue S2-C15-Suite:                 6 passed
C14/C15 gemeinsam:               12 passed
direkter S1-B/S2-Testverbund:    110 passed
Python-Kompilation:               bestanden
```

Die Tests verwenden typisierte technische Container. Die vollstaendige
Komposition von den kanonischen A/B-Welten bis zu dieser Metrik ist inzwischen
in S2-C16 als eigener technischer End-to-End-Test gebunden. Es wurde keine
Ergebnisdatei erzeugt.

## Aussagegrenze

Ein von null verschiedener B2-Wert waere zunaechst nur der Abstand zweier
linearer Referenzwirkungen bei verschiedenen kontrollierten Weltkontakten.
Er waere kein Nachweis fuer Weltspezifitaet, Praegung, Memory, relative
Feldzeit, Organisation, Bedeutung, Semantik oder KI.

## Anschluss

S2-C16 schliesst die hier vorbereitete technische Komposition. Der naechste
Schritt ist ein begrenzter S2-Zwischenentscheid, keine weitere Metrik- oder
Containerstufe.
