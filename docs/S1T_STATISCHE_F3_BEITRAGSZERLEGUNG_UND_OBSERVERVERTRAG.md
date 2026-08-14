# S1-T: Statische F3-Beitragszerlegung und Observervertrag

Stand: 2026-08-09

Vertragsstatus: `PREREGISTERED_NOT_IMPLEMENTED_NOT_EXECUTED`

Runtimeaenderung: nein

Forschungslauf: nein

## Ausgangspunkt

S1-S zeigt in drei von vier spaeten Vorproben-M-Fenstern einen gemischten
Normverlauf. Gleichzeitig bleiben alle nachweisbaren M- und Probevektoren
innerhalb der linearen gekoppelten Baseline.

S1-T verlaengert deshalb weder die Zeitachse noch sucht es eine neue
Substratphysik. Es zerlegt zuerst die bereits implementierte F3-Gleichung in
ihre transparenten direkten Beitraege und bindet einen passiven
Komponentenobserver vor jeder Implementierung.

## Verwendete Projektquellen

- [`mcm_f3_coupling.py`](../mcm_field_organism/mcm_f3_coupling.py): lokale
  Kantenfluesse, M-Raten und S-Rueckwirkung;
- [`mcm_f3_baseline_coupling.py`](../mcm_field_organism/mcm_f3_baseline_coupling.py):
  lineare gekoppelte F3-Baseline;
- [`mcm_f3_runtime.py`](../mcm_field_organism/mcm_f3_runtime.py): additive
  rechte Seite und SSPRK(3,3)-Integration;
- [`s1s_phase_separation_evaluator.py`](../mcm_field_organism/s1s_phase_separation_evaluator.py):
  feste S1-Q-Zellen, lokale Nachweisboeden und Fensterrollen.

## Tatsachliche F3-Kausalstruktur

Fuer einen Knoten `i` mit Nachbarn `j` gilt die implementierte M-Rate:

```text
dM_i/dt = D_i + A_i

D_i = lambda * sum_j (M_j - M_i)

A_i = -lambda * kappa
      * sum_j ((M_i + M_j) * (S_j - S_i))
```

`D_i` ist der massenausgleichende Beitrag. `A_i` ist der durch lokale
Aktivierungsgradienten gerichtete Beitrag. Beide sind kantenantisymmetrisch;
ihre Summen ueber alle Knoten sind null. Die M-Gesamtmasse bleibt daher
erhalten.

Die Rueckwirkung auf S lautet:

```text
R_i = -eta * (1 - S_i^2) * (dM_i/dt) / M_total
```

Waehrend eines Nullkontakts gilt ohne Dissipation und ohne aeussere
Randquelle:

```text
dS/dt = G*S + R(S,M)
dH/dt = (S-H) / tau_H
dM/dt = D(M) + A(S,M)
```

`G*S` ist die bestehende schnelle Feldkopplung. H folgt S, erscheint aber
weder in der S- noch in der M-Gleichung. H ist in diesem F3-Pfad deshalb
kein Traeger der spaeten M-Mischung.

Der Weltkontakt wird an abgeschlossenen Rezeptorereignissen als Punktkontakt
auf S angewendet. Nach Kontaktende kann die vorhandene S-Lage M weiterhin
ueber `A` verschieben; M wirkt zugleich ueber `R` auf die weitere S-Lage
zurueck. Dieser geschlossene S-M-Kreis ist bereits bekannte F3-Mechanik.

## Beziehung zur linearen Baseline

Die lineare gekoppelte Baseline ersetzt im aktivierungsgetriebenen Beitrag
die lokale Massensumme `M_i + M_j` durch `2*M_0` um die uniforme Referenz:

```text
A_linear_i = -2 * lambda * kappa * M_0
             * sum_j (S_j - S_i)
```

Der massenausgleichende Beitrag bleibt linear identisch. Der kleine
S1-S-Baselinerest zeigt daher, dass die zustandsabhaengige Massengewichtung
im geprueften Korridor nur einen kleinen Zusatz liefert.

## Wichtige Normgrenze

S1-S klassifiziert den Verlauf der skalaren Groesse:

```text
M_pre(d) = Linf(M_exposed(d) - M_zero(d))
```

Ein Anstieg oder Abfall dieser Norm sagt nicht automatisch, dass derselbe
Knoten oder dieselbe lokale Struktur steigt oder faellt. Der Knoten mit dem
groessten Absolutwert kann zwischen zwei Grenzen wechseln.

S1-T darf deshalb keine Ursache aus dem Normverlauf allein ableiten. Der
Observer muss vollstaendige vorzeichenbehaftete Knotenvektoren, ihre
Knotenidentitaeten und den jeweiligen `Linf`-Argmax ausgeben.

## Gebundener Observerumfang

Untersucht werden die vier bereits gebundenen Kurven:

```text
dose_count = 1, 8
source_form = repeated-supports, continuous-support
```

Die S1-Q-Grenzen bleiben unveraendert:

```text
0.000, 0.025, 0.050, 0.100, 0.200, 0.400, 0.800, 1.600 s
```

Die fruehen Grenzen 0.025, 0.050, 0.100 und 0.200 Sekunden besitzen in S1-R
je einen eigenstaendigen Nullsupportpfad. Sie sind deshalb keine
geschachtelten Teilstuecke derselben Trajektorie. Fuer diese Grenzen darf der
Observer nur den kumulativen Ledger ab Kontaktende ausgeben; Differenzen
zweier kumulativer Ledger duerfen nicht als Intervallursache interpretiert
werden.

Ab 0.200 Sekunden verwenden alle gebundenen Pfade dieselben aufeinander
folgenden 0.100-Sekunden-Supports. Nur folgende drei spaete Intervalle sind
damit kausal geschachtelt:

```text
0.200 -> 0.400 s
0.400 -> 0.800 s
0.800 -> 1.600 s
```

Fuer die vier fruehen kumulativen Grenzen und die drei spaeten geschachtelten
Intervalle bilanziert der Observer bei SSPRK-Verfeinerung 2 und 4:

- M-Vektor am Intervallanfang und -ende;
- direkten massenausgleichenden Beitragsvektor `Delta_D`;
- direkten aktivierungsgetriebenen Beitragsvektor `Delta_A`;
- Gesamtinkrement `Delta_M`;
- Bilanzrest `Delta_M - Delta_D - Delta_A`;
- Knotensummen jedes Beitrags;
- `Linf` und Argmax-Knoten vor und nach dem Intervall;
- Anzahl und Gewicht der SSPRK-Stufen.

Es werden keine Rohquellen, Bilder, Audiodaten oder neuen Feldzustaende
gespeichert.

## Exakte SSPRK-Beitragsrechnung

Fuer einen SSPRK(3,3)-Schritt der Laenge `h` mit den drei Raten `f1`, `f2`
und `f3` gilt exakt:

```text
Delta_y = h * (f1/6 + f2/6 + 2*f3/3)
```

Der Observer wendet dieselben Gewichte getrennt auf `D` und `A` an. Er darf
keine Euler-Approximation an den Intervallgrenzen und keine nachtraegliche
Differenzaufteilung verwenden.

Die Instrumentierung ist rein diagnostisch. Sie darf weder Stufenwerte noch
Schrittweite, Kopplungsrechner, Integrator oder Feldzustand veraendern.

## Gegenkontrollen

### Lineare gekoppelte Baseline

Die lineare Baseline erhaelt dieselbe Komponentenrechnung. Sie prueft, ob
die beobachtete Beitragsordnung bereits durch die Linearisierung getragen
wird.

### `kappa=0`

Dieser technische Ablationsarm entfernt nur `A`; `D` und die M-Erhaltung
bleiben bestehen. Er prueft, ob massenausgleichender Transport allein den
spaeten gemischten M-Normverlauf reproduziert.

### `eta=0`

Dieser Arm behaelt `D` und `A`, entfernt aber die M-Rueckwirkung `R` auf S.
Er prueft, ob der reziproke S-M-Kreis die spaete Beitragsfolge veraendert.

### Null- und Bilanzkontrollen

- P0 besitzt exakt `Delta_D = Delta_A = Delta_M = 0`;
- uniforme M-Lage bei S=0 besitzt exakt null direkte M-Rate;
- `sum(Delta_D)`, `sum(Delta_A)` und `sum(Delta_M)` bleiben je Intervall
  innerhalb `1e-12` bei null;
- Observer ein/aus erzeugt bitgleiche Endzustaende und Digests;
- Wiederholung einer langen Randkurve erzeugt bitgleiche Ledgervektoren.

## Numerische Boeden

Fuer jeden Beitragsvektor wird vor Klassifikation gebildet:

```text
convergence_floor = 8 * Linf(vector_r4 - vector_r2)
detection_floor = max(1e-12, convergence_floor)
ledger_closure_tolerance = max(1e-12, 8 * Linf(closure_r4 - closure_r2))
```

Paarvergleiche verwenden die groessere lokale Nachweisgrenze. Schwellen
werden nach der Ausfuehrung nicht veraendert.

## Vorregistrierte technische Entscheidungen

Zuerst muss die Ledgerbilanz fuer alle Intervalle gueltig sein, sonst lautet
das Gesamtergebnis `TECHNICALLY_INVALID`.

Die Rolle des direkten Antriebs lautet danach:

- `ACTIVATION_FORCING_REQUIRED_FOR_LATE_MIXTURE`: Der aktive F3-Pfad besitzt
  spaete gemischte/steigende M-Intervalle, der `kappa=0`-Arm jedoch nicht.
- `MASS_RELAXATION_ALONE_REPRODUCES_LATE_MIXTURE`: Mindestens ein spaetes
  gemischtes/steigendes Intervall bleibt bei `kappa=0` bestehen.
- `NO_LATE_MIXTURE_IN_COMPONENT_LEDGER`: Die vektorielle Intervallrechnung
  reproduziert keine spaete Mischung oberhalb ihrer Boeden.

Die Rueckwirkungsrolle wird getrennt ausgegeben:

- `RECIPROCAL_BACKREACTION_CHANGES_LATE_LEDGER`: Aktiver F3- und `eta=0`-Arm
  unterscheiden sich spaet oberhalb des Konvergenzbodens.
- `LATE_LEDGER_ETA_EQUIVALENT_WITHIN_FLOOR`: Sie bleiben innerhalb des
  Bodens gleich.

Die Mechanikrolle bleibt:

- `COMPONENT_LEDGER_LINEARLY_EXPLAINED`: Alle nachweisbaren direkten
  Beitragsvektoren bleiben innerhalb 5 Prozent der linearen Baseline.
- `COMPONENT_LEDGER_CONTAINS_BASELINE_DIFFERENT_INTERVAL`: Mindestens ein
  nachweisbarer Beitragsvektor ueberschreitet 5 Prozent.

Keine dieser Rollen ist ein Memory-, Lern-, Feldzeit- oder
Organisationsnachweis.

## Aussagegrenze

S1-T ist eine statische Gleichungs- und Observervorregistrierung. Es wurde
nichts implementiert oder ausgefuehrt. Der Vertrag fuehrt keine neue
Feldmechanik, keinen Speicher und keine regulatorische Funktion ein.

Browser, Kamera, Mikrofon, reale Sensorik, externe Runner, Reports und neue
Laufnummern bleiben gesperrt. Lauf 197 und die geschlossenen Zweige bleiben
unberuehrt.

## Bester naechster Schritt

S1-U implementiert nur den passiven stufengenauen Komponentenobserver und
seine technischen Bilanztests. Zunaechst werden eine einzelne aktive Zelle,
die P0-/Uniformnullen, Observertransparenz und 2/4-Konvergenz geprueft. Die
vier Kurven und die drei S1-T-Entscheidungsrollen bleiben in S1-U noch
unausgefuehrt.

## Spaeterer Umsetzungsstand S1-U

S1-U hat den passiven stufengenauen Komponentenobserver inzwischen fuer eine
gebundene Einzelzelle umgesetzt. Ledgerabschluss, Observertransparenz, P0,
uniforme aktive Null und lokale 2/4-Bodenbildung bestehen. Die Vierkurven-
und Ablationsentscheidungen bleiben unausgefuehrt.
