# K2/F3 E3: Baseline-Audit und Vorregistrierung

Stand: 2026-08-06

Status:

- statischer Audit abgeschlossen;
- drei enge Vergleichsklassen und ihre Parameter fest gebunden;
- keine Anpassung an Ergebnisse von Lauf 188 bis 191;
- noch kein E3-Befund und kein Memory-Claim.

## 1. Forschungsfrage

Wird die in Lauf 189 und 191 beobachtete spaetere geometrische M-Wirkung
durch gleich budgetierte lineare Standardzustaende reproduziert, oder bleibt
in den vollstaendigen S/H-Trajektorien ein belastbarer Rest?

Der Vergleich prueft nur die Reduzierbarkeit der bestehenden F3-Form. Er
prueft weder Feldzeitverdichtung noch einen Memory-Lebenszyklus.

## 2. Feste gemeinsame Budgets

Kandidat und Baselines erhalten unveraendert:

```text
ein skalarer Zusatzstate pro Feldort
84 Feldorte und dieselben lokalen Kanten
float64
SSPRK(3,3), refinement 4n
response time 1.0 s, H time constant 0.5 s
lambda 1.0, kappa 0.5, eta 1.0
dieselben zwei Geschichten und dieselbe gemeinsame Probe
dieselbe exakte S/H-Nullangleichung vor der Probe
dieselben natural-, reflected-, neutral-left- und neutral-right-Arme
keine Parameteranpassung je Geschichte, Phase oder Arm
```

Die Digests bleiben:

```text
same history:    997f318cf5f43f84a9747fcd5b95e3fe4cbfce68d3d5f851f22895d70504002d
changed history: a263b21d6fefa93389d494cb7d298910caa6f5cfea882aacc74cfb4da4cfba53
shared probe:    dba4ae9b51af783ec4abe195eacaac98be94380f1e7125d6cf56f154a15cc927
```

## 3. Vorregistrierte Baselines

Es sei `m0 = 1/N`, `x = M - m0` und `L_G` der feste symmetrische
Graph-Laplace-Operator mit `(L_G z)_i = sum_j(z_j-z_i)`.

### B1: lokale Leaky-Spur

```text
dx/dt = -lambda*x - 2*lambda*kappa*m0*L_G*S
R      = eta*lambda*x
```

Der Zusatzstate besitzt keinen eigenen raeumlichen Fluss. Er liest nur den
lokalen Nettoanteil des bereits bestehenden schnellen S-Flusses und wirkt
ueber einen festen linearen Leser zurueck.

### B2: lineare lokale Gegenvariable

```text
dx/dt = -lambda*x - 2*lambda*kappa*m0*L_G*S
R      = -eta*dx/dt
```

Der State ist identisch budgetiert zu B1; nur die feste Gegenwirkung ist an
seine aktuelle Aenderung gebunden.

### B3: lineare gekoppelte Feldform

```text
dx/dt = lambda*L_G*x - 2*lambda*kappa*m0*L_G*S
R      = -eta*dx/dt
```

B3 ist keine gefittete Naeherung. Sie ist die analytische Linearisierung der
implementierten F3-Gleichung um gleichfoermiges M und neutrales S. Sie ist
damit die staerkste enge Gegenbaseline dieses Laufs.

Alle drei Raten summieren exakt zu null. Gesamtbudget und geometrische
Interventionen bleiben dadurch mit dem Kandidaten vergleichbar.

## 4. Vollstaendige Beobachtung

Ein passiver Observer erfasst nach jedem Rezeptor-Abschlusszeitpunkt sowie am
Phasenende die vollstaendigen S-, H- und Zusatzstate-Vektoren. Der Observer
schreibt nicht in die Runtime zurueck. Verglichen werden:

- komplette Geschichte je Welt;
- komplette Probe je Geschichte und Geometriearm;
- natural-reflected-, natural-left- und natural-right-Effekttrajektorien;
- same-changed-Kontrast unter der gemeinsamen natural-Probe;
- Massenbilanz, Nichtnegativitaet und identische Beobachtungstakte.

## 5. Feste Entscheidung

Fuer jede Baseline werden die maximalen L-inf-Residuen ueber alle Orte und
alle erfassten Zeitpunkte relativ zum jeweiligen Kandidateneffekt berichtet.
Es wird nichts anhand des Resultats nachparametriert.

Eine Baseline gilt in diesem engen Lauf als `BASELINE_EXPLAINS_EFFECT`, wenn:

1. alle Beobachtungstakte exakt uebereinstimmen;
2. Gesamtbudget und Nichtnegativitaet erhalten bleiben;
3. alle sechs E2-Interventionseffekte und der same-changed-Kontrast vorhanden
   bleiben;
4. das maximale Residuum jeder Effekttrajektorie hoechstens `5 %` des
   zugehoerigen F3-Effekts betraegt.

Erfuellt mindestens eine Baseline diese Bedingungen, lautet die
Gesamtentscheidung `E3_EXPLAINED_BY_NARROW_BASELINE`; der Weg zu verteilter
kausaler Nichtseparierbarkeit wird geschlossen.

Scheitern alle drei Formen, lautet die Entscheidung nur
`E3_RESIDUAL_REQUIRES_MORE_BASELINES`. Das ist kein positiver E3-Nachweis,
weil Hysterese, Oszillator und konkrete nichtlineare Feldbaselines dann noch
ausstehen. Technische Kontrollverletzungen ergeben `TECHNICALLY_UNDECIDABLE`.

## 6. Grenzen

Ein kleiner nichtlinearer Rest gegen B3 beweist keine neue Funktionsklasse.
Die implementierte F3-Form ist bereits transparent als lokale bilineare
konservative Drift-/Cross-Diffusionsphysik bekannt. Ebenso belegt eine gute
lineare Reproduktion nur Reduzierbarkeit im untersuchten Korridor.

Nicht freigegeben sind Memory, Organisation, Topologie, Feldzeitverdichtung,
innerer Kontext, Semantik oder KI.

## 7. Laufnummer

Der letzte ausgefuehrte Forschungsdurchlauf ist Lauf 191. Erst die einmalige
Ausfuehrung dieses unveraenderten Vertrags erzeugt Lauf 192.
