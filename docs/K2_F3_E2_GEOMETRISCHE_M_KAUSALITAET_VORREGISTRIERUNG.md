# K2/F3 E2: Vorregistrierung geometrischer M-Kausalitaet

Stand: 2026-08-06

Status:

- feste 84-Orte-Geometrie aus Lauf 189 gebunden;
- wertunabhaengige Spiegelung und zwei lokale Masken gebunden;
- gemeinsame Probe und F3-Parameter unveraendert;
- kein Memory-, Organisations-, Topologie-, Semantik- oder KI-Claim.

## 1. Forschungsfrage

Haengt die in Lauf 189 isolierte spaetere M-Wirkung von der konkreten
Zuordnung der M-Werte zur festen Feldgeometrie ab, oder genuegen die
ungeordnete M-Werteverteilung beziehungsweise globale Summenwerte?

Der Versuch prueft nur Evidenzstufe E2: geometrisch verteilte Kausalitaet.
Er prueft noch keine Nichtseparierbarkeit gegen lokale Baselines und keinen
Memory-Lebenszyklus.

## 2. Unveraenderte Welt- und Parameterbindung

Verwendet werden dieselben zwei dreisekuendigen Geschichten und dieselbe
einmal frisch reduzierte gemeinsame Probe aus Lauf 189:

```text
same history digest:    997f318cf5f43f84a9747fcd5b95e3fe4cbfce68d3d5f851f22895d70504002d
changed history digest: a263b21d6fefa93389d494cb7d298910caa6f5cfea882aacc74cfb4da4cfba53
shared probe digest:     dba4ae9b51af783ec4abe195eacaac98be94380f1e7125d6cf56f154a15cc927
```

```text
response_time_seconds: 1.0
afterimage_time_constant_seconds: 0.5
lambda_sm_per_second: 1.0
kappa: 0.5
eta: 1.0
dissipation: keine
refinement: 4n
```

S und H werden nach jeder Geschichte und vor jeder Intervention exakt auf
Null angeglichen.

## 3. Gebundene Geometrie

```text
neuron_count: 84
auditory row: Zeile 0, Spalten 0..11
visual rows:  Zeilen 1..4, Spalten 0..17
```

### I3: zeilenweise horizontale Spiegelung

Jeder Ort `(row, column)` erhaelt den M-Wert des an der Mitte derselben Zeile
gespiegelten Ortes. Die Abbildung liest ausschliesslich Positionen.

```text
pair_count: 84
reflection_digest: 603db647df0717d7c94747e90f98dd907717e08f9830e23c5aa038e4d82d2ffb
```

Die Abbildung ist bijektiv und involutiv. Sie erhaelt jeden einzelnen M-Wert,
die gesamte Wertemultimenge, Gesamtmasse und alle globalen Momente. Nur die
Zuordnung der Werte zu Orten wird geaendert.

### I4: massenbilanzierte lokale Neutralisierung

```text
left mask:  visuelle Zeilen 1..4, Spalten 0..8, 36 Orte
right mask: visuelle Zeilen 1..4, Spalten 9..17, 36 Orte
left mask digest:  c6221c5edee311f8795bdda1de10a30828e5a712e0355d29c1f4faf614217a24
right mask digest: 77485ba0a8cd50f54bc83b6e0d00459c5935fb0e346ed95e27a799af5ca9d8d5
```

Die Zielmaske wird auf den gleichfoermigen M-Referenzwert gesetzt. Ihre
vollstaendige Massedifferenz wird gleichmaessig in der jeweils anderen
visuellen Halbmaske verbucht. Auditive Orte bleiben unveraendert. Negative M-
Werte oder eine Bilanzabweichung brechen vor der Probe ab.

## 4. Vorregistrierte Probe-Arme

Fuer beide Geschichten `same` und `changed`:

```text
natural
reflected
neutral-left
neutral-right
eta-null-natural
eta-null-reflected
```

Alle zwoelf Arme erhalten dasselbe unveraenderliche Probeobjekt.

## 5. Entscheidungskontrollen

Ein enger Befund `GEOMETRIC_M_CAUSALITY` erfordert gleichzeitig:

1. Spiegelung erhaelt die M-Wertemultimenge und Gesamtmasse exakt.
2. Zweimalige Spiegelung stellt den urspruenglichen M-Vektor exakt wieder her.
3. S und H sind vor der Probe in allen Armen exakt Null.
4. Natural und reflected erzeugen fuer beide Geschichten unterschiedliche
   spaetere S- oder H-Vektoren.
5. Bei eta-null fallen natural und reflected in S und H fuer jede Geschichte
   exakt zusammen.
6. Beide lokalen Neutralisierungen erhalten Gesamtmasse und Nichtnegativitaet.
7. Neutral-left und neutral-right veraendern jeweils die spaetere S/H-Wirkung
   gegen natural.
8. Neutral-left und neutral-right erzeugen voneinander verschiedene spaetere
   S/H-Vektoren.
9. Alle S/H/M-Invarianten bleiben eingehalten.

Scheitert eine Kontrolle, lautet die Entscheidung `NO_GEOMETRIC_M_EFFECT`
oder `TECHNICALLY_UNDECIDABLE`. Geometrie, Masken, Probe und Parameter werden
nicht nach dem Ergebnis geaendert.

## 6. Messungen

- M-Linf zwischen natural und reflected vor der Probe;
- S/H-Linf natural gegen reflected;
- S/H-Linf natural gegen beide lokalen Neutralisierungen;
- S/H-Linf neutral-left gegen neutral-right;
- eta-null-Gleichheit;
- Multimengen-, Involutions-, Gesamtmassen- und Nichtnegativitaetskontrollen;
- Snapshot- und Komponentendigests.

## 7. Evidenzgrenze

Ein positiver Befund belegt nur, dass die spaetere Wirkung von der raeumlichen
Zuordnung der konservierten M-Werte im festen Feld abhaengt. Er belegt weder,
dass diese Kausalitaet nicht durch unabhaengige lokale Zustandsvariablen plus
S-Fluss reproduzierbar ist, noch Praegung, Feldzeitverdichtung, Loesung,
Wiederpraegung, Memory, Organisation, Topologie, Semantik oder KI.

## 8. Laufnummer

Der letzte nachweislich ausgefuehrte Forschungsdurchlauf ist Lauf 189. Nur
bei tatsaechlicher Ausfuehrung dieses unveraenderten Vertrags entsteht Lauf
190.
