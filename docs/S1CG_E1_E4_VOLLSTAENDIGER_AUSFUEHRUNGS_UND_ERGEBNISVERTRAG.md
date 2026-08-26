# S1-CG: E1 E4 vollstaendiger Ausfuehrungs- und Ergebnisvertrag

## Status

Statische Vorregistrierung des vollstaendigen E4-Korridors. Dieser Schritt
fuehrt keinen E4-Lauf aus, erzeugt keine Baselineentscheidung und veraendert
keine bestehende Gleichung. Er bindet die in S1-CE geforderte Vergleichsmatrix
an die in S1-CF implementierten privaten Handoffs.

Kein Ergebnis dieses Vertrags ist ein Nachweis fuer MCM-Memory, Lernen,
Organisation, Semantik, Selbstregulation oder KI.

## Forschungsfrage

Kann mindestens eine bereits registrierte, engere technische Baseline den
gesamten beobachtbaren E1-Verlauf aus Geschichte, Freigabe, Konkurrenz und
identischer eingefrorener Probe innerhalb der vorab gebundenen Profilgrenze
erklaeren?

Verglichen werden keine internen E1-, L- oder M-Zustaende. Vergleichsgegenstand
ist ausschliesslich das signierte 72-Komponenten-S/H-Wirkungsprofil.

## Unveraenderliches Modellinventar

Die spaetere Ausfuehrung verwendet genau diese Reihenfolge:

```text
E1  unveraenderter E1-Referenzkandidat
B0  P0 ohne langsame Zustandsrueckwirkung
B1  ein statischer E1-H8-Gain fuer den gesamten Verlauf
B2  S2 B2; B1 ist seine Rueckwirkungsablation
B3  F3 local-leaky mit festem direktem Reader
B4  F3 linear-coupled-field
B5  F3 candidate
B6  W7-N CONST-V auf derselben Drei-Knoten-Geometrie
ORACLE-G  checkpointweise exakt passender eingefrorener E1-Gain
```

ORACLE-G ist nur eine technische Obergrenze. Er darf keine E4-
Erklaerungsentscheidung ausloesen.

## Feste Parameter

```text
S response_time_seconds = 1.0
H time_constant_seconds = 0.5
S/H dissipation         = 0.0

B3, B4, B5:
lambda_sm_per_second    = 1.0
kappa                   = 0.5
eta                     = 1.0
initial_total_mass      = 1.0

B6 CONST-V:
lambda_sm_per_second    = 0.5
kappa                   = 0.5
eta                     = 1.0
initial_total_mass      = 1.0
```

E1 und S2 verwenden unveraendert ihre bereits gebundenen Vertrage. Es gibt
keinen Parameterfit gegen S1-CD oder gegen das spaetere E4-Ergebnis.

## Gemeinsame Drei-Phasen-Welt

Jedes dynamische Modell startet aus seinem neutralen Zustand auf derselben
Drei-Knoten-Geometrie.

```text
Phase H:
8 linke Kontakte mit (1.0, 0.0, 0.0), jeweils 1.0 s
Checkpoint H8 nach dem achten Kontakt

Phase G:
Nullkontakt ab einer Kopie von H8
Checkpoints G1, G4 und G8 nach insgesamt 1.0, 4.0 und 8.0 s

Phase C:
zweite tiefe Kopie des Zustands G4
8 rechte Kontakte mit (0.0, 0.0, 1.0), jeweils 1.0 s
Checkpoints C1 bis C8
```

In H und G bleiben Zustandsentwicklung und die modellspezifische
Rueckwirkung aktiv. In C bleibt die langsame Zustandsentwicklung aktiv,
waehrend ihre Rueckwirkung auf S/H ausgeschaltet ist. Die Interventionslogik
muss fuer jedes Modell explizit sein; ein nicht trennbares Modell macht die
Baseline-Matrix technisch inkompatibel.

## Gebundene Rueckwirkungsinterventionen

```text
E1 Phase C:
Kantenentwicklung aktiv, E1-zu-S-Rueckwirkung aus

S2 Phase C:
vorhandener B1-Pfad statt B2; L-Entwicklung aktiv, L-zu-S-Rueckwirkung aus

F3 B3/B4/B5 Phase C:
urspruengliche mass_rate unveraendert, activation_backreaction = 0

CONST-V Phase C:
urspruengliche mass_rate unveraendert, activation_backreaction = 0
```

Bei F3 und CONST-V wird der Kopplungsrechner zuerst unveraendert auf dem
aktuellen S/M-Zustand ausgewertet. Nur die ausgegebene Rueckwirkung wird fuer
Phase C auf null gesetzt. Dadurch wird weder die M-Dynamik neu definiert noch
eine neue Gleichung eingefuehrt.

## Identische eingefrorene Probe

An jedem Checkpoint `H8, G1, G4, G8, C1 ... C8` wird nur der langsame Zustand
auf eine frische Kopie desselben Probefeldes uebertragen. Er entwickelt sich
waehrend der Probe nicht weiter.

```text
F* Anfang: S/H uniform und wertidentisch fuer alle Modelle
Q: (0.30, -0.20, 0.60), t = 0 ... 20 Ticks
P: (0.75, -0.25, 0.25), t = 20 ... 40 Ticks
Abtastrate: 20 Hz
```

Die gefrorenen Reader sind:

```text
E1       fester Kantenratenreader
S2       fester L-Reader aus S1-CF
F3/B6    mass_rate = 0; Rueckwirkung aus festem M und aktuellem S
B1       derselbe H8-Gain an jedem Checkpoint
B0       P0
ORACLE-G checkpointweise passender E1-Gain
```

Die Probeablation setzt langsame Zustandsrate und Rueckwirkung auf null und
muss dadurch P0 bis zur absoluten Toleranz reproduzieren. ORACLE-G muss E1
an jedem Checkpoint bis zur absoluten Toleranz reproduzieren.

## Profil und Numerik

Jeder Probecheckpoint liefert:

```text
Delta_S = S_active - S_P0
Delta_H = H_active - H_P0
```

Die Reihenfolge ist unveraendert `12 Checkpoints * 3 Knoten * S,H = 72`
signierte Komponenten. Die primaere Ausfuehrung verwendet `n=4`, die
Numerikkontrolle `n=2`.

```text
absolute_control_tolerance       = 1e-12
relative_control_tolerance       = 0
relative_refinement_linf_limit   = 0.01
relative_profile_linf_limit      = 0.05
```

Die grobe und feine Ausfuehrung muessen denselben Zeitplan und dieselben
Checkpointidentitaeten besitzen. Der relative Refinementrest wird gegen die
jeweilige messbare Profilskala gebildet; eine nicht messbare erforderliche
Skala ist ungueltig und wird nicht durch Division kaschiert.

## S1-CD-Kontinuitaetsanker

Vor dem Baselinevergleich muss E1 an `H8`, `G4` und `C8` die bereits einmalig
erzeugten S1-CD-Anker innerhalb der absoluten Toleranz reproduzieren. S1-CD
wird dabei nicht erneut ausgefuehrt; seine gebundenen Referenzwerte werden
nur gelesen:

```text
release_hold_s_linf          = 0.003720672275362047
release_hold_h_linf          = 0.002329590741211862
compete_release_s_linf       = 0.0029908008917126083
compete_release_h_linf       = 0.0025335555912394947
hold_p0_s_linf               = 0.005960779905044511
hold_p0_h_linf               = 0.0037253303212222977
release_p0_s_linf            = 0.002240107629682464
release_p0_h_linf            = 0.0013957395800104355
compete_p0_s_linf            = 0.0026902423795267943
compete_p0_h_linf            = 0.00238212405542311
release_analytic_linf        = 1.734723475976807e-18
resource_budget_linf         = 4.440892098500626e-16
release_total_binding_drop   = 0.10364242805542052
compete_total_binding_rebound = 0.11840875933358301
maximum_refinement_linf      = 1.2490009027033011e-15
```

## Modellinvarianten

Jeder Modelllauf muss endliche S/H-Werte, unveraenderte Geometrie,
Checkpointvollstaendigkeit und deterministische Profilbildung bestaetigen.
Zusaetzlich gelten die vorhandenen modellspezifischen Vertrage:

```text
E1       Ressourcenbilanz, Bereichsgrenzen und Kanteninventar
S2       festes Modell, endliche L-Werte und identische B2/B1-Zuordnung
F3/B6    Massenbilanz, Nichtnegativitaet und unveraendertes Knoteninventar
B0/B1    keine verdeckte langsame Zustandsentwicklung
ORACLE-G exakte lokale Kontrollreproduktion, keine Entscheidungsrolle
```

## Ergebniscontainer

S1-CH implementiert genau drei private, unveraenderliche Rollen:

```text
E1E4ModelRun
  Modellkennung, Parameterdigest, Checkpoints, Profil, Kontrollmetriken,
  Invarianten und Refinementrest

E1E4BaselineMeasurement
  Profilabstand zu E1, Release- und Konkurrenzrest, Gueltigkeitsflags

E1E4RunResult
  Vertragsdigest, geordnete Modelllaeufe, geordnete Baselinevergleiche,
  Kontinuitaetsanker und Rohmetriken
```

Der Ergebniscontainer enthaelt keine eingebettete wissenschaftliche
Interpretation. Die Entscheidung wird erst nach vollstaendiger technischer
Validierung aus den vorregistrierten Regeln abgeleitet.

## Ausfuehrungs- und Abbruchreihenfolge

```text
1. Vertrags-, Geometrie- und Parameter-Preflight
2. gemeinsame H/G/C-Welten erzeugen
3. Interventions- und Frozen-Probe-Wrapper pruefen
4. E1 samt S1-CD-Kontinuitaetsankern erzeugen
5. B0 bis B6 in fester Reihenfolge erzeugen
6. ORACLE-G-Kontrollen erzeugen
7. n=2/n=4-, Ablations-, Reader- und Invariantenkontrollen pruefen
8. Profilresiduen berechnen
9. interpretationsfreien E1E4RunResult materialisieren
10. externe Entscheidung nach der gebundenen Reihenfolge ableiten
```

Bei einem Fehler wird der Lauf beendet; fehlende Modelle werden nicht
uebersprungen und ein Teilergebnis wird nicht als vollstaendige E4-Matrix
ausgegeben.

## Entscheidungsreihenfolge

Die in S1-CE vorregistrierte Reihenfolge bleibt unveraendert:

```text
INVALID_E4_RUN
TECHNICALLY_INCOMPATIBLE_BASELINE_SET
E4_EXPLAINED_BY_NARROW_BASELINE
E4_RESIDUAL_AFTER_REGISTERED_BASELINES
```

`E4_EXPLAINED_BY_NARROW_BASELINE` gilt, sobald mindestens eine gueltige
Baseline B1 bis B6 das vollstaendige Profil mit
`relative_profile_linf_residual <= 0.05` erklaert.

`E4_RESIDUAL_AFTER_REGISTERED_BASELINES` ist nur zulaessig, wenn alle
registrierten Baselines technisch kompatibel und gueltig sind, aber keine
die Profilgrenze erreicht. Auch dieser Ausgang waere kein Memorynachweis.

## Einmallaufgrenze

S1-CG gibt keinen Lauf frei. S1-CH darf zuerst ausschliesslich Wrapper,
Komposition, Ergebniscontainer und synthetische Preflighttests implementieren.
Erst wenn diese Abnahme vollstaendig besteht, darf der gebundene E4-Korridor
in einem getrennten Schritt genau einmal ausgefuehrt werden. Die S1-BZ- und
S1-CD-Einmallaufe duerfen dabei nicht wiederholt werden.

## Anschluss

S1-CH implementiert die privaten F3-Interventions- und Frozen-Probe-Wrapper,
den geordneten E4-Executorkern und die drei Ergebnisrollen. Die synthetische
Abnahme besteht; ein E4-Einmallauf wurde nicht ausgefuehrt.

## Bester naechster Schritt

S1-CI bindet B3 bis B6 einzeln an Weltfolge und Probe und nimmt sie isoliert
ab. S1-CJ schliesst als naechstes E1, B0 und B1 an. Erst eine vollstaendige
Matrixbereitschaft kann einen spaeteren getrennten E4-Einmallauf oeffnen.
