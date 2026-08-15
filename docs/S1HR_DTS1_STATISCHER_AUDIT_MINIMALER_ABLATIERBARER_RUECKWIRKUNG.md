# S1-HR: DTS-1 statischer Rueckwirkungsaudit

## Status

Genau eine minimale ablatierbare Rueckwirkungsfamilie von leitend gebundener
DTS-1-Ressource auf vorhandene interne MCM-Kanten wurde statisch auditiert.
Keine Implementierung, keine Materialratenwerte, kein gekoppelter Integrator,
keine Runtime und kein Feldlauf.

Entscheidung:

```text
ZULASSEN_DTS1_SYMMETRIC_BOUNDED_CONDUCTANCE_BACKREACTION
```

`ZULASSEN` bedeutet nur, dass diese bekannte technische Adapterfamilie als
kleinster Leser der DTS-1-Dynamik weiter spezifiziert werden darf. Sie ist
kein Funktionsbefund und keine neue MCM-Natur.

## Genau eine Rueckwirkungsfamilie

```text
SYMMETRIC_BOUNDED_CONDUCTANCE_AUGMENTATION
```

Fuer eine vorhandene ungerichtete Kante `e={i,j}` wird die leitend gebundene
Belegung dimensionslos normiert:

```text
c_e = b_e / (2 * min(q_i, q_j))
```

Aus der S1-HI-Knotenbilanz folgt an jedem Endpunkt
`0.5*b_e <= q_i`. Daher gilt konstruktiv:

```text
0 <= c_e <= 1
```

Die Familie verwendet die bereits vorhandene neutrale interne Basisrate:

```text
r_0 = 1 / response_time

Rueckwirkung an:   r_e = r_0 * (1 + c_e)
Rueckwirkung aus:  r_e = r_0
```

Damit gilt im aktiven Arm `r_0 <= r_e <= 2*r_0`. Es wird kein zusaetzlicher
Rueckwirkungsstaerkeparameter eingefuehrt oder angepasst. Die Wahl der
positiven Leitungsrichtung folgt ausschliesslich der Rolle `leitend gebunden`;
negative, schwellende, signierte oder nichtlineare Leser werden nicht
parallel offengehalten.

## Generatorvertrag

Auf beiden Richtungen derselben ungerichteten Kante gilt dieselbe Rate:

```text
J_i<-j = r_e * (S_j - S_i)
J_j<-i = -J_i<-j
```

Der resultierende interne Graphgenerator bleibt:

- symmetrisch;
- mit Nullzeilensumme und ohne additive Feldquelle;
- negativ semidefinit;
- neutral auf einem konstanten Feld;
- getrennt von Rezeptorrand und schnellem Nachhall H.

DTS-1 darf weder Weltkontakt noch Rezeptoramplitude oder H direkt gewichten.

## Ablation und Pflichtbaselines

Verbindlich bleiben sechs Rollen:

| Arm | Rolle |
|---|---|
| P0 | bestehendes neutrales Feld ohne DTS-1-Zustand |
| A0 | derselbe entwickelte DTS-1-Zustand, Rueckwirkung aus |
| A1 | derselbe entwickelte DTS-1-Zustand, Rueckwirkung an |
| F0 | vor der Probe eingefrorenes A1-Kantenratenledger |
| U0 | uniformes festes Ledger im gleichen Ratenbereich |
| E1 | dynamische Zweizustandsressource mit derselben Leserfamilie |

A0 und A1 duerfen sich nur durch den technischen Ablationsschalter
unterscheiden. Der DTS-1-Zustand entwickelt sich in beiden Armen identisch,
solange keine gekoppelte Feldrueckwirkung implementiert ist.

Leaky/Integrator, F3/CONST-V und schneller Nachhall bleiben zusaetzlich die
S1-HH-Pflichtbaselines fuer den spaeteren Gesamtverlauf.

## Ehrliche Fixed-Adapter-Grenze

Fuer einen einzelnen abgeschlossenen Zustand ist `b_e -> r_e` exakt ein
Fixed Adapter. S1-HR behauptet hier keine strukturelle Ueberlegenheit. Die
einzige spaetere Gegenprognose entsteht aus der gekoppelten DTS-1-Dynamik:

```text
gleiche S, H, b_e und gleiche momentane Kantenrate
+ unterschiedliche Aufteilung frei / refraktaer
-> gleiche momentane Antwort
-> nach derselben naechsten Teilnahme unterschiedliche Bindung
-> erst danach unterschiedliche Kantenrate
```

Ein vor der Probe eingefrorenes Ledger sagt dagegen unveraenderte Raten
voraus. Reproduziert es den vollstaendigen Kandidatenverlauf, wird die
Rueckwirkungsrichtung gestoppt. Frozen-E1 wird dadurch nicht wiedereroeffnet;
es bleibt nur Gegenbaseline.

## STOPP-Bedingungen

Die Familie wird verworfen, wenn unter anderem:

- F0 den vollstaendigen Kandidatenverlauf reproduziert;
- die frei/refraktaer-Intervention spaetere Raten nicht trennt;
- dynamisches Zweizustands-E1 mit demselben Leser alle Profile erklaert;
- eine registrierte S1-HH-Baseline ausreicht;
- ein nichtlinearer, schwellender oder inhaltsspezifischer Leser benoetigt
  wird;
- ein zusaetzlicher Gain auf das gewuenschte Ergebnis angepasst werden muss;
- Rezeptor- oder H-Grenzen veraendert werden muessen;
- Symmetrie, Erhaltung oder Nichtpositivitaet des Generators verloren gehen.

## Aussagegrenze

S1-HR waehlt nur eine parameterlose bekannte Leserfamilie. Nicht gezeigt
sind korrekte Implementierung, gekoppelte numerische Stabilitaet,
Abschwaechung, Interferenz, Freigabe, Wiederbeanspruchung oder Trennung von
einer Baseline.

## Bester naechster Schritt

S1-HS darf nach dem naechsten `ok weiter` ausschliesslich den privaten reinen
Kantenratenadapter und einen reinen symmetrischen Generatorvertrag mit
fokussierten technischen Tests spezifizieren. Noch keine Implementierung,
keine Materialratenwerte, keine gekoppelte Runtime und kein Feldlauf.
