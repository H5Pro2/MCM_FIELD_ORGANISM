# S1-UF: ACM-1H statischer Parameter-, Runtimeabbildungs-, Orakel- und Implementierungszulassungsvertrag

## Auftrag und Grenze

S1-UF prueft, ob die symbolische ACM-1H-Minimalform aus S1-UE ohne neuen
Normalisierungszustand auf den vorhandenen Feldkern abgebildet werden kann.
Der Vertrag bindet einen kleinen Parameterkandidatenraum, reine
Referenzorakel, Fehlercodes, Ergebnisrollen und die kleinste spaetere
Implementierungsoberflaeche.

S1-UF veraendert keine Runtime, implementiert keinen Operator, fuehrt keinen
Test und keinen Feldlauf aus. Eine Implementierung bleibt durch die
ausdrueckliche ACM-1-Arbeitsgrenze gesperrt, bis sie gesondert freigegeben
wird.

## Gepruefte produktive Grundlagen

Die statische Runtimepruefung ergibt:

- `MCMFieldStepTime` bindet `clock_id`, geordnete Ticks und eine endliche
  positive `ticks_per_second`-Rate;
- `elapsed_seconds` ist die eindeutige Dauer eines atomaren Feldintervalls;
- `SharedMCMField.advance` verlangt bei expliziter Zeit dieselbe
  Feldzeitgrenze wie die verteilte Rezeptorzeit;
- `mcm_substrate_edge_inventory` leitet aus der symmetrischen lokalen
  Nachbarschaft jede vorhandene Kante kanonisch genau einmal ab;
- der neutrale Feldkern verwendet auf jeder internen Kante die symmetrische
  Rate `1 / response_time_seconds`;
- `build_e1_weighted_diffusion_generator` zeigt bereits, dass ein
  vollstaendiges Inventar nichtnegativer symmetrischer Kantenraten in einen
  quellenfreien Graphgenerator uebersetzt werden kann.

Die benoetigten Rollen sind damit vorhanden. Der neutrale Feldkern speichert
jedoch keinen eigenen Flussledger und `SharedMCMField` besitzt keinen
ACM-1H-Zustand. Eine spaetere erste Implementierung muss deshalb als
isolierter reiner Referenzkern beginnen und darf nicht direkt das produktive
Feldschema erweitern.

## Eindeutige Feldzeitabbildung

Verbindlich gilt:

```text
Delta_tau = step_time.elapsed_seconds
```

Zulaessig ist nur ein `MCMFieldStepTime`, dessen `clock_id`, `start_tick` und
`end_tick` exakt mit dem verteilten Feldintervall uebereinstimmen. Es wird
weder Wandzeit noch Prozesslaufzeit verwendet. Ein fehlendes `step_time`,
ein Uhrenwechsel oder eine abweichende Intervallgrenze sperrt ACM-1H.

Damit verwendet ACM-1H dieselbe aus der Feldlage uebergebene technische
Zeitordnung wie der primaere Feldschritt. Es entsteht keine zweite Uhr und
kein gespeicherter Zeitstempel im Motivzustand.

## Eindeutige Primaerflussabbildung

Fuer jede kanonische Kante

```text
e = (first_neuron_id, second_neuron_id)
first_neuron_id < second_neuron_id
```

seien `S_first` und `S_second` die Aktivierungen aus demselben `TX_PRE`. Die
primaere symmetrische Kantenrate sei `k_e >= 0` in Sekunden hoch minus eins.
Dann lautet der fuer ACM-1H orientierte Primaerfluss:

```text
Phi_e = k_e * (S_first - S_second)
```

`Phi_e > 0` bezeichnet Fluss von `first` nach `second`. Der vorhandene
Graphgenerator bucht denselben Beitrag als `-Phi_e` am ersten und
`+Phi_e` am zweiten Knoten. Damit ist die Flussrolle algebraisch identisch
mit dem bestehenden symmetrischen Diffusionsgenerator.

Im neutralen Feldkern gilt:

```text
k_e = 1 / response_time_seconds
```

In einem spaeteren bereits gewichteten opt-in Pfad darf `k_e` aus einem
vollstaendig validierten nichtnegativen Kantenratenledger stammen. ACM-1H
liest stets die primaere Rate vor seiner eigenen Modifikation. Ein bereits
ACM-modifizierter Fluss ist als Ursache unzulaessig.

## Einheitenabschluss

Die Aktivierung `S` ist im vorhandenen Feldkern dimensionslos und auf
`[-1,1]` begrenzt. Daher besitzt:

```text
k_e                         Einheit 1 / Sekunde
Phi_e                       Einheit 1 / Sekunde
abs(Phi_e) * Delta_tau      dimensionslose uebertragene Feldmenge
gamma_z, gamma_g            dimensionsloser Kehrwert dieser Feldmenge
beta                        dimensionslos
```

Damit sind die Exponenten aus S1-UE dimensionslos. Es wird keine
Normierungsmasse, gleitende Statistik oder neue Skala aus beobachteten Daten
benoetigt.

## Erste zulaessige Geometrie

Der erste Implementierungskorridor ist ausschliesslich die vorhandene offene
Vier-Knoten-Linie:

```text
node-a -- node-b -- node-c -- node-d
```

Kanten:

```text
e_ab = (node-a, node-b)
e_bc = (node-b, node-c)
e_cd = (node-c, node-d)
```

Motive:

```text
M_left  = (e_ab, e_bc)
M_right = (e_bc, e_cd)
```

Die Linie besitzt genau die in S1-UE behandelte Ueberlappung. Allgemeine
Graphen, periodische Geometrien, Verzweigungen und mehr als zwei Motive pro
Kante bleiben fuer die erste Implementierung gesperrt. Diese Begrenzung ist
ein Engineeringkorridor und keine Aussage ueber den allgemeinen Feldkern.

## Endlicher Parameterkandidatenraum

Fuer eine spaetere synthetische technische Abnahme werden genau sechs aktive
ACM-1H-Konfigurationen vorregistriert:

```text
gamma_z in {0.25, 0.5, 1.0}
beta    in {0.25, 0.5}
```

Das kartesische Produkt wird vollstaendig verwendet. Es gibt keine Suche,
Optimierung, armweise Auswahl oder nachtraegliche Erweiterung anhand eines
Ergebnisses.

Fuer IAG-2 gilt in jedem matched Fall:

```text
gamma_g = gamma_z
beta_g  = beta
```

Der IAG-2-Readout ist fuer den spaeteren Referenzvergleich eng gebunden als:

```text
r_e_IAG = 1 + beta_g * g_e
Phi_e_IAG = r_e_IAG * Phi_e_primary
```

Er bleibt pro Kante unabhaengig und vorzeichenblind. Diese Gleichsetzung ist
ein gemeinsames Parameterbudget, keine Behauptung gleicher Modellfunktion.

Zusaetzliche feste Ablationen sind:

```text
ACM-OFF       kein ACM-Zustand und unveraenderter primaerer Feldkern
ACM-Z-NULL    z = 0 bei aktivem reinen Readoutorakel
ACM-R-OFF     beta = 0 nur als Readoutablation
ACM-W-OFF     keine Zustandsfortschreibung, aber gebundener z-Vorzustand
```

`beta = 0` und eine gesperrte Zustandsfortschreibung sind keine aktiven
Parameterkandidaten.

## Reine Referenzorakel

Eine spaetere Implementierung muss vor jeder Runtimeintegration gegen sieben
voneinander getrennte reine Orakel pruefbar sein.

### O1: Kanteninventarorakel

Aus der Layergeometrie entstehen exakt `e_ab`, `e_bc`, `e_cd` in
kanonischer Reihenfolge und ein dazugehoeriger Inventardigest. Fehlende,
doppelte oder gerichtete Zusatzkanten sind ungueltig.

### O2: Primaerflussorakel

Aus `S_first`, `S_second` und `k_e` entsteht exakt:

```text
k_e * (S_first - S_second)
```

Kantenumkehr kehrt nur das Flussvorzeichen um. Nullgradient ergibt exakt
null.

### O3: Motivzustandsorakel

Aus `Phi_1`, `Phi_2`, `Delta_tau`, `gamma_z` und `z_pre` entstehen nur
`u_M`, `sigma_M`, `theta_M` und `z_next` nach S1-UE. Wertebereich und
Halteidentitaet muessen algebraisch ohne Clipping gelten.

### O4: Motivreadoutorakel

Aus `sigma_M`, `z_pre` und `beta` entsteht genau ein Faktor `r_M`. Beide
Motivkanten erhalten denselben Faktor. `z_next` ist kein Leser.

### O5: Ueberlappungsorakel

Die aeusseren Kanten erhalten je einen Motivfaktor. Auf `e_bc` gilt exakt:

```text
R_bc = r_M_left * r_M_right
```

Der Primaerfluss wird danach einmal multipliziert. Vertauschte
Motiviterationsreihenfolge muss bitgleich denselben kanonischen Payload
erzeugen.

### O6: Generatororakel

Jede komponierte Rate lautet:

```text
k_e_ACM = R_e * k_e
```

Alle Raten muessen endlich und nichtnegativ sein. Der daraus gebildete
symmetrische Graphgenerator muss Zeilensumme null besitzen. ACM-OFF muss den
vorhandenen neutralen Generator wertidentisch reproduzieren.

### O7: G/O- und IAG-2-Orakel

Die in S1-UE gebundenen G/O-Geschichten muessen fuer jeden der sechs
Parametersaetze:

- entgegengesetzte ACM-1H-Endzustaende gleichen Betrags erzeugen;
- wertidentische vollstaendige IAG-2-Kantenzustaende erzeugen;
- unter derselben positiven Probe unterschiedliche ACM-Faktoren und
  identische IAG-2-Faktoren liefern.

Dieses Orakel prueft eine vorregistrierte technische Gegenprognose und noch
keinen Feldnutzen.

## Minimale spaetere Recordoberflaeche

Ein isolierter Referenzkern darf genau folgende unveraenderliche Records
besitzen:

1. `ACM1HConfigRecord`: Schema-ID, `gamma_z`, `beta` und Konfigurationsdigest.
2. `ACM1HPrestateRecord`: Feld-, Geometrie-, Kanteninventar-, Zeit- und
   Zustandsdigest sowie die vier S- und zwei z-Werte.
3. `ACM1HEdgeFluxRecord`: drei primaere Kantenraten und signed Fluesse.
4. `ACM1HMotifProposalRecord`: Motivrolle, `u`, `sigma`, `theta`, `z_pre`,
   `z_next`, `r_M` und gemeinsamer Vorzustandsdigest.
5. `ACM1HCompositionRecord`: drei komponierte Faktoren und Raten,
   einschliesslich der beiden provenancegetrennten Faktoren auf `e_bc`.
6. `ACM1HDecisionRecord`: vollstaendiger Erfolgspayload oder genau ein
   Fehlercode ohne Teilresultat.

Die Records enthalten keine Rezeptorrohdaten, Labels, Zielwerte,
Comparatorentscheidung, Sequenzpuffer oder Feldlaufergebnisse. Sie werden
im ersten Korridor nicht in `SharedMCMFieldSnapshot` aufgenommen.

## Fail-closed-Fehlercodes

Genau folgende erste Fehlerfamilie wird gebunden:

```text
ACM1H_INVALID_CONFIG
ACM1H_INVALID_FIELD_PRESTATE
ACM1H_INVALID_STEP_TIME
ACM1H_STEP_TIME_MISMATCH
ACM1H_UNSUPPORTED_GEOMETRY
ACM1H_EDGE_INVENTORY_MISMATCH
ACM1H_INVALID_Z_STATE
ACM1H_NONFINITE_PROPOSAL
ACM1H_NEGATIVE_EDGE_RATE
ACM1H_SHARED_EDGE_COMPOSITION_MISMATCH
ACM1H_ITERATION_ORDER_DEPENDENCE
ACM1H_ATOMIC_RESULT_REQUIRED
```

Ein Fehlercode beendet den gesamten reinen Aufruf. Es gibt keine Reparatur,
kein Clipping, keine Nachnormalisierung, keinen Teilpayload und keinen
Fallback auf einen anderen Parametersatz.

## Spaetere minimale synthetische Testmatrix

Nach gesonderter Implementierungsfreigabe muss die reine technische Abnahme
mindestens folgende Klassen enthalten:

- sechs aktive Parameterkonfigurationen und vier feste Ablationen;
- beide Paritaeten, `z` an beiden Grenzen, `z = 0` und innere z-Werte;
- Nullgradient, Einzelkante, Zwei-Kanten-Motiv und beide aktive Motive;
- `e_bc` mit zwei verstaerkenden, zwei abschwaechenden und gemischten
  Faktoren;
- Halten bei fehlender gemeinsamer Beteiligung und Gegenwirkung bei
  umgekehrter Paritaet;
- gemeinsamer Vorzeichenwechsel, Spiegelung und Motiviterationsumkehr;
- G/O-Match gegen IAG-2;
- jede gebundene Fail-Closed-Klasse;
- ACM-OFF gegen den vorhandenen neutralen Generator.

Diese Liste ist eine spaetere Testpflicht. In S1-UF wird keine Testdatei
angelegt und kein Test ausgefuehrt.

## Implementierungszulassung und verbleibende Sperren

Die Runtimeabbildung ist eindeutig und benoetigt keinen neuen
Normalisierungszustand. Damit ist nach gesonderter Freigabe genau eine erste
Implementierung technisch zulaessig:

```text
isolierter privater reiner ACM-1H-Referenzkern
+ synthetische Vertragstests
+ keine SharedMCMField-Integration
+ kein Snapshotumbau
+ kein Feldlauf
```

Weiterhin gesperrt bleiben:

- Aenderungen an `SharedMCMField.advance` oder `MCMNeuronLayer.advance`;
- ein produktiver ACM-1H-Zustand im Feldsnapshot;
- Browser-, Audio-, Video- oder reale Rezeptorpfade;
- Parameteroptimierung oder Ergebniswahl;
- Forschungs- oder Funktionsentscheidung aus synthetischen Tests;
- Wiedereroeffnung von RFM-1;
- Aussagen ueber vorhandene Memory-, Lern- oder KI-Faehigkeiten.

## Vertragsentscheidung

Die S1-UE-Gleichung kann auf die vorhandene technische Feldzeit, das
kanonische Kanteninventar und den symmetrischen Diffusionsgenerator
abgebildet werden. Der Primaerfluss ist eindeutig aus `TX_PRE` ableitbar;
ein zusaetzlicher Flussspeicher oder Normalisierungszustand ist nicht
erforderlich.

Die statische Vorbereitung ist damit bis zur Grenze eines isolierten reinen
Referenzkerns abgeschlossen. Es wurde keine Implementierung oder Ausfuehrung
vorgenommen.

```text
S1_UF_ACM1H_RUNTIME_TIME_AND_PRIMARY_EDGE_FLOW_MAPPING_BOUND
SIX_FINITE_PARAMETER_CANDIDATES_AND_MATCHED_IAG2_BUDGET_BOUND
SEVEN_REFERENCE_ORACLES_AND_FAIL_CLOSED_SURFACE_BOUND
PURE_PRIVATE_REFERENCE_KERNEL_TECHNICALLY_ADMISSIBLE_AFTER_EXPLICIT_RELEASE
NO_IMPLEMENTATION_NO_TEST_NO_FIELD_RUN
```

## Erforderliche naechste Freigabe

Der naechste moegliche Abschnitt ist S1-UG: Implementierung ausschliesslich
des privaten reinen ACM-1H-Referenzkerns und seiner synthetischen
Vertragstests. Dieser Schritt ist noch nicht freigegeben, weil die
ausdrueckliche Richtungsentscheidung ACM-1 bisher ohne Implementierung und
Feldlaeufe untersuchen laesst.

Ein allgemeines `ok weiter` ueberschreitet diese Sperre nicht. Fuer S1-UG ist
eine konkrete fachliche Freigabe erforderlich, die den reinen Kern und
synthetische Tests erlaubt, aber Runtimeintegration, Snapshotumbau und
Feldlaeufe weiterhin ausschliesst.
