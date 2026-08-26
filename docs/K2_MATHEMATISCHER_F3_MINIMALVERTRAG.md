# K2: mathematischer F3-Minimalvertrag

## Status

```text
Vertragstyp:                       statischer mathematischer Kandidatenvertrag
Kantenform:                         genau eine kontinuierliche Minimalform
M-Erhaltung:                        nachgewiesen
M-Nichtnegativitaet und Begrenzung: nachgewiesen
S-Bereichsinvarianz:                bedingt nachgewiesen
aktiver frischer Referenzarm:        definiert
exakter Nullparameterarm:            definiert
Memory- oder Organisationsclaim:     nein
Implementierung oder Versuch:        noch nicht zugelassen
```

## Zweck

Dieser Vertrag formuliert unter dem verbindlichen
[K2-Nullpfad](NULLPFAD_KORREKTURVERTRAG_GEKOPPELTE_SUBSTRATPHYSIK.md)
genau eine kleinste kontinuierliche Kantenform fuer den konservativen
S-M-Austausch.

Die Form ist eine deklarierte digitale Materialhypothese. Sie wird nicht aus
der heutigen MCM-Gleichung hergeleitet und nicht als neue Naturwissenschaft
behauptet.

## 1. Zustands- und Geometriegrenze

Auf jedem bestehenden Feldort i liegt:

```text
S_i in [-1, 1]
H_i in [-1, 1]
M_i >= 0
```

Fuer jede verbundene Komponente C der festen MCM-Geometrie gilt:

```text
M_total(C) = Summe der M_i in C
M_total(C) > 0
```

Die vorhandene ungerichtete Kante zwischen i und j besitzt ein festes
symmetrisches nichtnegatives Geometriegewicht:

```text
w_ij = w_ji >= 0
```

Es werden keine neuen Kanten, Richtungs-IDs oder Partnerrollen eingefuehrt.

## 2. Feste Naturparameter

Die Minimalform besitzt drei globale inhaltsfreie Parameterrollen:

```text
lambda_sm >= 0     gemeinsame Staerke des Materialaustauschs
kappa              Richtungsempfindlichkeit gegenueber S-Differenz
eta >= 0           Staerke der gebundenen S-Rueckarbeit
```

Verbindlich gilt:

```text
abs(kappa) <= 1/2
```

Alle Parameter werden vor einem Arm festgelegt und bleiben raeumlich sowie
zeitlich konstant. `kappa` und `eta` duerfen nicht lokal gelernt oder nach
einem Ergebnis angepasst werden.

## 3. Gerichtete M-Austauschraten

Fuer jeden abgeschlossenen Vorzustand werden pro ungerichteter Kante zwei
nichtnegative gerichtete Raten gebildet:

```text
dS_ij = S_j - S_i

q_i_to_j = lambda_sm * w_ij * M_i * (1 + kappa * dS_ij)
q_j_to_i = lambda_sm * w_ij * M_j * (1 - kappa * dS_ij)
```

Der orientierte Nettofluss lautet:

```text
J_ij = q_i_to_j - q_j_to_i
J_ji = -J_ij
```

### Rolleninterpretation

- Der Faktor M_i ist die tatsaechlich vorhandene Quellmenge.
- Der konstante Anteil `1` ist die passive Diffusionsbaseline.
- Der Anteil `kappa * dS_ij` ist die kleinste lineare S-Richtungskomponente.
- `lambda_sm` schaltet die gesamte gekoppelte Materialphysik als
  Forschungsarm ein oder aus.

Die Form liest keine Rezeptoridentitaet, Bedeutung, Wiederholung oder Probe.

## 4. Beweis nichtnegativer Raten

Aus `S_i, S_j in [-1,1]` folgt:

```text
-2 <= dS_ij <= 2
```

Mit `abs(kappa) <= 1/2` gilt:

```text
1 + kappa * dS_ij >= 0
1 - kappa * dS_ij >= 0
```

Da auch `lambda_sm`, `w_ij` und M nichtnegativ sind, gilt:

```text
q_i_to_j >= 0
q_j_to_i >= 0
```

Die Transportform benoetigt weder Vorzeichenverzweigung noch Clipping.

## 5. Kontinuierliche M-Fortsetzung

Der lokale kontinuierliche M-Anteil lautet:

```text
C_i(S,M) = Summe ueber Nachbarn j von (q_j_to_i - q_i_to_j)
dM_i/dt  = C_i(S,M)
```

Alle Raten lesen denselben abgeschlossenen S-M-Vorzustand. Die Summe wird
unabhaengig von der Iterationsreihenfolge gebildet.

### Exakte Gesamtmengenerhaltung

Jede Kante traegt zu ihren beiden Endorten einmal `-J_ij` und einmal
`+J_ij` bei. Daher gilt:

```text
Summe_i C_i = 0
d/dt Summe_i M_i = 0
```

Die Erhaltung folgt aus der Kantenantisymmetrie, nicht aus nachtraeglicher
Normierung.

### Nichtnegativitaet

An der Grenze `M_i = 0` verschwinden alle Abgaberaten von i. Eingehende Raten
bleiben nichtnegativ. Daher gilt:

```text
M_i = 0 -> dM_i/dt >= 0
```

Der nichtnegative Orthant ist fuer die kontinuierliche Dynamik invariant.

### Endliche lokale Obergrenze

Aus Nichtnegativitaet und fester Gesamtmenge folgt fuer jeden Ort:

```text
0 <= M_i <= M_total(C)
```

Eine separate lokale Obergrenze und Zielkapazitaet sind fuer diese Minimalform
nicht notwendig.

## 6. Weltbedingter Fluss aus gleichfoermigem M

Sei innerhalb einer Komponente `M_i = M_j = m0`. Dann gilt an einer Kante:

```text
J_ij = 2 * lambda_sm * w_ij * m0 * kappa * dS_ij
```

Fuer aktive Kopplung, `kappa != 0` und eine reale S-Differenz ist der
M-Fluss nicht null. Der materielle Gleichzustand kann deshalb durch normale
S-Feldgeschichte umverteilt werden.

Bei `kappa > 0` ist die gewaehlte Grundrichtung Transport zu hoeherem S. Der
vorzeicheninvertierte `kappa`-Arm ist eine zwingende Gegenhypothese. Das
Vorzeichen darf nicht nach einem Musterbefund ausgewaehlt werden.

## 7. Gebundene additive S-Rueckarbeit

Die lokale S-Rueckarbeit wird ausschliesslich aus der tatsaechlichen
M-Mengenrate desselben Schritts gebildet:

```text
R_i(S,M) = -eta * (1 - S_i^2) * C_i(S,M) / M_total(C)
```

Die aktive kontinuierliche S-Fortsetzung lautet abstrakt:

```text
dS_i/dt = F_current_i(S, Weltkontakt) + R_i(S,M)
```

`F_current` bezeichnet die bestehende schnelle MCM-Naturform. Der Vertrag
veraendert sie noch nicht im Code.

### Unteilbarkeit

`R_i` liest weder M als ruhendes Pattern noch eine gespeicherte Vorlage. Ist
der tatsaechliche lokale M-Austausch null, gilt:

```text
C_i = 0 -> R_i = 0
```

Die Rueckarbeit existiert nur waehrend realisierter M-Umverteilung. Ein
identischer spaeterer S-Verlauf kann bei unterschiedlicher M-Verteilung
unterschiedliche C- und damit R-Verlaeufe erzeugen.

### Additive Rolle

R wird als eigener interner Term zur S-Fortsetzung addiert. Er multipliziert
weder Rezeptorkontakt noch den bestehenden S-Nachbarschaftsfluss und
veraendert keine Kante oder Zeitkonstante.

## 8. Invarianz des S-Bereichs

An den S-Grenzen gilt fuer die neue Rueckarbeit:

```text
S_i = -1 oder S_i = 1
-> 1 - S_i^2 = 0
-> R_i = 0
```

Die neue Kopplung kann S daher an keiner Bereichsgrenze nach aussen treiben.
Wenn die bestehende schnelle Naturform `F_current` den Bereich `-1..1`
bereits invariant haelt, bleibt dieser Bereich auch unter Addition von R
invariant.

Der Faktor `1-S_i^2` ist eine technische Randhuelle. Er wird als
zustandsabhaengige Begrenzungsbaseline ausgewiesen und darf nicht als
Memoryfunktion interpretiert werden.

Nachtraegliches Clipping ist fuer die mathematische Kandidatenform nicht
zulaessig.

## 9. Atomare gemeinsame Dynamik

Die mathematische Kandidatenform ist das gekoppelte kontinuierliche System:

```text
dS/dt = F_current(S, Welt) + R(S,M)
dM/dt = C(S,M)
dH/dt = bestehende schnelle H-Nachfuehrung aus S
```

S, H und M werden als ein gemeinsamer Zustand fortgesetzt. Eine spaetere
numerische Integration darf nicht zuerst M vollstaendig schreiben und danach
R aus dem neuen M auslesen.

Die exakte kontinuierliche Flussabbildung besitzt die Semigruppeneigenschaft.
Eine numerische Implementierung muss Zeitverfeinerungskonvergenz nachweisen;
byteidentische Grob-/Feinpartitionierung wird fuer die nichtlineare Form nicht
ohne exakten Integrator behauptet.

## 10. K2-Arme

### P0: heutiger Nullparameterarm

```text
lambda_sm = 0
-> q = 0
-> C = 0
-> R = 0
```

Damit bleiben S und H exakt unter ihrer heutigen Naturform. M bleibt im
gleichfoermigen Referenzzustand kausal abgekoppelt.

### P1: aktiver frischer Referenzarm

```text
lambda_sm > 0
M anfangs gleichfoermig
kappa und eta vorab fest
```

P1 darf ab der ersten S-Inhomogenitaet von P0 abweichen. Diese Differenz ist
die aktive Grundantwort der Materialphysik, kein Geschichtsbefund.

### P2: aktive Geschichtsarme

P2 verwendet exakt dieselben Parameter wie P1. Nur die kontrollierte
Weltvorgeschichte und daraus entstandene M-Verteilung duerfen sich
unterscheiden.

## 11. Enge Ablationen und Baselines

Vor jeder positiven Interpretation sind mindestens erforderlich:

1. `lambda_sm = 0`: heutiger schneller Nullpfad;
2. `kappa = 0`: passive M-Diffusion mit gebundener Diffusionsrueckarbeit;
3. `eta = 0`: einseitige drift-diffusive M-Bildung ohne S-Rueckarbeit;
4. Vorzeicheninversion von kappa;
5. konstante lineare Cross-Diffusion mit gleichem Zustandsbudget;
6. dieselbe M-Drift mit separatem Pattern-Leser;
7. Randhuelle durch eine gleich sichere alternative technische Huelle;
8. M-Tausch, mengenbilanzierte Neutralisierung und geometrische Permutation.

Die Kandidatenform ist selbst eine enge konservative Drift-Diffusionsphysik.
Ein spaeterer Befund darf nicht behaupten, ausserhalb dieser Mathematik zu
liegen.

## 12. Reichweite des Existenznachweises

Statisch nachgewiesen sind:

- lokale nichtnegative gerichtete Raten;
- exakte M-Gesamtmengenerhaltung;
- Invarianz von M-Nichtnegativitaet;
- endliche lokale M-Begrenzung durch M_total;
- weltbedingte Umverteilung aus gleichfoermigem M;
- an denselben Austausch gebundene additive S-Rueckarbeit;
- Erhaltung des S-Bereichs unter der bestehenden invarianten S-Naturform;
- exakter K2-Nullparameterfall.

Nicht nachgewiesen sind:

- numerische Eignung in der heutigen Runtime;
- robuste nichtseparierbare Feldwirkung;
- Praegung, Loesung oder Wiederpraegung;
- relative Feldzeitverdichtung;
- Memory, Organisation, Semantik oder KI.

## Forschungsentscheidung

```text
mathematische Minimalform existent:  ja
Projektgrenzen statisch vereinbar:   ja, unter K2 und genannten Baselines
konkrete Parameterwerte:             nicht gewaehlt
Schema- oder Runtimeaenderung:        noch nicht freigegeben
Versuch:                              noch nicht freigegeben
```

Die Form darf als naechstes in eine statische Implementierungsspezifikation
ueberfuehrt werden. Diese Spezifikation muss zuerst zeigen, wie M in Zustand,
Snapshot und atomare Feldfortsetzung integriert wuerde, ohne bereits Code zu
aendern.

## Quellen

- E. F. Keller und L. A. Segel,
  [Initiation of slime mold aggregation viewed as an instability](https://doi.org/10.1016/0022-5193(70)90092-5),
  1970. Dient als Drift- und Aggregationsbaseline.
- L. Onsager,
  [Reciprocal Relations in Irreversible Processes II](https://doi.org/10.1103/PhysRev.38.2265),
  1931. Dient nur als physikalischer Existenzhinweis fuer gekoppelte
  Kraft-Fluss-Rollen; die konkrete Form dieses Vertrags ist eine
  Projektkonstruktion.

## Bester naechster Schritt

Als naechstes wird eine **statische Implementierungsspezifikation fuer den
K2-F3-Kandidaten** erstellt. Sie muss ohne Datei- oder Runtimeaenderung
festlegen:

1. M-Zustandsfeld, Initialisierung, Validierung und Snapshotversion;
2. kanonische einmalige Kanteninventarisierung;
3. globale atomare Bildung von C und R aus demselben Vorzustand;
4. kontinuierliche Integrationsgrenze und numerische Invarianten;
5. exakte P0-, P1- und Ablationsarme;
6. kleinste spaetere Codeaenderungsflaeche und Rueckfallplan.

Erst danach kann separat entschieden werden, ob eine Implementierung fuer
einen reinen technischen Invariantentest freigegeben wird.
